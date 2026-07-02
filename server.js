const express = require('express');
const nunjucks = require('nunjucks');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { db, initDB, query, get, run, transaction } = require('./db');
const multer = require('multer');
const xlsx = require('xlsx');
const rateLimit = require('express-rate-limit');
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 5 * 1024 * 1024, files: 1 }
});
const app = express();
const IS_PRODUCTION = process.env.NODE_ENV === 'production';
const COOKIE_SECURE = process.env.COOKIE_SECURE === '1';
const JWT_SECRET = process.env.JWT_SECRET || (IS_PRODUCTION ? null : 'development-only-change-me');

if (!JWT_SECRET || (IS_PRODUCTION && JWT_SECRET.length < 32)) {
    throw new Error('JWT_SECRET must contain at least 32 characters when NODE_ENV=production');
}

if (process.env.TRUST_PROXY === '1') app.set('trust proxy', 1);
app.disable('x-powered-by');

// Rate limiter — max 15 login attempts per 15 minutes per IP
const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 15,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Too many login attempts. Please try again in 15 minutes.' },
    skipSuccessfulRequests: true
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use('/static', express.static(path.join(__dirname, 'static')));

app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'same-origin');
    res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
    if (COOKIE_SECURE) {
        res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    }
    next();
});

// SameSite cookies block most CSRF; this additionally rejects cross-origin browser posts.
app.use((req, res, next) => {
    if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) return next();
    const origin = req.get('origin');
    if (!origin) return next();
    try {
        if (new URL(origin).host !== req.get('host')) return res.status(403).send('Cross-origin request rejected');
    } catch {
        return res.status(403).send('Invalid request origin');
    }
    next();
});

// Configure Nunjucks
app.set('views', path.join(__dirname, 'templates'));
const njEnv = nunjucks.configure(path.join(__dirname, 'templates'), {
    autoescape: true,
    express: app,
    watch: false,
    noCache: true
});

const renderError = (res, statusCode, title, message) => {
    res.status(statusCode).render('error.html', {
        statusCode,
        title,
        message
    });
};

// Custom Nunjucks filters
njEnv.addFilter('datestr', (val) => {
    if (!val) return '—';
    return String(val).substring(0, 10);
});
njEnv.addFilter('datetimefmt', (val) => {
    if (!val) return '—';
    if (val instanceof Date) {
        return val.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' }) + ', ' + val.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    }
    const s = String(val);
    const d = new Date(s + (s.endsWith('Z') || s.includes('+') ? '' : 'Z'));
    if (isNaN(d.getTime())) return s.substring(0, 10);
    return d.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' }) + ', ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
});
njEnv.addFilter('shortid', (val) => {
    if (!val) return '—';
    return String(val).replace(/-/g, '').substring(0, 8).toUpperCase();
});

const WARRANTY_DATE_EXPR = `COALESCE(a.warrantyExpiryDate, a.warranty_date)`;
const WARRANTY_ENABLED_EXPR = `(COALESCE(a.hasWarranty, 0) = 1 OR (LOWER(COALESCE(a.in_warranty_status, '')) = 'yes' AND ${WARRANTY_DATE_EXPR} IS NOT NULL))`;

function normalizeWarrantyFields({ hasWarranty, warrantyExpiryDate, warranty_date, in_warranty_status }) {
    const normalizedFlag = hasWarranty === '1'
        || hasWarranty === 1
        || String(in_warranty_status || '').trim().toLowerCase() === 'yes';
    const normalizedDate = normalizedFlag ? (warrantyExpiryDate || warranty_date || null) : null;

    return {
        hasWarrantyValue: normalizedFlag ? 1 : 0,
        warrantyExpiryValue: normalizedDate
    };
}

const ASSET_ARCHIVE_INSERT_SQL = `
    INSERT INTO asset_archive (id, original_asset_id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status, archived_by, reason,
    sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
    system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
    network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, hasWarranty, warrantyExpiryDate, source_type, source_user_id)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?)
`;

function buildAssetArchiveValues(asset, archivedBy, reason, archivedStatus = 'rejected') {
    return [
        uuidv4(), asset.id, asset.asset_tag, asset.brand, asset.model, asset.serial_number,
        asset.category, asset.purchase_date, asset.warranty_date, asset.purchase_cost,
        asset.department, asset.location, archivedStatus, archivedBy, reason,
        asset.sl_no, asset.monitor_make, asset.monitor_serial_no, asset.asset_owner_pl_no, asset.asset_usage_status, asset.in_warranty_status,
        asset.system_serial_no, asset.host_name, asset.group_name, asset.division, asset.user_name, asset.designation, asset.ip_address, asset.mac_address,
        asset.network_type, asset.drona_domain, asset.os_version, asset.antivirus_status, asset.usb_status, asset.admin_privilege,
        asset.hasWarranty || 0, asset.warrantyExpiryDate || null, asset.source_type || null, asset.source_user_id || null
    ];
}

async function getEmployeeAssets(employeeId) {
    const assets = await query(`
        SELECT a.id, a.asset_tag, a.brand, a.model, a.status, a.created_at as assigned_date,
               a.category, a.department, a.location, a.asset_usage_status, a.in_warranty_status,
               a.asset_owner_pl_no, a.monitor_make
        FROM assets a
        WHERE a.current_owner_id = ?
          AND a.status NOT IN ('pending', 'rejected')
        ORDER BY a.created_at DESC, a.asset_tag DESC
    `, [employeeId]);

    return assets.map(asset => ({
        ...asset,
        name: `${asset.brand} ${asset.model}`
    }));
}

async function getNavStats(user, employee) {
    if (user.role === 'employee') {
        const employeeId = employee && employee.id ? employee.id : 'none';
        return {
            total_assets: (await get(`SELECT count(*) as c FROM assets WHERE current_owner_id = ? AND status NOT IN ('pending', 'rejected')`, [employeeId])).c,
            assigned: (await get(`SELECT count(*) as c FROM assets WHERE current_owner_id = ? AND status='assigned'`, [employeeId])).c,
            available: 0,
            maintenance: (await get(`SELECT count(*) as c FROM assets WHERE current_owner_id = ? AND status='maintenance'`, [employeeId])).c,
            pending_requests: (await get(`SELECT count(*) as c FROM requests WHERE employee_id = ? AND status='pending'`, [employeeId])).c,
            warranty_expiring: (await get(
                `SELECT count(*) as c
                 FROM assets a
                 WHERE a.current_owner_id = ?
                   AND ${WARRANTY_ENABLED_EXPR}
                   AND a.status NOT IN ('pending', 'rejected')
                   AND CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) BETWEEN 0 AND 30`,
                [employeeId]
            )).c
        };
    }

    return {
        total_assets: (await get(`SELECT count(*) as c FROM assets WHERE status NOT IN ('pending', 'rejected')`)).c,
        assigned: (await get(`SELECT count(*) as c FROM assets WHERE status='assigned'`)).c,
        available: (await get(`SELECT count(*) as c FROM assets WHERE status='available'`)).c,
        maintenance: (await get(`SELECT count(*) as c FROM assets WHERE status='maintenance'`)).c,
        pending_requests: (await get(`SELECT count(*) as c FROM requests WHERE status='pending'`)).c,
        warranty_expiring: (await get(
            `SELECT count(*) as c
             FROM assets a
             WHERE ${WARRANTY_ENABLED_EXPR}
               AND a.status NOT IN ('pending', 'rejected')
               AND CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) BETWEEN 0 AND 30`
        )).c
    };
}

// ============================================================
// Auth Middleware
// ============================================================
const requireAuth = async (req, res, next) => {
    const token = req.cookies.token;
    if (!token) return res.redirect('/login');
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const user = await get(
            `SELECT u.*, e.name as emp_name, e.id as emp_id, e.department as emp_department
             FROM users u LEFT JOIN employees e ON u.id = e.user_id
             WHERE u.id = ?`,
            [decoded.id]
        );
        if (!user) throw new Error('User not found');
        req.user = user;
        req.employee = { id: user.emp_id, name: user.emp_name, department: user.emp_department };
        res.locals.user = {
            id: user.id,
            username: user.username,
            role: user.role,
            employee: req.employee
        };
        res.locals.navStats = await getNavStats(user, req.employee);
        next();
    } catch (e) {
        res.clearCookie('token');
        res.redirect('/login');
    }
};

const requireAdmin = (req, res, next) => {
    if (req.user && (req.user.role === 'admin' || req.user.role === 'super_admin')) {
        next();
    } else {
        res.status(403).send('Forbidden: Admin access required');
    }
};

const requireSuperAdmin = (req, res, next) => {
    if (req.user && req.user.role === 'super_admin') {
        next();
    } else {
        res.status(403).send('Forbidden: Super Admin access required');
    }
};

const requireRole = (roles) => {
    return (req, res, next) => {
        if (req.user && roles.includes(req.user.role)) {
            next();
        } else {
            res.status(403).send(`Forbidden: Required role: ${roles.join(' or ')}`);
        }
    };
};

// ============================================================
// Auth Routes
// ============================================================
app.get('/', (req, res) => res.redirect('/dashboard'));

app.get('/login', (req, res) => {
    res.render('index.html', { error: req.query.error });
});

