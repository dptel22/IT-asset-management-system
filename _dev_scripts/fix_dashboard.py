import re

# 1. Update partials/sidebar.html to remove Tasks for employee
with open('templates/partials/sidebar.html', 'r') as f:
    sidebar = f.read()

sidebar = re.sub(
    r'<div class="nav-section">Tasks</div>\s*<a href="/tasks" class="nav-item">\s*<i data-lucide="check-square"></i>\s*<span>My Tasks</span>\s*</a>',
    '',
    sidebar
)
with open('templates/partials/sidebar.html', 'w') as f:
    f.write(sidebar)

# 2. Update server.js dashboard, requests, maintenance
with open('server.js', 'r') as f:
    server = f.read()

dashboard_original = """app.get('/dashboard', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') {
        return res.render('employee-dashboard.html');
    }"""
dashboard_new = """app.get('/dashboard', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') {
        const emp = await get(`SELECT id FROM employees WHERE user_id = ?`, [req.user.id]);
        const emp_id = emp ? emp.id : 'none';
        
        const my_assets = await query(`
            SELECT id, asset_tag, brand, model, status, created_at as assigned_date
            FROM assets WHERE current_owner_id = ?
        `, [emp_id]);
        
        const pending_requests = (await query(`SELECT count(*) as c FROM requests WHERE employee_id = ? AND status='pending'`, [emp_id]))[0].c;
        
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
            }
        });
    }"""
server = server.replace(dashboard_original, dashboard_new)

requests_original = """app.get('/requests', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    let sql = `
        SELECT r.*, e.name as employee_name, e.department
        FROM requests r JOIN employees e ON r.employee_id = e.id
    `;
    const params = [];
    if (statusFilter) { sql += ` WHERE r.status = ?`; params.push(statusFilter); }
    sql += ` ORDER BY r.requested_date DESC`;"""
requests_new = """app.get('/requests', requireAuth, async (req, res) => {
    const { status: statusFilter } = req.query;
    let sql = `
        SELECT r.*, e.name as employee_name, e.department
        FROM requests r JOIN employees e ON r.employee_id = e.id
    `;
    const params = [];
    if (req.user.role === 'employee') {
        const emp = await get(`SELECT id FROM employees WHERE user_id = ?`, [req.user.id]);
        sql += ` WHERE r.employee_id = ?`;
        params.push(emp ? emp.id : 'none');
        if (statusFilter) { sql += ` AND r.status = ?`; params.push(statusFilter); }
    } else {
        if (statusFilter) { sql += ` WHERE r.status = ?`; params.push(statusFilter); }
    }
    sql += ` ORDER BY r.requested_date DESC`;"""
server = server.replace(requests_original, requests_new)

maint_original = """app.get('/maintenance', requireAuth, async (req, res) => {
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
    sql += ` ORDER BY m.reported_date DESC`;"""
maint_new = """app.get('/maintenance', requireAuth, async (req, res) => {
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
    sql += ` ORDER BY m.reported_date DESC`;"""
server = server.replace(maint_original, maint_new)

with open('server.js', 'w') as f:
    f.write(server)

# 3. Update templates/employee-dashboard.html
with open('templates/employee-dashboard.html', 'r') as f:
    html = f.read()

# Header New Request -> Add Asset
html = html.replace('<button class="btn btn-primary" onclick="openModal(\'requestModal\')">\\n            <i data-lucide="plus"></i> New Request\\n          </a>', 
                    '<a href="/requests/new" class="btn btn-primary">\\n            <i data-lucide="plus"></i> Add Asset\\n          </a>')
html = html.replace('<button class="btn btn-primary" onclick="openModal(\'requestModal\')">\\n            <i data-lucide="plus"></i> New Request\\n          </button>', 
                    '<a href="/requests/new" class="btn btn-primary">\\n            <i data-lucide="plus"></i> Add Asset\\n          </a>')

