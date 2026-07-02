const express = require('express');
const nunjucks = require('nunjucks');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { initDB, query, get, run } = require('./db');

const app = express();
const JWT_SECRET = 'super-secret-key-for-local-demo';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use('/static', express.static(path.join(__dirname, 'static')));

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
njEnv.addFilter('shortid', (val) => {
    if (!val) return '—';
    return String(val).replace(/-/g, '').substring(0, 8).toUpperCase();
});

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

// ============================================================
// Auth Routes
// ============================================================
app.get('/', (req, res) => res.redirect('/dashboard'));

app.get('/login', (req, res) => {
    res.render('index.html', { error: req.query.error });
});

app.post('/login', async (req, res) => {
    const username = String(req.body.username || '').trim();
    try {
        const user = await get(`SELECT * FROM users WHERE username = ?`, [username]);
        if (!user) return res.render('index.html', { error: 'Unknown username' });
        const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, { expiresIn: '24h' });
        res.cookie('token', token, { httpOnly: true });
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
        return res.render('employee-dashboard.html');
    }
    const stats = {};
    stats.total_assets    = (await get(`SELECT count(*) as c FROM assets`)).c;
    stats.assigned        = (await get(`SELECT count(*) as c FROM assets WHERE status='assigned'`)).c;
    stats.available       = (await get(`SELECT count(*) as c FROM assets WHERE status='available'`)).c;
    stats.maintenance     = (await get(`SELECT count(*) as c FROM assets WHERE status='maintenance'`)).c;
    stats.pending_requests= (await get(`SELECT count(*) as c FROM requests WHERE status='pending'`)).c;
    stats.warranty_expiring = (await get(
        `SELECT count(*) as c FROM assets WHERE warranty_date BETWEEN date('now') AND date('now', '+30 days')`
    )).c;

    const recent_assets = await query(`
        SELECT a.asset_tag, a.brand, a.model, a.status, a.id, e.name as assigned_to_name
        FROM assets a LEFT JOIN employees e ON a.current_owner_id = e.id
        ORDER BY a.created_at DESC LIMIT 5
    `);
    const recent_requests = await query(`
        SELECT r.id, r.request_type, r.category, r.status, r.requested_date, e.name as employee_name
        FROM requests r JOIN employees e ON r.employee_id = e.id
        WHERE r.status = 'pending'
        ORDER BY r.requested_date DESC LIMIT 5
    `);

    res.render('dashboard.html', { stats, recent_assets, recent_requests });
});