app.post('/login', loginLimiter, async (req, res) => {
    const username = String(req.body.username || '').trim();
    const password = String(req.body.password || '');
    try {
        const user = await get(`SELECT * FROM users WHERE username = ?`, [username]);
        const passwordMatches = user && (
            String(user.password || '').startsWith('$2')
                ? await bcrypt.compare(password, user.password)
                : password === user.password
        );
        if (!passwordMatches) return res.status(401).render('index.html', { error: 'Invalid username or password' });

        // Upgrade legacy plaintext passwords created by older versions.
        if (!String(user.password || '').startsWith('$2')) {
            await run(`UPDATE users SET password = ? WHERE id = ?`, [await bcrypt.hash(password, 12), user.id]);
        }
        const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, { expiresIn: '24h' });
        res.cookie('token', token, {
            httpOnly: true,
            sameSite: 'strict',
            secure: COOKIE_SECURE,
            maxAge: 24 * 60 * 60 * 1000
        });
        res.redirect('/dashboard');
    } catch (err) {
        res.render('index.html', { error: 'System error' });
    }
});

app.get('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/login');
});

// ============================================================
// Health Check
// ============================================================
app.get('/api/health', async (req, res) => {
    try {
        const { count: assets } = await get(`SELECT count(*) as count FROM assets`);
        const { count: employees } = await get(`SELECT count(*) as count FROM employees`);
        res.json({ status: 'ok', database: 'connected', assets, employees, uptime: process.uptime() });
    } catch (e) {
        res.status(500).json({ status: 'error', database: 'disconnected' });
    }
});

// ============================================================
// Dashboard
// ============================================================
app.get('/dashboard', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') {
        const emp_id = req.employee.id || 'none';
        
        const my_assets = await getEmployeeAssets(emp_id);
        
        const assetRequestRows = await query(
            `SELECT status, count(*) as count
             FROM (
                SELECT status
                FROM requests
                WHERE employee_id = ?

                UNION ALL

                SELECT CASE
                    WHEN a.status = 'pending' THEN 'pending'
                    WHEN a.status = 'rejected' THEN 'rejected'
                    ELSE 'approved'
                END as status
                FROM assets a
                WHERE a.source_type = 'excel_import'
                  AND (a.source_user_id = ? OR a.current_owner_id = ?)
             )
             GROUP BY status`,
            [emp_id, req.user.id, emp_id]
        );
        const asset_request_counts = { pending: 0, approved: 0, rejected: 0 };
        assetRequestRows.forEach(row => {
            if (row.status in asset_request_counts) asset_request_counts[row.status] = row.count;
        });

        const transferRequestRows = await query(
            `SELECT status, count(*) as count
             FROM transfers
             WHERE requested_by = ? OR from_employee_id = ? OR to_employee_id = ?
             GROUP BY status`,
            [req.user.id, emp_id, emp_id]
        );
        const transfer_request_counts = { pending: 0, approved: 0, rejected: 0 };
        transferRequestRows.forEach(row => {
            if (row.status === 'completed') {
                transfer_request_counts.approved += row.count;
            } else if (row.status in transfer_request_counts) {
                transfer_request_counts[row.status] = row.count;
            }
        });

        const pending_requests = asset_request_counts.pending;
        
        const my_requests = await query(`
            SELECT * FROM requests WHERE employee_id = ? ORDER BY requested_date DESC LIMIT 5
        `, [emp_id]);
        
        const my_issues = await query(`
            SELECT m.*, a.asset_tag FROM maintenance m JOIN assets a ON m.asset_id = a.id
            WHERE m.reported_by = ? ORDER BY m.reported_date DESC LIMIT 5
        `, [req.user.id]);

        return res.render('employee-dashboard.html', {
            employee: req.user,
            my_assets,
            my_requests,
            my_issues,
            stats: {
                total_assets: my_assets.length,
                pending_requests
            },
            asset_request_counts,
            transfer_request_counts
        });
    }
    const stats = {};
    stats.total_assets    = (await get(`SELECT count(*) as c FROM assets WHERE status NOT IN ('pending', 'rejected')`)).c;
    stats.assigned        = (await get(`SELECT count(*) as c FROM assets WHERE status='assigned'`)).c;
    stats.available       = (await get(`SELECT count(*) as c FROM assets WHERE status='available'`)).c;
    stats.maintenance     = (await get(`SELECT count(*) as c FROM assets WHERE status='maintenance'`)).c;
    stats.pending_requests= (await get(`SELECT count(*) as c FROM requests WHERE status='pending'`)).c;
    stats.warranty_expiring = (await get(
        `SELECT count(*) as c
         FROM assets a
         WHERE ${WARRANTY_ENABLED_EXPR}
           AND a.status NOT IN ('pending', 'rejected')
           AND CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) BETWEEN 0 AND 30`
    )).c;

    const recent_assets = await query(`
        SELECT a.asset_tag, a.brand, a.model, a.status, a.id, e.name as assigned_to_name
        FROM assets a LEFT JOIN employees e ON a.current_owner_id = e.id
        WHERE a.status NOT IN ('pending', 'rejected')
        ORDER BY a.created_at DESC LIMIT 5
    `);
    const recent_requests = await query(`
        SELECT r.id, r.request_type, r.category, r.status, r.requested_date, e.name as employee_name
        FROM requests r JOIN employees e ON r.employee_id = e.id
        WHERE r.status = 'pending'
        ORDER BY r.requested_date DESC LIMIT 5
    `);

    const department_stats_raw = await query(`
        SELECT CASE WHEN department IS NULL OR department = '' THEN 'Unknown' ELSE department END as name, count(*) as value
        FROM assets
        WHERE status NOT IN ('pending', 'rejected')
        GROUP BY name
        ORDER BY value DESC
        LIMIT 5
    `);
    let max_dept_value = 0;
    for (let d of department_stats_raw) {
        if (d.value > max_dept_value) max_dept_value = d.value;
    }
    const department_stats = department_stats_raw.map(d => ({
        ...d,
        percent: max_dept_value > 0 ? Math.round((d.value / max_dept_value) * 100) : 0
    }));

    const category_stats_raw = await query(`
        SELECT CASE WHEN category IS NULL OR category = '' THEN 'Unknown' ELSE category END as name, count(*) as value
        FROM assets
        WHERE status NOT IN ('pending', 'rejected')
        GROUP BY name
        ORDER BY value DESC
        LIMIT 6
    `);
    const colors = ['var(--accent-amber)', 'var(--accent-ice)', 'var(--status-warn)', 'var(--status-active)', 'var(--border-glow)', 'var(--text-disabled)'];
    let current_percent_sum = 0;
    const category_stats = category_stats_raw.map((c, i) => {
        let pct = stats.total_assets > 0 ? Math.round((c.value / stats.total_assets) * 100) : 0;
        let start_pct = current_percent_sum;
        current_percent_sum += pct;
        return {
            ...c,
            color: colors[i % colors.length],
            percent: pct,
            start_pct: start_pct,
            end_pct: current_percent_sum
        };
    });

    res.render('dashboard.html', { stats, recent_assets, recent_requests, department_stats, category_stats });
});

// ============================================================
// Inventory & Asset CRUD
// ============================================================

app.get('/warranty-lists', requireAuth, requireRole(['admin', 'super_admin']), async (req, res) => {
    try {
        const user = req.user || res.locals.user;
        const q = req.query.q || '';
        const department = req.query.department || '';

        let sql = `
            SELECT a.id, a.asset_tag, a.brand, a.model, a.department, a.purchase_date,
                   ${WARRANTY_DATE_EXPR} as warranty_date,
                   e.name as assigned_to_name,
                   CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) as days_remaining
            FROM assets a
            LEFT JOIN employees e ON a.current_owner_id = e.id
            WHERE ${WARRANTY_ENABLED_EXPR}
              AND a.status NOT IN ('pending', 'rejected')
        `;

        let params = [];
        if (q) {
            sql += " AND (a.asset_tag LIKE ? OR a.model LIKE ? OR e.name LIKE ?)";
            const term = '%' + q + '%';
            params.push(term, term, term);
        }
        if (department) {
            sql += " AND a.department = ?";
            params.push(department);
        }

        // Default sort: soonest-expiring first
        sql += ` ORDER BY ${WARRANTY_DATE_EXPR} ASC`;

        const assets = await query(sql, params);

        // Calculate statuses
        assets.forEach(a => {
            if (a.days_remaining < 0) {
                a.warranty_status = 'expired';
            } else if (a.days_remaining <= 30) {
                a.warranty_status = 'expiring_soon';
            } else {
                a.warranty_status = 'active';
            }
        });

        const departments = await query('SELECT DISTINCT department FROM employees WHERE department IS NOT NULL');
        
        res.render('warranty-lists.html', {
            assets,
            searchQuery: q,
            selectedDept: department,
            departments,
            path: '/warranty-lists',
            user
        });
    } catch (err) {
        console.error("Error in /warranty-lists:", err);
        renderError(res, 500, "Server Error", "Could not fetch warranty lists.");
    }
});

app.get('/api/warranty-status', requireAuth, requireRole(['admin', 'super_admin']), async (req, res) => {
    try {
        const q = req.query.q || '';
        const department = req.query.department || '';

        let sql = `
            SELECT a.id, a.asset_tag, a.brand, a.model, a.department, a.purchase_date,
                   ${WARRANTY_DATE_EXPR} as warranty_date,
                   e.name as assigned_to_name,
                   CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) as days_remaining
            FROM assets a
            LEFT JOIN employees e ON a.current_owner_id = e.id
            WHERE ${WARRANTY_ENABLED_EXPR}
              AND a.status NOT IN ('pending', 'rejected')
        `;

        let params = [];
        if (q) {
            sql += " AND (a.asset_tag LIKE ? OR a.model LIKE ? OR e.name LIKE ?)";
            const term = '%' + q + '%';
            params.push(term, term, term);
        }
        if (department) {
            sql += " AND a.department = ?";
            params.push(department);
        }

        sql += ` ORDER BY ${WARRANTY_DATE_EXPR} ASC`;

        const assets = await query(sql, params);
        
        const mappedAssets = assets.map(a => {
            let status = 'active';
            if (a.days_remaining < 0) status = 'expired';
            else if (a.days_remaining <= 30) status = 'expiring_soon';
            
            return {
                id: a.id,
                asset_tag: a.asset_tag,
                name: `${a.brand} ${a.model}`,
                assigned_to_name: a.assigned_to_name || 'Unassigned',
                department: a.department || '-',
                purchase_date: a.purchase_date,
                warranty_date: a.warranty_date,
                days_remaining: a.days_remaining,
                status: status
            };
        });
        
        res.json(mappedAssets);
    } catch (err) {
        res.status(500).json({ error: "Internal error" });
    }
});