# Quick actions
html = html.replace('<a href="requests.html" class="quick-action-btn">\\n            <div class="qa-icon" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">\\n              <i data-lucide="plus-circle"></i>\\n            </div>\\n            <div>\\n              <div class="qa-label">New Request</div>',
                    '<a href="/requests/new" class="quick-action-btn">\\n            <div class="qa-icon" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">\\n              <i data-lucide="plus-circle"></i>\\n            </div>\\n            <div>\\n              <div class="qa-label">Add Asset</div>')

html = html.replace('<a href="add-issue.html" class="quick-action-btn">', '<a href="/maintenance/new" class="quick-action-btn">')

html = html.replace('<a href="requests.html" class="quick-action-btn">\\n            <div class="qa-icon" style="background: rgba(34,197,94,0.1); color: var(--status-active);">\\n              <i data-lucide="history"></i>\\n            </div>\\n            <div>\\n              <div class="qa-label">My History</div>',
                    '<a href="/requests" class="quick-action-btn">\\n            <div class="qa-icon" style="background: rgba(34,197,94,0.1); color: var(--status-active);">\\n              <i data-lucide="history"></i>\\n            </div>\\n            <div>\\n              <div class="qa-label">Add Asset Requests</div>')

# Hero section stats
html = html.replace('<div class="hero-greeting">Good morning, Rith 👋</div>', '<div class="hero-greeting">Good morning, {{ employee.username }} 👋</div>')
html = html.replace('<div class="hero-sub">Software Engineer &nbsp;·&nbsp; IT Department</div>', '<div class="hero-sub">Role: {{ employee.role }}</div>')
html = html.replace('<span class="hero-tag hero-tag-ice">3 assets assigned</span>', '<span class="hero-tag hero-tag-ice">{{ stats.total_assets }} assets assigned</span>')
html = html.replace('<span class="hero-tag hero-tag-amber">1 request pending</span>', '<span class="hero-tag hero-tag-amber">{{ stats.pending_requests }} requests pending</span>')
html = html.replace('<div class="kpi-value">3</div>\\n            <div class="kpi-label">My Assets</div>', '<div class="kpi-value">{{ stats.total_assets }}</div>\\n            <div class="kpi-label">My Assets</div>')
html = html.replace('<div class="kpi-value">1</div>\\n            <div class="kpi-label">Pending Requests</div>', '<div class="kpi-value">{{ stats.pending_requests }}</div>\\n            <div class="kpi-label">Pending Requests</div>')
# Third KPI could be My Issues
html = html.replace('<div class="kpi-value">1</div>\\n            <div class="kpi-label">Warranty Expiring</div>', '<!-- Replaced KPI -->')


# Replace My Assets list
my_assets_hardcoded = """<div class="asset-row">
                <div class="asset-icon-wrap" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">
                  <i data-lucide="laptop"></i>
                </div>
                <div style="flex:1; min-width:0;">
                  <div class="asset-name">MacBook Pro 14"</div>
                  <div class="asset-meta"><span class="font-data">#LP-0421</span> · Assigned Jan 2025</div>
                </div>
                <div class="asset-status">
                  <div class="status-dot" style="background: var(--status-active);"></div>
                  <span style="color: var(--status-active); font-family: var(--font-data);">Active</span>
                </div>
              </div>
              <div class="asset-row">
                <div class="asset-icon-wrap" style="background: rgba(34,197,94,0.1); color: var(--status-active);">
                  <i data-lucide="mouse-pointer-2"></i>
                </div>
                <div style="flex:1; min-width:0;">
                  <div class="asset-name">Logitech MX Master 3</div>
                  <div class="asset-meta"><span class="font-data">#PH-0088</span> · Assigned Mar 2025</div>
                </div>
                <div class="asset-status">
                  <div class="status-dot" style="background: var(--status-active);"></div>
                  <span style="color: var(--status-active); font-family: var(--font-data);">Active</span>
                </div>
              </div>
              <div class="asset-row">
                <div class="asset-icon-wrap" style="background: rgba(245,158,11,0.1); color: var(--status-warn);">
                  <i data-lucide="smartphone"></i>
                </div>
                <div style="flex:1; min-width:0;">
                  <div class="asset-name">iPhone 14 Pro</div>
                  <div class="asset-meta"><span class="font-data">#MB-0312</span> · In maintenance since Jun 5</div>
                </div>
                <div class="asset-status">
                  <div class="status-dot" style="background: var(--status-warn);"></div>
                  <span style="color: var(--status-warn); font-family: var(--font-data);">Maint.</span>
                </div>
              </div>"""
              