// ============================================================
// Inventory & Asset CRUD
// ============================================================
app.get('/inventory', requireAuth, async (req, res) => {
    const { search, category, status, department, location } = req.query;

    let sql = `
        SELECT a.*, e.name as assigned_to_name
        FROM assets a LEFT JOIN employees e ON a.current_owner_id = e.id
        WHERE 1=1
    `;
    const params = [];
    
    if (req.user.role === 'employee') {
        sql += ` AND a.current_owner_id = ?`;
        params.push(req.employee.id);
    } else if (req.user.role === 'admin') {
        sql += ` AND a.department = ?`;
        params.push(req.employee.department);
    }
    if (search) {
        sql += ` AND (a.brand LIKE ? OR a.model LIKE ? OR a.asset_tag LIKE ?)`;
        params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (category)   { sql += ` AND a.category = ?`;   params.push(category); }
    if (status)     { sql += ` AND a.status = ?`;     params.push(status); }
    if (department) { sql += ` AND a.department = ?`; params.push(department); }
    if (location)   { sql += ` AND a.location = ?`;   params.push(location); }
    sql += ` ORDER BY a.created_at DESC`;

    const rawAssets = await query(sql, params);
    const assets = rawAssets.map(a => ({
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

    res.render('inventory.html', {
        assets,
        filters: { search: search || '', category: category || '', status: status || '', department: department || '', location: location || '' },
        categories,
        departments,
        locations
    });
});

// Add Asset form
app.get('/assets/new', requireAuth, (req, res) => {
    res.render('assets-new.html', { error: null, values: {} });
});

// Create Asset
app.post('/assets', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    let { 
        asset_tag, brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
        sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
        system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
        network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege
    } = req.body;
    
    asset_tag = asset_tag ? asset_tag.trim() : '';
    serial_number = serial_number ? serial_number.trim() : '';

    if (!monitor_make || !monitor_serial_no || !asset_owner_pl_no || !asset_usage_status || !in_warranty_status || !serial_number) {
        return res.render('assets-new.html', { error: 'Please fill out all mandatory fields.', values: req.body });
    }

    try {
        if (!asset_tag) {
            const last = await get(`SELECT asset_tag FROM assets WHERE asset_tag LIKE 'AST-%' ORDER BY CAST(SUBSTR(asset_tag, 5) AS INTEGER) DESC LIMIT 1`);
            const num = last ? parseInt(last.asset_tag.replace('AST-', ''), 10) : 999;
            asset_tag = `AST-${num + 1}`;
        } else {
            const existingTag = await get(`SELECT id FROM assets WHERE asset_tag = ?`, [asset_tag]);
            if (existingTag) {
                return res.render('assets-new.html', { error: 'Asset tag already exists. Leave it blank to auto-generate one, or enter a different tag.', values: req.body });
            }
        }
        
        if (serial_number) {
            const existingSerial = await get(`SELECT id FROM assets WHERE serial_number = ?`, [serial_number]);
            if (existingSerial) {
                return res.render('assets-new.html', { error: 'Serial number already exists. Please enter a different serial number.', values: req.body });
            }
        }

        const id = uuidv4();
        await run(
            `INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?)`,
            [id, asset_tag, brand, model, serial_number, category,
             purchase_date || null, warranty_date || null,
             parseFloat(purchase_cost) || 0, department, location, status || 'available',
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege]
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
        res.render('assets-new.html', { error: errorMsg, values: req.body });
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
    
    if (!monitor_make || !monitor_serial_no || !asset_owner_pl_no || !asset_usage_status || !in_warranty_status || !serial_number) {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        return res.render('assets-edit.html', { asset, error: 'Please fill out all mandatory fields.' });
    }

    try {
        await run(
            `UPDATE assets SET brand=?, model=?, serial_number=?, category=?, department=?, location=?,
             purchase_date=?, warranty_date=?, purchase_cost=?, status=?,
             sl_no=?, monitor_make=?, monitor_serial_no=?, asset_owner_pl_no=?, asset_usage_status=?, in_warranty_status=?,
             system_serial_no=?, host_name=?, group_name=?, division=?, user_name=?, designation=?, ip_address=?, mac_address=?,
             network_type=?, drona_domain=?, os_version=?, antivirus_status=?, usb_status=?, admin_privilege=?
             WHERE id=?`,
            [brand, model, serial_number, category, department, location,
             purchase_date || null, warranty_date || null, parseFloat(purchase_cost) || 0, status,
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
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        if (!asset) return res.status(404).send('Not found');
        await run(
            `INSERT INTO asset_archive (id, original_asset_id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status, archived_by, reason,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?)`,
            [uuidv4(), asset.id, asset.asset_tag, asset.brand, asset.model, asset.serial_number,
             asset.category, asset.purchase_date, asset.warranty_date, asset.purchase_cost,
             asset.department, asset.location, asset.status, req.user.id, reason || 'Manual Archive',
             asset.sl_no, asset.monitor_make, asset.monitor_serial_no, asset.asset_owner_pl_no, asset.asset_usage_status, asset.in_warranty_status,
             asset.system_serial_no, asset.host_name, asset.group_name, asset.division, asset.user_name, asset.designation, asset.ip_address, asset.mac_address,
             asset.network_type, asset.drona_domain, asset.os_version, asset.antivirus_status, asset.usb_status, asset.admin_privilege]
        );
        await run(`DELETE FROM maintenance WHERE asset_id = ?`, [req.params.id]);
        await run(`DELETE FROM transfers WHERE asset_id = ?`, [req.params.id]);
        await run(`DELETE FROM assets WHERE id = ?`, [req.params.id]);
        res.redirect('/inventory');
    } catch (err) {
        res.status(500).send('Error archiving asset');
    }
});
// ============================================================
// Asset Assignment
// ============================================================
app.get('/asset-assignment', requireAuth, async (req, res) => {
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
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [asset_id]);
        if (!asset) throw new Error('Asset not found');
        if (asset.status !== 'available') throw new Error(`Asset is currently "${asset.status}" and cannot be assigned`);
        const employee = await get(`SELECT * FROM employees WHERE id = ?`, [employee_id]);
        if (!employee) throw new Error('Employee not found');

        await run(`UPDATE assets SET current_owner_id = ?, status = 'assigned' WHERE id = ?`, [employee_id, asset_id]);
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), asset_id, 'Assigned', `Assigned to ${employee.name}.`, req.user.id]
        );
        await run(
            `INSERT INTO transfers (id, asset_id, from_employee_id, to_employee_id, requested_by, approved_by, status, notes) VALUES (?,?,?,?,?,?,?,?)`,
            [uuidv4(), asset_id, null, employee_id, req.user.id, req.user.id, 'completed', `Initial assignment to ${employee.name}`]
        );
        res.redirect('/inventory?success=Asset+assigned+successfully');
    } catch (err) {
        res.redirect(`/asset-assignment?asset_id=${asset_id || ''}&error=${encodeURIComponent(err.message)}`);
    }
});

// ============================================================
// Employees
// ============================================================
app.get('/employees/new', requireAuth, requireAdmin, (req, res) => {
    res.render('add-user.html', { error: null });
});

app.get('/users/new', requireAuth, requireAdmin, (req, res) => {
    res.redirect('/employees/new');
});

app.post('/employees', requireAuth, requireAdmin, async (req, res) => {
    let { name, email, department, role, location, phone, designation, join_date, manager_id } = req.body;
    location = location || "Head Office";
    try {
        if (!name || !email || !department || !role) {
            return res.render('add-user.html', { error: 'Please fill all mandatory fields' });
        }
        
        // Ensure email isn't used
        const existingEmp = await get(`SELECT id FROM employees WHERE email = ?`, [email]);
        if (existingEmp) return res.render('add-user.html', { error: 'Email already exists' });
        
        // The username will just be the prefix of email
        const username = email.split('@')[0];
        
        // See if username is taken, append random if so
        let finalUsername = username;
        let existingUser = await get(`SELECT id FROM users WHERE username = ?`, [finalUsername]);
        if (existingUser) {
            finalUsername = username + Math.floor(Math.random() * 1000);
        }

        const user_id = uuidv4();
        await run(`INSERT INTO users (id, username, password, role) VALUES (?, ?, 'Welcome123!', ?)`, [user_id, finalUsername, role]);
        
        const emp_id = uuidv4();
        await run(`INSERT INTO employees (id, user_id, name, email, department, location) VALUES (?, ?, ?, ?, ?, ?)`, 
                  [emp_id, user_id, name, email, department, location]);
                  
        res.redirect('/employees');
    } catch (err) {
        res.render('add-user.html', { error: err.message });
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
    if (statusFilter) { sql += ` WHERE m.status = ?`; params.push(statusFilter); }
    sql += ` ORDER BY m.reported_date DESC`;

    const maintenance = await query(sql, params);
    const all_assets = await query(`SELECT id, asset_tag, brand, model FROM assets ORDER BY asset_tag`);
    res.render('maintenance.html', { maintenance, all_assets, statusFilter: statusFilter || '' });
});

app.post('/maintenance', requireAuth, async (req, res) => {
    const { asset_id, issue_description, status } = req.body;
    try {
        const ticketStatus = status || 'pending';
        await run(
            `INSERT INTO maintenance (id, asset_id, issue_description, status, reported_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), asset_id, issue_description, ticketStatus, req.user.id]
        );
        if (ticketStatus !== 'completed') {
            await run(`UPDATE assets SET status = 'maintenance' WHERE id = ?`, [asset_id]);
        }
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), asset_id, 'Maintenance Start', `Ticket created: ${issue_description}`, req.user.id]
        );
        res.redirect('/maintenance');
    } catch (err) {
        res.redirect(`/maintenance?error=${encodeURIComponent(err.message)}`);
    }
});

app.post('/maintenance/:id/status', requireAuth, async (req, res) => {
    const { status } = req.body;
    try {
        const ticket = await get(`SELECT * FROM maintenance WHERE id = ?`, [req.params.id]);
        if (!ticket) return res.status(404).send('Ticket not found');
        await run(
            `UPDATE maintenance SET status = ?,
             resolved_date = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE resolved_date END
             WHERE id = ?`,
            [status, status, req.params.id]
        );
        if (status === 'completed') {
            await run(`UPDATE assets SET status = 'available' WHERE id = ? AND status = 'maintenance'`, [ticket.asset_id]);
            await run(
                `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
                [uuidv4(), ticket.asset_id, 'Maintenance End', 'Maintenance completed, asset returned to available.', req.user.id]
            );
        }
        res.redirect('/maintenance');
    } catch (err) {
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
            `INSERT INTO approvals (id, request_id, approver_id, status) VALUES (?, ?, null, 'pending')`,
            [uuidv4(), reqId]
        );
        
        return res.render('add-asset.html', { success: 'Asset request submitted successfully.' });
    } catch (err) {
        return res.render('add-asset.html', { error: err.message });
    }
});
app.get('/requests', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    let sql = `
        SELECT r.*, e.name as employee_name, e.department
        FROM requests r JOIN employees e ON r.employee_id = e.id
    `;
    const params = [];
    if (statusFilter) { sql += ` WHERE r.status = ?`; params.push(statusFilter); }
    sql += ` ORDER BY r.requested_date DESC`;
    const requests = await query(sql, params);
    res.render('requests.html', { requests, statusFilter: statusFilter || '' });
});