app.get('/api/dashboard-counts', requireAuth, requireRole(['admin', 'super_admin']), async (req, res) => {
    try {
        const { count: warranty_expiring } = await get(`
            SELECT count(*) as count 
            FROM assets a
            WHERE ${WARRANTY_ENABLED_EXPR}
              AND a.status NOT IN ('pending', 'rejected') 
              AND CAST(julianday(${WARRANTY_DATE_EXPR}) - julianday('now') AS INTEGER) BETWEEN 0 AND 30
        `);
        res.json({ warranty_expiring });
    } catch (err) {
        console.error("Error in /api/dashboard-counts:", err);
        res.status(500).json({ error: "Internal error" });
    }
});

app.get('/inventory', requireAuth, async (req, res) => {
    const { search, category, status, department, location } = req.query;
    const requestedPage = Math.max(1, Number.parseInt(req.query.page, 10) || 1);
    const pageSize = 25;

    let sql = `
        SELECT a.*, e.name as assigned_to_name
        FROM assets a LEFT JOIN employees e ON a.current_owner_id = e.id
        WHERE a.status NOT IN ('pending', 'rejected')
    `;
    const params = [];
    
    if (req.user.role === 'employee') {
        sql += ` AND a.current_owner_id = ?`;
        params.push(req.employee.id);
    }
    if (search) {
        sql += ` AND (a.brand LIKE ? OR a.model LIKE ? OR a.asset_tag LIKE ?)`;
        params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (category)   { sql += ` AND a.category = ?`;   params.push(category); }
    if (status)     { sql += ` AND a.status = ?`;     params.push(status); }
    if (department) { sql += ` AND a.department = ?`; params.push(department); }
    if (location)   { sql += ` AND a.location = ?`;   params.push(location); }
    const { count: total } = await get(`SELECT COUNT(*) as count FROM (${sql}) filtered_assets`, params);
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const page = Math.min(requestedPage, totalPages);
    sql += ` ORDER BY a.created_at DESC, a.asset_tag DESC LIMIT ? OFFSET ?`;
    params.push(pageSize, (page - 1) * pageSize);

    const rawAssets = await query(sql, params);
    const assets = rawAssets.map(a => ({
        ...a,
        id: a.id,
        name: `${a.brand} ${a.model}`,
        tag: a.asset_tag,
        category: a.category,
        status: a.status,
        department: a.department,
        location: a.location,
        assigned_employee: a.assigned_to_name ? { name: a.assigned_to_name } : null
    }));

    const categories  = await query(`SELECT DISTINCT category  FROM assets ORDER BY category`);
    const departments = await query(`SELECT DISTINCT department FROM assets ORDER BY department`);
    const locations   = await query(`SELECT DISTINCT location   FROM assets ORDER BY location`);
    const inventoryQuery = new URLSearchParams();
    for (const [key, value] of Object.entries({ search, category, status, department, location })) {
        if (value) inventoryQuery.set(key, value);
    }
    const pageUrl = (targetPage) => {
        const nextQuery = new URLSearchParams(inventoryQuery);
        nextQuery.set('page', String(targetPage));
        return `/inventory?${nextQuery.toString()}`;
    };

    res.render('inventory.html', {
        assets,
        filters: { search: search || '', category: category || '', status: status || '', department: department || '', location: location || '' },
        categories,
        departments,
        locations,
        total,
        page,
        pageSize,
        totalPages,
        previousPageUrl: page > 1 ? pageUrl(page - 1) : null,
        nextPageUrl: page < totalPages ? pageUrl(page + 1) : null,
        user: req.user
    });
});

app.get('/inventory/export', requireAuth, async (req, res) => {
    try {
        let exportSql = `
            SELECT a.*, e.name as current_owner_name
            FROM assets a
            LEFT JOIN employees e ON a.current_owner_id = e.id
            WHERE a.status NOT IN ('pending', 'rejected')`;
        const exportParams = [];
        if (req.user.role === 'employee') {
            exportSql += ` AND a.current_owner_id = ?`;
            exportParams.push(req.employee.id || 'none');
        }
        exportSql += ` ORDER BY a.asset_tag ASC`;
        const assets = await query(exportSql, exportParams);

        if (!assets || assets.length === 0) {
            return res.status(404).send('No assets found to export.');
        }

        const headers = ['Asset Tag', 'Brand', 'Model', 'Serial Number', 'Category', 'Department', 'Location', 'Status', 'Current Owner', 'Purchase Date', 'Warranty Date', 'Purchase Cost'];
        let csvContent = headers.join(',') + '\n';

        assets.forEach(asset => {
            const row = [
                asset.asset_tag,
                asset.brand,
                asset.model,
                asset.serial_number,
                asset.category,
                asset.department,
                asset.location,
                asset.status,
                asset.current_owner_name || '',
                asset.purchase_date || '',
                asset.warranty_date || '',
                asset.purchase_cost || ''
            ].map(val => {
                let str = String(val || '').replace(/"/g, '""').replace(/[\r\n]+/g, ' ');
                return `"${str}"`;
            });
            csvContent += row.join(',') + '\n';
        });

        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="inventory_assets.csv"');
        res.send(csvContent);
    } catch (err) {
        console.error('Export inventory error:', err);
        res.status(500).send('Error exporting inventory data');
    }
});


// ============================================================
// Bulk Import Template
app.get('/assets/import-template', requireAuth, (req, res) => {
    const ws_data = [
        ['asset_tag', 'brand', 'model', 'serial_number', 'category', 'department', 'location', 'purchase_date', 'warranty_date', 'purchase_cost', 'status', 'sl_no', 'monitor_make', 'monitor_serial_no', 'asset_owner_pl_no', 'asset_usage_status', 'in_warranty_status', 'system_serial_no', 'host_name', 'group_name', 'division', 'user_name', 'designation', 'ip_address', 'mac_address', 'network_type', 'drona_domain', 'os_version', 'antivirus_status', 'usb_status', 'admin_privilege', 'owner_email']
    ];
    const ws = xlsx.utils.aoa_to_sheet(ws_data);
    const wb = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(wb, ws, 'Template');
    const buf = xlsx.write(wb, { type: 'buffer', bookType: 'xlsx' });
    res.setHeader('Content-Disposition', 'attachment; filename="asset_import_template.xlsx"');
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.send(buf);
});

// Bulk Import Submission
app.post('/assets/import', requireAuth, upload.single('excel_file'), async (req, res) => {
    if (!req.file || path.extname(req.file.originalname).toLowerCase() !== '.xlsx') {
        return res.render('assets-new.html', { error: 'Please upload a valid Excel (.xlsx) file.', values: {}, req, importSummary: null });
    }

    let rows = [];
    try {
        const wb = xlsx.read(req.file.buffer, { type: 'buffer' });
        const ws = wb.Sheets[wb.SheetNames[0]];
        rows = xlsx.utils.sheet_to_json(ws);
        if (rows.length > 5000) {
            return res.render('assets-new.html', { error: 'Excel imports are limited to 5,000 rows.', values: {}, req, importSummary: null });
        }
    } catch (err) {
        return res.render('assets-new.html', { error: 'Failed to parse Excel file.', values: {}, req, importSummary: null });
    }

    let importedCount = 0;
    let skippedCount = 0;
    let skippedReasons = [];

    try {
        await transaction(async (tx) => {
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const rowNum = i + 2; // 1 for header, 1 for 0-index

                let { 
                    asset_tag, brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
                    sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                    system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                    network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, owner_email
                } = row;

                asset_tag = asset_tag ? String(asset_tag).trim() : '';
                serial_number = serial_number ? String(serial_number).trim() : '';

                if (!asset_tag) {
                    skippedCount++;
                    skippedReasons.push(`Row ${rowNum}: Missing asset_tag`);
                    continue;
                }

                if (!serial_number) {
                    skippedCount++;
                    skippedReasons.push(`Row ${rowNum}: Missing mandatory fields (serial_number)`);
                    continue;
                }

                const existingTag = await tx.get(`SELECT id FROM assets WHERE asset_tag = ?`, [asset_tag]);
                if (existingTag) {
                    skippedCount++;
                    skippedReasons.push(`Row ${rowNum}: Asset tag ${asset_tag} already exists`);
                    continue;
                }

                const existingSerial = await tx.get(`SELECT id FROM assets WHERE serial_number = ?`, [serial_number]);
                if (existingSerial) {
                    skippedCount++;
                    skippedReasons.push(`Row ${rowNum}: Serial number ${serial_number} already exists`);
                    continue;
                }

                let current_owner_id = null;
                if (owner_email) {
                    const ownerStr = String(owner_email).trim();
                    const emp = await tx.get(`SELECT id FROM employees WHERE email = ?`, [ownerStr]);
                    if (emp) {
                        current_owner_id = emp.id;
                    } else {
                        skippedReasons.push(`Row ${rowNum} Warning: Owner email ${ownerStr} not found, imported with NULL owner`);
                    }
                }

                const id = uuidv4();
                const { hasWarrantyValue, warrantyExpiryValue } = normalizeWarrantyFields({
                    hasWarranty: in_warranty_status ? (String(in_warranty_status).trim().toLowerCase() === 'yes' ? 1 : 0) : 0,
                    warrantyExpiryDate: warranty_date || null,
                    warranty_date: warranty_date || null,
                    in_warranty_status: in_warranty_status || ''
                });

                await tx.run(
                    `INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
                    sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                    system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                    network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id, hasWarranty, warrantyExpiryDate, source_type, source_user_id)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?, ?, ?, ?, ?)`,
                    [id, asset_tag, brand || 'Unknown', model || 'Unknown', serial_number, category || 'Other',
                     purchase_date || null, warranty_date || null,
                     parseFloat(purchase_cost) || 0, department || 'Unknown', location || 'Unknown', 'pending',
                     sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                     system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                     network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id, hasWarrantyValue, warrantyExpiryValue, 'excel_import', req.user.id]
                );
                await tx.run(
                    `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                    [uuidv4(), id, 'Imported', `Asset ${asset_tag} imported from Excel.`, req.user.id]
                );

                importedCount++;
            }
        });
    } catch (err) {
        return res.render('assets-new.html', { error: 'Database error during import: ' + err.message, values: {}, req, importSummary: null });
    }

    res.render('assets-new.html', { 
        error: null, 
        values: {}, 
        req, 
        importSummary: { importedCount, skippedCount, skippedReasons }
    });
});

// Pending Imports routes
app.get('/pending-imports', requireAuth, requireAdmin, async (req, res) => {
    try {
        const assets = await query(`SELECT * FROM assets WHERE status = 'pending' ORDER BY purchase_date DESC`);
        res.render('pending-imports.html', { req, user: req.user, assets, activePage: 'pending-imports' });
    } catch (err) {
        console.error('Error fetching pending imports:', err);
        res.render('error.html', { message: 'Internal Server Error' });
    }
});

app.post('/pending-imports/:id/approve', requireAuth, requireAdmin, async (req, res) => {
    try {
        await transaction(async (tx) => {
            const result = await tx.run(
                `UPDATE assets
                 SET status = CASE WHEN current_owner_id IS NULL THEN 'available' ELSE 'assigned' END
                 WHERE id = ? AND status = 'pending'`,
                [req.params.id]
            );
            if (result.changes === 0) return;
            await tx.run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), req.params.id, 'Import Approved', 'Excel import was approved by admin.', req.user.id]
            );
        });
        res.redirect('/pending-imports');
    } catch (err) {
        console.error('Error approving import:', err);
        res.render('error.html', { message: 'Internal Server Error' });
    }
});

app.post('/pending-imports/:id/reject', requireAuth, requireAdmin, async (req, res) => {
    try {
        await transaction(async (tx) => {
            const asset = await tx.get(`SELECT * FROM assets WHERE id = ? AND status = 'pending'`, [req.params.id]);
            if (!asset) return;
            await tx.run(
                ASSET_ARCHIVE_INSERT_SQL,
                buildAssetArchiveValues({ ...asset, source_type: asset.source_type || 'excel_import' }, req.user.id, 'Import Rejected by Admin')
            );
            await tx.run(`DELETE FROM asset_history WHERE asset_id = ?`, [req.params.id]);
            await tx.run(`DELETE FROM assets WHERE id = ?`, [req.params.id]);
        });
        res.redirect('/pending-imports');
    } catch (err) {
        console.error('Error rejecting import:', err);
        res.render('error.html', { message: 'Internal Server Error' });
    }
});

app.post('/pending-imports/approve-all', requireAuth, requireAdmin, async (req, res) => {
    try {
        await transaction(async (tx) => {
            const pendingAssets = await tx.query(`SELECT id FROM assets WHERE status = 'pending'`);
            for (const asset of pendingAssets) {
                await tx.run(
                    `UPDATE assets
                     SET status = CASE WHEN current_owner_id IS NULL THEN 'available' ELSE 'assigned' END
                     WHERE id = ? AND status = 'pending'`,
                    [asset.id]
                );
                await tx.run(
                    `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                    [uuidv4(), asset.id, 'Import Approved', 'Excel import was approved by admin (bulk).', req.user.id]
                );
            }
        });
        res.redirect('/pending-imports');
    } catch (err) {
        console.error('Error approving all imports:', err);
        res.render('error.html', { message: 'Internal Server Error' });
    }
});

app.post('/pending-imports/reject-all', requireAuth, requireAdmin, async (req, res) => {
    try {
        await transaction(async (tx) => {
            const pendingAssets = await tx.query(`SELECT * FROM assets WHERE status = 'pending'`);
            for (const asset of pendingAssets) {
                await tx.run(
                    ASSET_ARCHIVE_INSERT_SQL,
                    buildAssetArchiveValues({ ...asset, source_type: asset.source_type || 'excel_import' }, req.user.id, 'Import Rejected by Admin (bulk)')
                );
                await tx.run(`DELETE FROM asset_history WHERE asset_id = ?`, [asset.id]);
                await tx.run(`DELETE FROM assets WHERE id = ?`, [asset.id]);
            }
        });
        res.redirect('/pending-imports');
    } catch (err) {
        console.error('Error rejecting all imports:', err);
        res.render('error.html', { message: 'Internal Server Error' });
    }
});

// Add Asset form
app.get('/assets/new', requireAuth, (req, res) => {
    res.render('assets-new.html', { error: null, values: {}, req });
});

// Create Asset
app.post('/assets', requireAuth, async (req, res) => {
    let { 
        asset_tag, brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
        sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
        system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
        network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege,
        hasWarranty, warrantyExpiryDate
    } = req.body;
    
    asset_tag = asset_tag ? asset_tag.trim() : '';
    serial_number = serial_number ? serial_number.trim() : '';

    try {
        if (req.user.role === 'employee') {
            if (!category) {
                return res.render('assets-new.html', { error: 'Category is required to submit an asset request.', values: req.body, req });
            }

            const reqId = uuidv4();
            const requestDetails = [
                `Brand: ${brand || 'N/A'}`,
                `Model: ${model || 'N/A'}`,
                `Serial: ${serial_number || 'N/A'}`,
                `Department: ${department || req.employee.department || 'N/A'}`,
                `Location: ${location || 'N/A'}`,
                `Usage: ${asset_usage_status || 'N/A'}`,
                `Warranty: ${in_warranty_status || 'N/A'}`
            ].join(' | ');

            await run(
                `INSERT INTO requests (id, employee_id, request_type, category, justification, status) VALUES (?, ?, ?, ?, ?, 'pending')`,
                [reqId, req.employee.id, 'Asset Request', category, requestDetails]
            );
            await run(
                `INSERT INTO approvals (id, request_id, request_type, status) VALUES (?, ?, ?, 'pending')`,
                [uuidv4(), reqId, 'Asset Request']
            );
            return res.redirect('/requests');
        }

        if (!asset_tag) {
            const last = await get(`SELECT asset_tag FROM assets WHERE asset_tag LIKE 'AST-%' ORDER BY CAST(SUBSTR(asset_tag, 5) AS INTEGER) DESC LIMIT 1`);
            const num = last ? parseInt(last.asset_tag.replace('AST-', ''), 10) : 999;
            asset_tag = `AST-${num + 1}`;
        } else {
            const existingTag = await get(`SELECT id FROM assets WHERE asset_tag = ?`, [asset_tag]);
            if (existingTag) {
                return res.render('assets-new.html', { error: 'Asset tag already exists. Leave it blank to auto-generate one, or enter a different tag.', values: req.body, req });
            }
        }
        
        if (serial_number) {
            const existingSerial = await get(`SELECT id FROM assets WHERE serial_number = ?`, [serial_number]);
            if (existingSerial) {
                return res.render('assets-new.html', { error: 'Serial number already exists. Please enter a different serial number.', values: req.body, req });
            }
        }

        let current_owner_id = null;
        if (req.body.owner_email) {
            const emp = await get(`SELECT id FROM employees WHERE email = ?`, [String(req.body.owner_email).trim()]);
            if (emp) current_owner_id = emp.id;
        }
        if (!current_owner_id && req.body.employee_id) {
            const emp = await get(`SELECT id FROM employees WHERE id = ?`, [String(req.body.employee_id).trim()]);
            if (emp) current_owner_id = emp.id;
        }
        if (!current_owner_id && user_name) {
            const emp = await get(`SELECT id FROM employees WHERE name = ?`, [String(user_name).trim()]);
            if (emp) current_owner_id = emp.id;
        }

        let final_status = status || 'available';
        if (current_owner_id && (!status || status === 'available' || status === 'pending')) {
            final_status = 'assigned';
        }
        const { hasWarrantyValue, warrantyExpiryValue } = normalizeWarrantyFields({
            hasWarranty,
            warrantyExpiryDate,
            warranty_date,
            in_warranty_status
        });

        const id = uuidv4();
        
        await run(
            `INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id, hasWarranty, warrantyExpiryDate)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?, ?, ?)`,
            [id, asset_tag, brand, model, serial_number, category,
             purchase_date || null, warranty_date || null,
             parseFloat(purchase_cost) || 0, department, location, final_status,
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id, hasWarrantyValue, warrantyExpiryValue]
        );
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), id, 'Added', `Asset ${asset_tag} added to inventory.`, req.user.id]
        );
        res.redirect('/inventory');
    } catch (err) {
        console.error('Create asset error:', err.message);
        let errorMsg = 'Could not create asset. Please check the details and try again.';
        if (err.message && err.message.includes('assets.asset_tag')) {
            errorMsg = 'Asset tag already exists. Leave it blank to auto-generate one, or enter a different tag.';
        } else if (err.message && err.message.includes('assets.serial_number')) {
            errorMsg = 'Serial number already exists. Please enter a different serial number.';
        }
        res.render('assets-new.html', { error: errorMsg, values: req.body, req });
    }
});
// Asset Detail
app.get('/assets/:id', requireAuth, async (req, res) => {
    const asset = await get(
        `SELECT a.*, e.name as assigned_to_name, e.id as assigned_employee_id, e.department as assigned_dept
         FROM assets a LEFT JOIN employees e ON a.current_owner_id = e.id
         WHERE a.id = ?`,
        [req.params.id]
    );
    if (!asset) return res.status(404).send('Asset not found');
    if (req.user.role === 'employee' && asset.current_owner_id !== req.employee.id) {
        return res.status(403).send('Forbidden');
    }
    const history = await query(
        `SELECT h.*, u.username FROM asset_history h
         LEFT JOIN users u ON h.created_by = u.id
         WHERE h.asset_id = ? ORDER BY h.date DESC`,
        [req.params.id]
    );
    res.render('asset-detail.html', { asset, history });
});