my_assets_dynamic = """
              {% for asset in my_assets %}
              <div class="asset-row">
                <div class="asset-icon-wrap" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">
                  <i data-lucide="monitor"></i>
                </div>
                <div style="flex:1; min-width:0;">
                  <div class="asset-name">{{ asset.brand }} {{ asset.model }}</div>
                  <div class="asset-meta"><span class="font-data">{{ asset.asset_tag }}</span></div>
                </div>
                <div class="asset-status">
                  <div class="status-dot" style="background: var(--status-active);"></div>
                  <span style="color: var(--status-active); font-family: var(--font-data);">{{ asset.status }}</span>
                </div>
              </div>
              {% else %}
              <div class="asset-row" style="padding: 24px; text-align: center; color: var(--text-secondary);">No assets assigned to you yet.</div>
              {% endfor %}
"""
html = html.replace(my_assets_hardcoded, my_assets_dynamic)
html = html.replace('href="asset-detail.html"', 'href="/inventory"')


# Replace My Activity Feed
activity_feed_hardcoded = """<div class="feed-item">
                <div class="feed-icon" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">
                  <i data-lucide="check-circle" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">Request <span class="font-data">#RQ-0089</span> approved</div>
                  <div class="feed-meta">Monitor request approved by Admin · 2h ago</div>
                </div>
              </div>
              <div class="feed-item">
                <div class="feed-icon" style="background: rgba(245,158,11,0.1); color: var(--status-warn);">
                  <i data-lucide="wrench" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">iPhone 14 Pro sent to maintenance</div>
                  <div class="feed-meta">Asset <span class="font-data">#MB-0312</span> · Yesterday</div>
                </div>
              </div>
              <div class="feed-item">
                <div class="feed-icon" style="background: rgba(244,162,38,0.1); color: var(--accent-amber);">
                  <i data-lucide="clock" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">27" Monitor request submitted</div>
                  <div class="feed-meta">Request <span class="font-data">#RQ-0092</span> · Jun 10</div>
                </div>
              </div>
              <div class="feed-item">
                <div class="feed-icon" style="background: rgba(34,197,94,0.1); color: var(--status-active);">
                  <i data-lucide="user-check" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">MacBook Pro assigned to you</div>
                  <div class="feed-meta">Asset <span class="font-data">#LP-0421</span> · Jan 12 2025</div>
                </div>
              </div>"""

activity_feed_dynamic = """
              {% for r in my_requests %}
              <div class="feed-item">
                <div class="feed-icon" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">
                  <i data-lucide="clock" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">{{ r.request_type }} requested</div>
                  <div class="feed-meta">Status: {{ r.status }} · {{ r.requested_date }}</div>
                </div>
              </div>
              {% endfor %}
              {% for i in my_issues %}
              <div class="feed-item">
                <div class="feed-icon" style="background: rgba(245,158,11,0.1); color: var(--status-warn);">
                  <i data-lucide="alert-triangle" width="16"></i>
                </div>
                <div>
                  <div class="feed-text">Issue reported: {{ i.asset_tag }}</div>
                  <div class="feed-meta">Status: {{ i.status }} · {{ i.reported_date }}</div>
                </div>
              </div>
              {% endfor %}
"""
html = html.replace(activity_feed_hardcoded, activity_feed_dynamic)

# Also remove the hardcoded Modals at the bottom
if '<!-- Modals -->' in html:
    html = html.split('<!-- Modals -->')[0] + '\\n</body>\\n</html>'

with open('templates/employee-dashboard.html', 'w') as f:
    f.write(html)