app.post('/requests/:id/approve', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    await run(
        `UPDATE requests SET status='approved', decided_by=?, decision_date=CURRENT_TIMESTAMP WHERE id=?`,
        [req.user.id, req.params.id]
    );
    res.render('add-asset.html', { error: null });
});

app.post('/requests/:id/reject', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    await run(
        `UPDATE requests SET status='rejected', decided_by=?, decision_date=CURRENT_TIMESTAMP WHERE id=?`,
        [req.user.id, req.params.id]
    );
    res.render('add-asset.html', { error: null });
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
    if (statusFilter) { sql += ` WHERE t.status = ?`; params.push(statusFilter); }
    sql += ` ORDER BY t.request_date DESC`;

    const transfers = await query(sql, params);
    const employees = await query(`SELECT id, name, department FROM employees WHERE status='active' ORDER BY name`);
    const assets = await query(`SELECT id, asset_tag, brand, model FROM assets WHERE status='assigned' ORDER BY asset_tag`);
    res.render('transfers.html', { transfers, employees, assets, statusFilter: statusFilter || '' });
});

app.post('/transfers', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { asset_id, to_employee_id, notes } = req.body;
    try {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [asset_id]);
        if (!asset) throw new Error('Asset not found');
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
        const transfer = await get(`SELECT * FROM transfers WHERE id = ?`, [req.params.id]);
        if (!transfer) return res.status(404).send('Not found');
        await run(
            `UPDATE transfers SET status='completed', approved_by=?, completion_date=CURRENT_TIMESTAMP WHERE id=?`,
            [req.user.id, req.params.id]
        );
        await run(`UPDATE assets SET current_owner_id=? WHERE id=?`, [transfer.to_employee_id, transfer.asset_id]);
        const toEmp = await get(`SELECT name FROM employees WHERE id=?`, [transfer.to_employee_id]);
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), transfer.asset_id, 'Reassigned', `Transferred to ${toEmp ? toEmp.name : 'new employee'}.`, req.user.id]
        );
        res.redirect('/transfers');
    } catch (err) {
        res.redirect(`/transfers?error=${encodeURIComponent(err.message)}`);
    }
});

app.post('/transfers/:id/reject', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    await run(
        `UPDATE transfers SET status='rejected', approved_by=?, completion_date=CURRENT_TIMESTAMP WHERE id=?`,
        [req.user.id, req.params.id]
    );
    res.redirect('/transfers');
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
app.get('/reports', requireAuth, async (req, res) => {
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

// ============================================================
// Redirect helpers for old-style links
// ============================================================
app.get('/asset-detail', requireAuth, (req, res) => {
    if (req.query.id) return res.redirect(`/assets/${req.query.id}`);
    res.redirect('/inventory');
});

app.get('/requests/new', requireAuth, (req, res) => {
    res.render('add-asset.html', { error: null });
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

app.get('/:page', requireAuth, (req, res) => {
    const page = req.params.page;
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
const HOST = process.env.HOST || '127.0.0.1';
initDB()
    .then(() => {
        const server = app.listen(PORT, HOST);
        server.on('listening', () => console.log(`Server is running on http://${HOST}:${PORT}`));
        server.on('error', (err) => {
            console.error('Failed to start server:', err.message);
            process.exit(1);
        });
    })
    .catch(err => {
        console.error('Failed to initialize local database:', err);
        process.exit(1);
    });