// Edit Asset form
app.get('/assets/:id/edit', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
    if (!asset) return res.status(404).send('Asset not found');
    res.render('assets-edit.html', { asset, error: null });
});

// Update Asset
app.post('/assets/:id/edit', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { 
        brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
        sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
        system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
        network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege
    } = req.body;
    const { hasWarrantyValue, warrantyExpiryValue } = normalizeWarrantyFields({
        hasWarranty: req.body.hasWarranty,
        warrantyExpiryDate: req.body.warrantyExpiryDate,
        warranty_date,
        in_warranty_status
    });

    try {
        await run(
            `UPDATE assets SET brand=?, model=?, serial_number=?, category=?, department=?, location=?,
             purchase_date=?, warranty_date=?, purchase_cost=?, status=?, hasWarranty=?, warrantyExpiryDate=?,
             sl_no=?, monitor_make=?, monitor_serial_no=?, asset_owner_pl_no=?, asset_usage_status=?, in_warranty_status=?,
             system_serial_no=?, host_name=?, group_name=?, division=?, user_name=?, designation=?, ip_address=?, mac_address=?,
             network_type=?, drona_domain=?, os_version=?, antivirus_status=?, usb_status=?, admin_privilege=?
             WHERE id=?`,
            [brand, model, serial_number, category, department, location,
             purchase_date || null, warranty_date || null, parseFloat(purchase_cost) || 0, status, hasWarrantyValue, warrantyExpiryValue,
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege,
             req.params.id]
        );
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), req.params.id, 'Updated', `Asset details updated by ${req.user.username}.`, req.user.id]
        );
        res.redirect(`/assets/${req.params.id}`);
    } catch (err) {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        res.render('assets-edit.html', { asset, error: err.message });
    }
});
// Unassign Asset
app.post('/assets/:id/unassign', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
    if (!asset) return res.status(404).send('Not found');
    await run(`UPDATE assets SET current_owner_id = NULL, status = 'available' WHERE id = ?`, [req.params.id]);
    await run(
        `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
        [uuidv4(), req.params.id, 'Returned', 'Asset unassigned and returned to available pool.', req.user.id]
    );
    res.redirect(`/assets/${req.params.id}`);
});

// Archive Asset
app.post('/api/assets/:id/archive', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { reason } = req.body;
    try {
        await transaction(async (tx) => {
            const asset = await tx.get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
            if (!asset) {
                const err = new Error('Not found');
                err.statusCode = 404;
                throw err;
            }
            await tx.run(
                ASSET_ARCHIVE_INSERT_SQL,
                buildAssetArchiveValues(asset, req.user.id, reason || 'Manual Archive', asset.status)
            );
            await tx.run(`DELETE FROM maintenance WHERE asset_id = ?`, [req.params.id]);
            await tx.run(`DELETE FROM transfers WHERE asset_id = ?`, [req.params.id]);
            await tx.run(`DELETE FROM assets WHERE id = ?`, [req.params.id]);
        });
        res.redirect('/inventory');
    } catch (err) {
        res.status(err.statusCode || 500).send(err.statusCode ? err.message : 'Error archiving asset');
    }
});
// ============================================================
// Asset Assignment
// ============================================================
app.get('/asset-assignment', requireAuth, requireAdmin, async (req, res) => {
    const available_assets = await query(
        `SELECT id, asset_tag, brand, model, category FROM assets WHERE status = 'available' ORDER BY asset_tag`
    );
    const employees = await query(
        `SELECT e.*, (SELECT count(*) FROM assets a WHERE a.current_owner_id = e.id) as assets_count
         FROM employees e WHERE e.status = 'active' ORDER BY e.name`
    );
    const preselect_asset = req.query.asset_id || null;
    res.render('asset-assignment.html', {
        available_assets,
        employees,
        preselect_asset,
        error: req.query.error || null,
        success: req.query.success || null
    });
});

app.post('/asset-assignment', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { asset_id, employee_id } = req.body;
    try {
        await transaction(async (tx) => {
            const asset = await tx.get(`SELECT * FROM assets WHERE id = ?`, [asset_id]);
            if (!asset) throw new Error('Asset not found');
            if (asset.status !== 'available') throw new Error(`Asset is currently "${asset.status}" and cannot be assigned`);
            const employee = await tx.get(`SELECT * FROM employees WHERE id = ?`, [employee_id]);
            if (!employee) throw new Error('Employee not found');

            await tx.run(`UPDATE assets SET current_owner_id = ?, status = 'assigned' WHERE id = ? AND status = 'available'`, [employee_id, asset_id]);
            await tx.run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), asset_id, 'Assigned', `Assigned to ${employee.name}.`, req.user.id]
            );
            await tx.run(
                `INSERT INTO transfers (id, asset_id, from_employee_id, to_employee_id, requested_by, approved_by, status, notes) VALUES (?,?,?,?,?,?,?,?)`,
                [uuidv4(), asset_id, null, employee_id, req.user.id, req.user.id, 'completed', `Initial assignment to ${employee.name}`]
            );
        });
        res.redirect('/inventory?success=Asset+assigned+successfully');
    } catch (err) {
        res.redirect(`/asset-assignment?asset_id=${asset_id || ''}&error=${encodeURIComponent(err.message)}`);
    }
});

// ============================================================
// Employees
// ============================================================
async function getManagers() {
    return await query(`
        SELECT e.id, e.name, e.department
        FROM employees e
        JOIN users u ON e.user_id = u.id
        WHERE u.role IN ('admin', 'super_admin')
        ORDER BY e.name ASC
    `);
}

app.get('/employees/new', requireAuth, requireAdmin, async (req, res) => {
    try {
        const managers = await getManagers();
        res.render('add-user.html', { error: null, managers });
    } catch (err) {
        console.error('Error fetching managers:', err);
        res.render('add-user.html', { error: 'Failed to load managers', managers: [] });
    }
});

app.get('/users/new', requireAuth, requireAdmin, (req, res) => {
    res.redirect('/employees/new');
});

app.post('/employees', requireAuth, requireAdmin, async (req, res) => {
    let { name, email, department, role, location, phone, designation, join_date, manager_id } = req.body;
    location = location || "Head Office";
    try {
        if (!name || !email || !department || !role) {
            const managers = await getManagers();
            return res.render('add-user.html', { error: 'Please fill all mandatory fields', managers });
        }
        if (!['employee', 'admin'].includes(role) || (role === 'admin' && req.user.role !== 'super_admin')) {
            const managers = await getManagers();
            return res.status(403).render('add-user.html', { error: 'You cannot create a user with that role', managers });
        }
        
        // Ensure email isn't used
        const existingEmp = await get(`SELECT id FROM employees WHERE email = ?`, [email]);
        if (existingEmp) {
            const managers = await getManagers();
            return res.render('add-user.html', { error: 'Email already exists', managers });
        }
        
        // The username will just be the prefix of email
        const username = email.split('@')[0];
        
        // See if username is taken, append random if so
        let finalUsername = username;
        let existingUser = await get(`SELECT id FROM users WHERE username = ?`, [finalUsername]);
        if (existingUser) {
            finalUsername = username + Math.floor(Math.random() * 1000);
        }

        const user_id = uuidv4();
        const temporaryPassword = process.env.DEFAULT_USER_PASSWORD || 'Welcome123!';
        const passwordHash = await bcrypt.hash(temporaryPassword, 12);
        await run(`INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)`, [user_id, finalUsername, passwordHash, role]);
        
        const emp_id = uuidv4();
        await run(`INSERT INTO employees (id, user_id, name, email, phone, department, designation, location, join_date, manager_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, 
                  [emp_id, user_id, name, email, phone || null, department, designation || null, location, join_date || new Date().toISOString().substring(0, 10), manager_id || null, "Active"]);
                  
        res.redirect('/employees');
    } catch (err) {
        const managers = await getManagers();
        res.render('add-user.html', { error: err.message, managers });
    }
});

app.get('/employees', requireAuth, requireAdmin, async (req, res) => {
    const rows = await query(
        `SELECT e.*, u.role, (SELECT count(*) FROM assets a WHERE a.current_owner_id = e.id) as assets_count
         FROM employees e
         LEFT JOIN users u ON e.user_id = u.id
         ORDER BY e.name ASC`
    );
    const employees = rows.map((employee) => ({
        ...employee,
        initials: String(employee.name || '?')
            .trim()
            .split(/\s+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part[0])
            .join('')
            .toUpperCase() || '?'
    }));
    res.render('employee-directory.html', { employees });
});

app.get('/employee-profile', requireAuth, async (req, res) => {
    const id = req.query.id;
    if (!id) return res.redirect('/employees');
    if (req.user.role === 'employee' && id !== req.employee.id) return res.status(403).send('Forbidden');
    const employee = await get(`SELECT * FROM employees WHERE id = ?`, [id]);
    if (!employee) return res.status(404).send('Employee not found');
    const assigned_assets = await query(
        `SELECT * FROM assets WHERE current_owner_id = ? ORDER BY created_at DESC`, [id]
    );
    const emp_requests = await query(
        `SELECT * FROM requests WHERE employee_id = ? ORDER BY requested_date DESC LIMIT 10`, [id]
    );
    const recent_history = await query(
        `SELECT h.*, a.asset_tag, a.brand, a.model FROM asset_history h
         JOIN assets a ON h.asset_id = a.id
         WHERE a.current_owner_id = ? ORDER BY h.date DESC LIMIT 10`, [id]
    );
    res.render('employee-profile.html', { employee, assigned_assets, emp_requests, recent_history });
});

// ============================================================
// Maintenance
// ============================================================
app.get('/maintenance', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    let sql = `
        SELECT m.*, a.asset_tag, a.brand, a.model, a.id as asset_db_id, e.name as reported_by_name
        FROM maintenance m
        JOIN assets a ON m.asset_id = a.id
        LEFT JOIN users u ON m.reported_by = u.id
        LEFT JOIN employees e ON u.id = e.user_id
    `;
    const params = [];
    if (req.user.role === 'employee') {
        sql += ` WHERE m.reported_by = ?`;
        params.push(req.user.id);
        if (statusFilter) { sql += ` AND m.status = ?`; params.push(statusFilter); }
    } else {
        if (statusFilter) { sql += ` WHERE m.status = ?`; params.push(statusFilter); }
    }
    sql += ` ORDER BY m.reported_date DESC`;

    const maintenance = await query(sql, params);
    const all_assets = req.user.role === 'employee'
        ? await query(`SELECT id, asset_tag, brand, model FROM assets WHERE current_owner_id = ? ORDER BY asset_tag`, [req.employee.id || 'none'])
        : await query(`SELECT id, asset_tag, brand, model FROM assets ORDER BY asset_tag`);
    res.render('maintenance.html', { maintenance, all_assets, statusFilter: statusFilter || '' });
});

app.post('/maintenance', requireAuth, async (req, res) => {
    const { asset_id, issue_description, status } = req.body;
    try {
        const ticketStatus = status || 'pending';
        if (!['pending', 'in_progress', 'completed'].includes(ticketStatus)) throw new Error('Invalid maintenance status');
        await transaction(async (tx) => {
            const asset = await tx.get(`SELECT id, current_owner_id FROM assets WHERE id = ?`, [asset_id]);
            if (!asset || (req.user.role === 'employee' && asset.current_owner_id !== req.employee.id)) {
                const err = new Error('Forbidden');
                err.statusCode = 403;
                throw err;
            }
            await tx.run(
                `INSERT INTO maintenance (id, asset_id, issue_description, status, reported_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), asset_id, issue_description, ticketStatus, req.user.id]
            );
            if (ticketStatus !== 'completed') {
                await tx.run(`UPDATE assets SET status = 'maintenance' WHERE id = ?`, [asset_id]);
            }
            await tx.run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), asset_id, 'Maintenance Start', `Ticket created: ${issue_description}`, req.user.id]
            );
        });
        res.redirect('/maintenance');
    } catch (err) {
        if (err.statusCode === 403) return res.status(403).send('Forbidden');
        res.redirect(`/maintenance?error=${encodeURIComponent(err.message)}`);
    }
});

app.post('/maintenance/:id/status', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { status } = req.body;
    try {
        if (!['pending', 'in_progress', 'completed'].includes(status)) throw new Error('Invalid maintenance status');
        await transaction(async (tx) => {
            const ticket = await tx.get(`SELECT * FROM maintenance WHERE id = ?`, [req.params.id]);
            if (!ticket) {
                const err = new Error('Ticket not found');
                err.statusCode = 404;
                throw err;
            }
            await tx.run(
                `UPDATE maintenance SET status = ?,
                 resolved_date = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE resolved_date END
                 WHERE id = ?`,
                [status, status, req.params.id]
            );
            if (status === 'completed') {
                await tx.run(`UPDATE assets SET status = 'available' WHERE id = ? AND status = 'maintenance'`, [ticket.asset_id]);
                await tx.run(
                    `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                    [uuidv4(), ticket.asset_id, 'Maintenance End', 'Maintenance completed, asset returned to available.', req.user.id]
                );
            }
        });
        res.redirect('/maintenance');
    } catch (err) {
        if (err.statusCode === 404) return res.status(404).send(err.message);
        res.redirect(`/maintenance?error=${encodeURIComponent(err.message)}`);
    }
});

// ============================================================
// Requests
// ============================================================
app.post('/requests', requireAuth, async (req, res) => {
    if (req.user.role !== 'employee') return res.status(403).send('Forbidden');
    const { category, priority, justification } = req.body;
    try {
        if (!category || !priority || !justification) {
            return res.render('add-asset.html', { error: 'Please fill all fields' });
        }
        
        // Note: Requests table does not have a priority column by default, we'll append it to justification.
        const fullJustification = `[Priority: ${priority}] ${justification}`;
        
        const reqId = uuidv4();
        await run(
            `INSERT INTO requests (id, employee_id, request_type, category, justification, status) VALUES (?, ?, ?, ?, ?, 'pending')`,
            [reqId, req.employee.id, 'Asset Request', category, fullJustification]
        );
        
        await run(
            `INSERT INTO approvals (id, request_id, request_type, status) VALUES (?, ?, ?, 'pending')`,
            [uuidv4(), reqId, 'Asset Request']
        );
        
        return res.render('add-asset.html', { success: 'Asset request submitted successfully.' });
    } catch (err) {
        return res.render('add-asset.html', { error: err.message });
    }
});
app.get('/requests', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    if (req.user.role === 'employee') {
        const employeeRequests = await query(`
            SELECT r.*, e.name as employee_name, e.department,
                   a.asset_tag as fulfilled_asset_tag,
                   a.brand as fulfilled_asset_brand,
                   a.model as fulfilled_asset_model,
                   'request' as entry_kind,
                   r.id as polling_id
            FROM requests r
            JOIN employees e ON r.employee_id = e.id
            LEFT JOIN assets a ON a.id = r.fulfilled_asset_id
            WHERE r.employee_id = ?
            ORDER BY r.requested_date DESC
        `, [req.employee.id || 'none']);

        const importedAssets = await query(`
            SELECT 'import-' || a.id as id, e.name as employee_name, e.department,
                   'Excel Import' as request_type, a.category, a.created_at as requested_date,
                   NULL as decision_date, NULL as decided_by,
                   CASE
                       WHEN a.status = 'pending' THEN 'pending'
                       WHEN a.status = 'rejected' THEN 'rejected'
                       ELSE 'approved'
                   END as status,
                   a.asset_tag as fulfilled_asset_tag,
                   a.brand as fulfilled_asset_brand,
                   a.model as fulfilled_asset_model,
                   'import' as entry_kind,
                   'import-' || a.id as polling_id
            FROM assets a
            JOIN employees e ON e.id = ?
            WHERE (
                a.current_owner_id = ? 
                OR a.source_user_id = ?
                OR EXISTS (
                    SELECT 1
                    FROM asset_history h
                    WHERE h.asset_id = a.id
                      AND h.event_type = 'Imported'
                      AND (h.created_by = ? OR a.current_owner_id = ?)
                )
            )
            AND (
                a.source_type = 'excel_import'
                OR EXISTS (SELECT 1 FROM asset_history h WHERE h.asset_id = a.id AND h.event_type = 'Imported')
            )
        `, [req.employee.id || 'none', req.employee.id || 'none', req.user.id, req.user.id, req.employee.id || 'none']);

        const archivedImports = await query(`
            SELECT 'import-' || aa.original_asset_id as id, e.name as employee_name, e.department,
                   'Excel Import' as request_type, aa.category, aa.archived_at as requested_date,
                   aa.archived_at as decision_date, aa.archived_by as decided_by,
                   'rejected' as status,
                   aa.asset_tag as fulfilled_asset_tag,
                   aa.brand as fulfilled_asset_brand,
                   aa.model as fulfilled_asset_model,
                   'import' as entry_kind,
                   'import-' || aa.original_asset_id as polling_id
            FROM asset_archive aa
            JOIN employees e ON e.id = ?
            WHERE aa.source_type = 'excel_import'
              AND aa.source_user_id = ?
              AND aa.status = 'rejected'
        `, [req.employee.id || 'none', req.user.id]);

        const importedById = new Map();
        importedAssets.forEach(row => importedById.set(row.id, row));
        archivedImports.forEach(row => importedById.set(row.id, row));

        let requests = [...employeeRequests, ...Array.from(importedById.values())];
        if (statusFilter) {
            requests = requests.filter(row => row.status === statusFilter);
        }
        requests.sort((a, b) => String(b.requested_date || '').localeCompare(String(a.requested_date || '')));
        return res.render('requests.html', { requests, statusFilter: statusFilter || '', user: req.user });
    } else {
        let sql = `
            SELECT r.*, e.name as employee_name, e.department,
                   a.asset_tag as fulfilled_asset_tag,
                   a.brand as fulfilled_asset_brand,
                   a.model as fulfilled_asset_model,
                   'request' as entry_kind,
                   r.id as polling_id
            FROM requests r
            JOIN employees e ON r.employee_id = e.id
            LEFT JOIN assets a ON a.id = r.fulfilled_asset_id
        `;
        const params = [];
        if (statusFilter) {
            sql += ` WHERE r.status = ?`;
            params.push(statusFilter);
        }
        sql += ` ORDER BY r.requested_date DESC`;
        const requests = await query(sql, params);
        return res.render('requests.html', { requests, statusFilter: statusFilter || '', user: req.user });
    }
});

app.post('/requests/:id/approve', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    
    try {
        await transaction(async (tx) => {
            const requestRow = await tx.get(`SELECT * FROM requests WHERE id = ?`, [req.params.id]);
            if (!requestRow) {
                const err = new Error('Request not found');
                err.statusCode = 404;
                throw err;
            }
            if (requestRow.status !== 'pending') return;

            const emp = await tx.get(`SELECT department, location FROM employees WHERE id = ?`, [requestRow.employee_id]);
            if (!emp) {
                const err = new Error('Employee not found');
                err.statusCode = 404;
                throw err;
            }

            let assignedAssetId = null;
            const availableAsset = await tx.get(
                `SELECT id, asset_tag FROM assets WHERE status = 'available' AND category = ? LIMIT 1`,
                [requestRow.category]
            );

            if (availableAsset) {
                assignedAssetId = availableAsset.id;
                await tx.run(
                    `UPDATE assets SET current_owner_id = ?, status = 'assigned' WHERE id = ? AND status = 'available'`,
                    [requestRow.employee_id, assignedAssetId]
                );
            } else {
                assignedAssetId = uuidv4();
                const last = await tx.get(`SELECT asset_tag FROM assets WHERE asset_tag LIKE 'AST-%' ORDER BY CAST(SUBSTR(asset_tag, 5) AS INTEGER) DESC LIMIT 1`);
                const num = last ? parseInt(last.asset_tag.replace('AST-', ''), 10) : 999;
                const new_asset_tag = `AST-${num + 1}`;
                const new_serial = `REQ-${assignedAssetId.substring(0,8).toUpperCase()}`;

                await tx.run(
                    `INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, department, location, status, current_owner_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [assignedAssetId, new_asset_tag, 'Pending Procurement', requestRow.category || 'Unknown', new_serial, requestRow.category || 'Unknown', emp.department, emp.location, 'assigned', requestRow.employee_id]
                );
            }

            await tx.run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), assignedAssetId, 'Request Approved', 'Asset assigned/created from approved request', req.user.id]
            );

            await tx.run(
                `UPDATE requests SET status='approved', decided_by=?, decision_date=CURRENT_TIMESTAMP, fulfilled_asset_id=? WHERE id=? AND status='pending'`,
                [req.user.id, assignedAssetId, req.params.id]
            );
            await tx.run(
                `UPDATE approvals
                 SET status='approved', decided_by=?, decided_date=CURRENT_TIMESTAMP
                 WHERE request_id = ?`,
                [req.user.id, req.params.id]
            );
        });
        res.redirect('/requests');
    } catch (err) {
        console.error('Error approving request:', err);
        res.status(err.statusCode || 500).send(err.statusCode ? err.message : 'Error approving request');
    }
});

app.post('/requests/:id/reject', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    try {
        await transaction(async (tx) => {
            const result = await tx.run(
                `UPDATE requests SET status='rejected', decided_by=?, decision_date=CURRENT_TIMESTAMP WHERE id=? AND status='pending'`,
                [req.user.id, req.params.id]
            );
            if (result.changes === 0) return;
            await tx.run(
                `UPDATE approvals
                 SET status='rejected', decided_by=?, decided_date=CURRENT_TIMESTAMP
                 WHERE request_id = ?`,
                [req.user.id, req.params.id]
            );
        });
        res.redirect('/requests');
    } catch (err) {
        console.error('Error rejecting request:', err);
        res.status(500).send('Error rejecting request');
    }
});

// ============================================================
// Transfers
// ============================================================
app.get('/transfers', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    let sql = `
        SELECT t.*, a.asset_tag, a.brand, a.model, a.id as asset_db_id,
               e1.name as from_employee, e2.name as to_employee
        FROM transfers t
        JOIN assets a ON t.asset_id = a.id
        LEFT JOIN employees e1 ON t.from_employee_id = e1.id
        JOIN employees e2 ON t.to_employee_id = e2.id
    `;
    const params = [];
    if (req.user.role === 'employee') {
        sql += ` WHERE t.requested_by = ?`;
        params.push(req.user.id);
        if (statusFilter) { sql += ` AND t.status = ?`; params.push(statusFilter); }
    } else if (statusFilter) { sql += ` WHERE t.status = ?`; params.push(statusFilter); }
    sql += ` ORDER BY t.request_date DESC`;

    const transfers = await query(sql, params);
    const employees = await query(`SELECT id, name, department FROM employees WHERE status='active' ORDER BY name`);
    const assets = await query(`SELECT id, asset_tag, brand, model FROM assets WHERE status='assigned' ORDER BY asset_tag`);
    res.render('transfers.html', { transfers, employees, assets, statusFilter: statusFilter || '', user: req.user });
});

app.post('/transfers', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { asset_id, to_employee_id, notes } = req.body;
    try {
        const asset = await get(`SELECT * FROM assets WHERE id = ? AND status = 'assigned'`, [asset_id]);
        if (!asset) throw new Error('Asset not found');
        const toEmployee = await get(`SELECT id FROM employees WHERE id = ? AND status = 'active'`, [to_employee_id]);
        if (!toEmployee) throw new Error('Target employee not found');
        await run(
            `INSERT INTO transfers (id, asset_id, from_employee_id, to_employee_id, requested_by, status, notes) VALUES (?,?,?,?,?,?,?)`,
            [uuidv4(), asset_id, asset.current_owner_id, to_employee_id, req.user.id, 'pending', notes || '']
        );
        res.redirect('/transfers');
    } catch (err) {
        res.redirect(`/transfers?error=${encodeURIComponent(err.message)}`);
    }
});

app.post('/transfers/:id/approve', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    try {
        await transaction(async (tx) => {
            const transfer = await tx.get(`SELECT * FROM transfers WHERE id = ?`, [req.params.id]);
            if (!transfer) {
                const err = new Error('Not found');
                err.statusCode = 404;
                throw err;
            }
            if (transfer.status !== 'pending') return;
            await tx.run(
                `UPDATE transfers SET status='approved', approved_by=?, completion_date=CURRENT_TIMESTAMP WHERE id=? AND status='pending'`,
                [req.user.id, req.params.id]
            );
            await tx.run(`UPDATE assets SET current_owner_id=?, status='assigned' WHERE id=?`, [transfer.to_employee_id, transfer.asset_id]);
            const toEmp = await tx.get(`SELECT name FROM employees WHERE id=?`, [transfer.to_employee_id]);
            await tx.run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), transfer.asset_id, 'Reassigned', `Transferred to ${toEmp ? toEmp.name : 'new employee'}.`, req.user.id]
            );
        });
        res.redirect('/transfers');
    } catch (err) {
        if (err.statusCode === 404) return res.status(404).send(err.message);
        res.redirect(`/transfers?error=${encodeURIComponent(err.message)}`);
    }
});

app.post('/transfers/:id/reject', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    try {
        await run(
            `UPDATE transfers SET status='rejected', approved_by=?, completion_date=CURRENT_TIMESTAMP WHERE id=? AND status='pending'`,
            [req.user.id, req.params.id]
        );
        res.redirect('/transfers');
    } catch (err) {
        res.redirect(`/transfers?error=${encodeURIComponent(err.message)}`);
    }
});

// ============================================================
// Employee Live Polling Endpoints
// ============================================================
app.get('/employee/my-assets', requireAuth, async (req, res) => {
    if (req.user.role !== 'employee') return res.status(403).json({ error: 'Forbidden' });
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    try {
        const assets = await getEmployeeAssets(req.employee.id || 'none');
        res.json(assets);
    } catch (err) {
        res.status(500).json({ error: 'Database error' });
    }
});

app.get('/employee/asset-requests/status', requireAuth, async (req, res) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    try {
        const statuses = await query(
            `SELECT r.id, r.status, r.fulfilled_asset_id, a.asset_tag as fulfilled_asset_tag
             FROM requests r
             LEFT JOIN assets a ON a.id = r.fulfilled_asset_id
             WHERE r.employee_id = ?

             UNION ALL

             SELECT 'import-' || a.id as id,
                    CASE
                        WHEN a.status = 'pending' THEN 'pending'
                        WHEN a.status = 'rejected' THEN 'rejected'
                        ELSE 'approved'
                    END as status,
                    a.id as fulfilled_asset_id,
                    a.asset_tag as fulfilled_asset_tag
             FROM assets a
             WHERE a.source_type = 'excel_import'
               AND (a.source_user_id = ? OR a.current_owner_id = ?)

             UNION ALL

             SELECT 'import-' || aa.original_asset_id as id,
                    'rejected' as status,
                    NULL as fulfilled_asset_id,
                    aa.asset_tag as fulfilled_asset_tag
             FROM asset_archive aa
             WHERE aa.source_type = 'excel_import'
               AND (aa.source_user_id = ? OR aa.user_name = ? OR aa.department = ? OR aa.archived_by = ?)
               AND aa.status = 'rejected'`,
            [
                req.employee.id || 'none',
                req.user.id,
                req.employee.id || 'none',
                req.user.id,
                req.employee.name || 'none',
                req.employee.department || 'none',
                req.user.id
            ]
        );
        res.json(statuses);
    } catch (err) {
        res.status(500).json({ error: 'Database error' });
    }
});

app.get('/employee/transfer-requests/status', requireAuth, async (req, res) => {
    try {
        const statuses = await query(`
            SELECT id, status FROM transfers 
            WHERE requested_by = ? 
               OR from_employee_id = ? 
               OR to_employee_id = ?
        `, [req.user.id, req.employee.id || 'none', req.employee.id || 'none']);
        res.json(statuses);
    } catch (err) {
        res.status(500).json({ error: 'Database error' });
    }
});

// ============================================================
// Employee Transfer Requests
// ============================================================
app.get('/transfer-request', requireAuth, async (req, res) => {
    if (req.user.role !== 'employee') return res.redirect('/dashboard');
    const my_assets = await query(`
        SELECT a.id, a.asset_tag, a.brand, a.model
        FROM assets a
        WHERE a.current_owner_id = ?
    `, [req.employee.id]);
    const all_employees = await query(`
        SELECT id, name, department FROM employees WHERE id != ? AND status = 'active' ORDER BY name
    `, [req.employee.id]);
    res.render('transfer-request.html', {
        activePage: 'transfer-request',
        my_assets,
        all_employees,
        success: req.query.success,
        error: req.query.error
    });
});

app.post('/transfer-request', requireAuth, async (req, res) => {
    if (req.user.role !== 'employee') return res.status(403).send('Forbidden');
    const { asset_id, to_employee_id, notes } = req.body;
    try {
        if (!asset_id || !to_employee_id) throw new Error('Asset and To Employee are required');
        const asset = await get(`SELECT id FROM assets WHERE id = ? AND current_owner_id = ?`, [asset_id, req.employee.id]);
        if (!asset) throw new Error('You can only request transfers for your own assets.');
        
        await run(
            `INSERT INTO transfers (id, asset_id, from_employee_id, to_employee_id, requested_by, status, notes, transfer_type)
             VALUES (?, ?, ?, ?, ?, 'pending', ?, 'employee_request')`,
            [uuidv4(), asset_id, req.employee.id, to_employee_id, req.user.id, notes || '']
        );
        res.redirect('/transfer-request?success=1');
    } catch (err) {
        res.redirect(`/transfer-request?error=${encodeURIComponent(err.message)}`);
    }
});

// ============================================================
// Notifications
// ============================================================
app.get('/notifications', requireAuth, async (req, res) => {
    const notifications = await query(
        `SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC`,
        [req.user.id]
    );
    const unread_count = notifications.filter(n => !n.is_read).length;
    res.render('notifications.html', { notifications, unread_count });
});

app.post('/notifications/read-all', requireAuth, async (req, res) => {
    await run(`UPDATE notifications SET is_read=1 WHERE user_id=?`, [req.user.id]);
    res.redirect('/notifications');
});

app.post('/notifications/:id/read', requireAuth, async (req, res) => {
    await run(`UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?`, [req.params.id, req.user.id]);
    res.redirect('/notifications');
});

// ============================================================
// Reports
// ============================================================
app.get('/reports', requireAuth, requireAdmin, async (req, res) => {
    const statusCounts   = await query(`SELECT status, count(*) as count FROM assets GROUP BY status`);
    const categoryCounts = await query(`SELECT category, count(*) as count FROM assets GROUP BY category`);
    const totalCost      = await get(`SELECT sum(purchase_cost) as total FROM assets`);
    res.render('reports.html', { statusCounts, categoryCounts, totalCost: totalCost.total || 0 });
});

app.get('/archive', requireAuth, requireSuperAdmin, async (req, res) => {
    const archived_assets = await query(`
        SELECT aa.*, u.username as archived_by_name
        FROM asset_archive aa
        LEFT JOIN users u ON aa.archived_by = u.id
        ORDER BY aa.archived_at DESC
    `);
    res.render('archive.html', { archived_assets });
});

app.get('/archive/export', requireAuth, requireSuperAdmin, async (req, res) => {
    try {
        const archived_assets = await query(`
            SELECT aa.*, u.username as archived_by_name
            FROM asset_archive aa
            LEFT JOIN users u ON aa.archived_by = u.id
            ORDER BY aa.archived_at DESC
        `);

        if (!archived_assets || archived_assets.length === 0) {
            return res.status(404).send('No archived assets found to export.');
        }

        const headers = ['Asset Tag', 'Brand', 'Model', 'Serial Number', 'Category', 'Department', 'Location', 'Status', 'Archived By', 'Archived At', 'Reason'];
        let csvContent = headers.join(',') + '\n';

        archived_assets.forEach(asset => {
            const row = [
                asset.asset_tag,
                asset.brand,
                asset.model,
                asset.serial_number,
                asset.category,
                asset.department,
                asset.location,
                asset.status,
                asset.archived_by_name,
                asset.archived_at,
                asset.reason || ''
            ].map(val => {
                let str = String(val || '').replace(/"/g, '""').replace(/[\r\n]+/g, ' ');
                return `"${str}"`;
            });
            csvContent += row.join(',') + '\n';
        });

        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="archived_assets.csv"');
        res.send(csvContent);
    } catch (err) {
        console.error('Export archive error:', err);
        res.status(500).send('Error exporting archive data');
    }
});

// ============================================================
// Redirect helpers for old-style links
// ============================================================
app.get('/asset-detail', requireAuth, (req, res) => {
    if (req.query.id) return res.redirect(`/assets/${req.query.id}`);
    res.redirect('/inventory');
});

app.get('/requests/new', requireAuth, (req, res) => {
    res.redirect('/requests');
});

app.get('/maintenance/new', requireAuth, (req, res) => {
    res.render('add-issue.html', { error: null });
});

// ============================================================
// Catch-all for any remaining static pages
// ============================================================

app.get('/tasks', requireAuth, async (req, res) => {
    let sql = `
        SELECT t.*, e.name as assigned_to_name, u.username as assigned_by_name
        FROM tasks t
        JOIN employees e ON t.assigned_to = e.id
        JOIN users u ON t.assigned_by = u.id
        WHERE 1=1
    `;
    const params = [];
    
    if (req.user.role === 'employee') {
        sql += ` AND t.assigned_to = ?`;
        params.push(req.employee.id);
    } else if (req.user.role === 'admin') {
        sql += ` AND e.department = ?`;
        params.push(req.employee.department);
    }
    
    sql += ` ORDER BY t.created_at DESC`;
    const tasks = await query(sql, params);
    res.render('tasks.html', { tasks });
});


app.get('/approvals', requireAuth, requireAdmin, async (req, res) => {
    const pending = await query(`SELECT * FROM approvals WHERE status = 'pending' ORDER BY id DESC`);
    const history = await query(`SELECT * FROM approvals WHERE status != 'pending' ORDER BY decided_date DESC`);
    res.render('approvals.html', { pending, history });
});


app.get('/profile', requireAuth, async (req, res) => {
    const employee = await get(`SELECT * FROM employees WHERE user_id = ?`, [req.user.id]);
    res.render('profile.html', { employee, success: req.query.success });
});

app.post('/profile', requireAuth, async (req, res) => {
    const { phone, emergency_contact, address } = req.body;
    try {
        await run(
            `UPDATE employees SET phone=?, emergency_contact=?, address=? WHERE user_id=?`,
            [phone, emergency_contact, address, req.user.id]
        );
        res.redirect('/profile?success=1');
    } catch(err) {
        res.redirect('/profile?error=' + encodeURIComponent(err.message));
    }
});

// Admin-only pages that must not be accessible by employee-role users via the catch-all route
const ADMIN_ONLY_PAGES = new Set(['reports', 'approvals', 'archive', 'pending-imports', 'transfers', 'warranty-lists', 'asset-assignment', 'employee-directory']);

app.get('/:page', requireAuth, (req, res) => {
    const page = req.params.page.replace(/\.html$/, '');
    if (ADMIN_ONLY_PAGES.has(page) && req.user.role === 'employee') {
        return res.status(403).render('error.html', { statusCode: 403, title: 'Access Denied', message: 'You do not have permission to view this page.' });
    }
    const template = page.endsWith('.html') ? page : `${page}.html`;
    res.render(template, {}, (err, html) => {
        if (err) return renderError(res, 404, 'Page not found', 'This page is not available.');
        res.send(html);
    });
});

app.use((req, res) => {
    renderError(res, 404, 'Page not found', 'This page is not available.');
});

app.use((err, req, res, next) => {
    console.error('Unhandled request error:', err);
    if (res.headersSent) return next(err);
    renderError(res, 500, 'Something went wrong', 'The page could not be loaded. Please try again.');
});

// ============================================================
// Start Server
// ============================================================
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';
let httpServer;

async function ensureBootstrapAdmin() {
    const { count } = await get(`SELECT COUNT(*) as count FROM users`);
    if (count > 0) return;
    const username = process.env.ADMIN_USERNAME || 'admin';
    const password = process.env.ADMIN_PASSWORD;
    if (!password) {
        throw new Error('ADMIN_PASSWORD must be set when initializing an empty database');
    }
    if (password.length < 12) throw new Error('ADMIN_PASSWORD must contain at least 12 characters');
    await run(
        `INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, 'super_admin')`,
        [uuidv4(), username, await bcrypt.hash(password, 12)]
    );
    console.log(`Created bootstrap super administrator: ${username}`);
}

initDB()
    .then(ensureBootstrapAdmin)
    .then(() => {
        httpServer = app.listen(PORT, HOST);
        httpServer.on('listening', () => console.log(`Server is running on http://${HOST}:${PORT}`));
        httpServer.on('error', (err) => {
            console.error('Failed to start server:', err.message);
            process.exit(1);
        });
    })
    .catch(err => {
        console.error('Failed to initialize local database:', err);
        process.exit(1);
    });

function shutdown(signal) {
    console.log(`${signal} received, shutting down`);
    const forceExit = setTimeout(() => process.exit(1), 10000);
    forceExit.unref();
    const closeDatabase = () => db.close(() => process.exit(0));
    if (httpServer) httpServer.close(closeDatabase);
    else closeDatabase();
}

process.once('SIGTERM', () => shutdown('SIGTERM'));
process.once('SIGINT', () => shutdown('SIGINT'));
