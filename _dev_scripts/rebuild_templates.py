#!/usr/bin/env python3
"""
Rebuild CognixAsset templates from UI design files.
Copies design HTML files and injects Nunjucks template variables.
"""
import re, os, shutil

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "ui", "ux")
TPL_DIR = os.path.join(BASE_DIR, "templates")

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Written: {os.path.basename(path)}")

def fix_nav_links(html):
    """Update navigation hrefs to match server routes."""
    replacements = {
        'href="dashboard.html"': 'href="/dashboard"',
        'href="inventory.html"': 'href="/inventory"',
        'href="asset-detail.html"': 'href="/asset-detail"',
        'href="asset-assignment.html"': 'href="/asset-assignment"',
        'href="employee-directory.html"': 'href="/employees"',
        'href="employee-profile.html"': 'href="/employee-profile"',
        'href="transfers.html"': 'href="/transfers"',
        'href="maintenance.html"': 'href="/maintenance"',
        'href="requests.html"': 'href="/requests"',
        'href="reports.html"': 'href="/reports"',
        'href="notifications.html"': 'href="/notifications"',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html

def fix_sidebar_user(html):
    """Replace static sidebar user info with Nunjucks variables."""
    # Replace avatar initials - use substring approach compatible with Nunjucks
    html = re.sub(
        r'(<div class="avatar">)[A-Z]+(<\/div>)',
        r'\1{{ user.employee.name | truncate(2, false, "") | upper }}\2',
        html
    )
    # Replace user name
    html = re.sub(
        r'(<span class="user-name">)[^<]*(</span>)',
        r'\1{{ user.employee.name }}\2',
        html
    )
    # Replace role pill
    html = re.sub(
        r'(<span class="role-pill">)[^<]*(</span>)',
        r'\1{{ user.role | replace("_", " ") | title }}\2',
        html
    )
    return html

def fix_topbar_date(html):
    """Replace static date with dynamic JS date."""
    html = re.sub(
        r'<span class="top-bar-date">[^<]*</span>',
        '<span class="top-bar-date" id="current-date"></span>',
        html
    )
    return html

def inject_date_script(html):
    """Inject a small script to set the date dynamically."""
    date_script = """
<script>
  (function() {
    var el = document.getElementById('current-date');
    if (el) {
      var now = new Date();
      el.textContent = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }).toUpperCase();
    }
  })();
</script>"""
    html = html.replace('</body>', date_script + '\n</body>')
    return html

def wrap_inline_scripts(html):
    """Wrap inline <script> blocks in raw tags to avoid Nunjucks parsing JS."""
    # We need to wrap all <script> blocks that don't contain Nunjucks with {% raw %}
    # But keep any Nunjucks script blocks unwrapped
    # Strategy: wrap everything EXCEPT our custom report_data block
    
    def wrap_script(match):
        full = match.group(0)
        # Don't wrap if it's already a Nunjucks template block or our injected data
        if 'window.REPORT_DATA' in full or 'lucide.createIcons' in full:
            return full
        # Wrap the content between script tags
        open_tag = re.match(r'<script[^>]*>', full).group(0)
        close_tag = '</script>'
        inner = full[len(open_tag):-len(close_tag)]
        # Only wrap if there's content and it's minified JS (long lines)
        if len(inner) > 500:
            return open_tag + '\n{% raw %}\n' + inner + '\n{% endraw %}\n' + close_tag
        return full
    
    html = re.sub(r'<script[^>]*>.*?</script>', wrap_script, html, flags=re.DOTALL)
    return html

# ============================================================
# 1. DASHBOARD
# ============================================================
def build_dashboard():
    html = read(f"{UI_DIR}/dashboard.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    # Replace static KPI values with Nunjucks variables
    html = re.sub(r'(<div class="kpi-value"[^>]*>)\s*165\s*(</div>)', r'\1{{ stats.total_assets }}\2', html)
    html = re.sub(r'(<div class="kpi-value"[^>]*>)\s*98\s*(</div>)', r'\1{{ stats.assigned }}\2', html)
    html = re.sub(r'(<div class="kpi-value"[^>]*>)\s*51\s*(</div>)', r'\1{{ stats.available }}\2', html)
    html = re.sub(r'(<div class="kpi-value"[^>]*>)\s*16\s*(</div>)', r'\1{{ stats.maintenance }}\2', html)
    html = re.sub(r'(<div class="metric-value">)\s*12\s*(</div>)', r'\1{{ stats.warranty_expiring }}\2', html, count=1)
    html = re.sub(r'(<div class="metric-value">)\s*8\s*(</div>)', r'\1{{ stats.pending_requests }}\2', html, count=1)

    write(f"{TPL_DIR}/dashboard.html", html)

# ============================================================
# 2. INVENTORY
# ============================================================
def build_inventory():
    html = read(f"{UI_DIR}/inventory.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_tbody = """{% for asset in assets %}
              <tr>
                <td>
                  <div style="font-family: var(--font-data); font-size: 13px; color: var(--accent-amber);">{{ asset.tag }}</div>
                  <div style="font-size: 13px;">{{ asset.name }}</div>
                </td>
                <td><span class="badge badge-neutral">{{ asset.category }}</span></td>
                <td>{{ asset.department }}</td>
                <td>
                  {% if asset.status == 'assigned' %}<span class="badge badge-active">Assigned</span>
                  {% elif asset.status == 'available' %}<span class="badge badge-neutral">Available</span>
                  {% elif asset.status == 'maintenance' %}<span class="badge badge-warn">Maintenance</span>
                  {% else %}<span class="badge badge-neutral">{{ asset.status | title }}</span>
                  {% endif %}
                </td>
                <td>{{ asset.assigned_employee.name if asset.assigned_employee else '—' }}</td>
                <td>
                  <div style="display:flex; gap:8px;">
                    <a href="/asset-detail?id={{ asset.id }}" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px;">View</a>
                    <form method="POST" action="/api/assets/{{ asset.id }}/archive" style="display:inline;" onsubmit="return confirm('Archive this asset?')">
                      <input type="hidden" name="reason" value="Manual Archive">
                      <button type="submit" class="btn" style="padding: 4px 10px; font-size: 12px; background: rgba(239,68,68,0.1); color: var(--status-critical); border: 1px solid rgba(239,68,68,0.3);">Archive</button>
                    </form>
                  </div>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align: center; color: var(--text-secondary); padding: 32px;">No assets found</td></tr>
              {% endfor %}"""

    html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n              {nunjucks_tbody}\n            </tbody>', html, flags=re.DOTALL)
    write(f"{TPL_DIR}/inventory.html", html)

# ============================================================
# 3. EMPLOYEES
# ============================================================
def build_employees():
    html = read(f"{UI_DIR}/employee-directory.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_tbody = """{% for emp in employees %}
              <tr>
                <td>
                  <div style="display:flex; align-items:center; gap:12px;">
                    <div class="avatar">{{ emp.name | truncate(2, false, "") | upper }}</div>
                    <div>
                      <div style="font-weight:500;">{{ emp.name }}</div>
                      <div style="font-size:12px; color:var(--text-secondary);">{{ emp.email }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ emp.department }}</td>
                <td>{{ emp.location }}</td>
                <td><span class="badge badge-neutral">{{ emp.assets_count }} assets</span></td>
                <td>
                  {% if emp.status == 'active' %}<span class="badge badge-active">Active</span>
                  {% else %}<span class="badge badge-neutral">{{ emp.status | title }}</span>
                  {% endif %}
                </td>
                <td><a href="/employee-profile?id={{ emp.id }}" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px;">View Profile</a></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align:center; color:var(--text-secondary); padding:32px;">No employees found</td></tr>
              {% endfor %}"""

    html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n              {nunjucks_tbody}\n            </tbody>', html, flags=re.DOTALL)
    write(f"{TPL_DIR}/employee-directory.html", html)

# ============================================================
# 4. MAINTENANCE
# ============================================================
def build_maintenance():
    html = read(f"{UI_DIR}/maintenance.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_tbody = """{% for m in maintenance %}
              <tr>
                <td>
                  <div style="font-family:var(--font-data); font-size:13px; color:var(--accent-amber);">{{ m.asset_tag }}</div>
                  <div style="font-size:13px;">{{ m.brand }} {{ m.model }}</div>
                </td>
                <td>{{ m.issue_description }}</td>
                <td>{{ m.reported_by_name or '—' }}</td>
                <td style="font-family:var(--font-data); font-size:12px;">{{ m.reported_date.split('T')[0] if m.reported_date else '—' }}</td>
                <td>
                  {% if m.status == 'completed' %}<span class="badge badge-active">Completed</span>
                  {% elif m.status == 'in_progress' %}<span class="badge badge-warn">In Progress</span>
                  {% elif m.status == 'awaiting_parts' %}<span class="badge badge-warn">Awaiting Parts</span>
                  {% else %}<span class="badge badge-neutral">{{ m.status | title }}</span>
                  {% endif %}
                </td>
                <td><button class="btn btn-outline" style="padding:4px 10px; font-size:12px;"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align:center; color:var(--text-secondary); padding:32px;">No maintenance records found</td></tr>
              {% endfor %}"""

    html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n              {nunjucks_tbody}\n            </tbody>', html, flags=re.DOTALL)
    write(f"{TPL_DIR}/maintenance.html", html)

# ============================================================
# 5. REQUESTS
# ============================================================
def build_requests():
    html = read(f"{UI_DIR}/requests.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_tbody = """{% for r in requests %}
              <tr>
                <td style="font-family:var(--font-data); font-size:13px; color:var(--accent-amber);">REQ-{{ r.id | truncate(6, false, "") | upper }}</td>
                <td>
                  <div style="font-weight:500;">{{ r.employee_name }}</div>
                  <div style="font-size:12px; color:var(--text-secondary);">{{ r.department }}</div>
                </td>
                <td>{{ r.request_type }}</td>
                <td>{{ r.category }}</td>
                <td style="font-family:var(--font-data); font-size:12px;">{{ r.requested_date.split('T')[0] if r.requested_date else '—' }}</td>
                <td>
                  {% if r.status == 'approved' %}<span class="badge badge-active">Approved</span>
                  {% elif r.status == 'pending' %}<span class="badge badge-warn">Pending</span>
                  {% elif r.status == 'rejected' %}<span class="badge badge-critical">Rejected</span>
                  {% else %}<span class="badge badge-neutral">{{ r.status | title }}</span>
                  {% endif %}
                </td>
                <td><button class="btn btn-outline" style="padding:4px 10px; font-size:12px;"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="7" style="text-align:center; color:var(--text-secondary); padding:32px;">No requests found</td></tr>
              {% endfor %}"""

    html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n              {nunjucks_tbody}\n            </tbody>', html, flags=re.DOTALL)
    write(f"{TPL_DIR}/requests.html", html)

# ============================================================
# 6. TRANSFERS
# ============================================================
def build_transfers():
    html = read(f"{UI_DIR}/transfers.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_tbody = """{% for t in transfers %}
              <tr>
                <td>
                  <div style="font-family:var(--font-data); font-size:13px; color:var(--accent-amber);">{{ t.asset_tag }}</div>
                  <div style="font-size:13px;">{{ t.brand }} {{ t.model }}</div>
                </td>
                <td>{{ t.from_employee or 'Unassigned' }}</td>
                <td>{{ t.to_employee }}</td>
                <td style="font-family:var(--font-data); font-size:12px;">{{ t.request_date.split('T')[0] if t.request_date else '—' }}</td>
                <td>
                  {% if t.status == 'completed' %}<span class="badge badge-active">Completed</span>
                  {% elif t.status == 'pending' %}<span class="badge badge-warn">Pending</span>
                  {% elif t.status == 'rejected' %}<span class="badge badge-critical">Rejected</span>
                  {% else %}<span class="badge badge-neutral">{{ t.status | title }}</span>
                  {% endif %}
                </td>
                <td><button class="btn btn-outline" style="padding:4px 10px; font-size:12px;"><i data-lucide="more-vertical"></i></button></td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="text-align:center; color:var(--text-secondary); padding:32px;">No transfers found</td></tr>
              {% endfor %}"""

    html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n              {nunjucks_tbody}\n            </tbody>', html, flags=re.DOTALL)
    write(f"{TPL_DIR}/transfers.html", html)

# ============================================================
# 7. NOTIFICATIONS
# ============================================================
def build_notifications():
    html = read(f"{UI_DIR}/notifications.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    nunjucks_list = """{% for n in notifications %}
              <div class="notification-item" style="padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; gap: 16px; align-items: flex-start; {% if not n.is_read %}background: rgba(244,162,38,0.03);{% endif %}">
                <div style="width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink:0; background: {% if n.type == 'critical' %}var(--status-critical){% elif n.type == 'warning' %}var(--status-warn){% elif n.type == 'success' %}var(--status-active){% else %}var(--accent-ice){% endif %}"></div>
                <div style="flex:1;">
                  <div style="font-weight: 500; font-size: 14px;">{{ n.title }}</div>
                  <div style="color: var(--text-secondary); font-size: 13px; margin-top: 4px;">{{ n.message }}</div>
                  <div style="font-family: var(--font-data); font-size: 11px; color: var(--text-disabled); margin-top: 8px;">{{ n.created_at.split('T')[0] if n.created_at else '' }}</div>
                </div>
                {% if not n.is_read %}<span class="badge badge-warn" style="flex-shrink:0;">New</span>{% endif %}
              </div>
              {% else %}
              <div style="padding:48px; text-align:center; color: var(--text-secondary);">No notifications</div>
              {% endfor %}"""

    # Replace static notification items with Nunjucks loop
    html = re.sub(
        r'(<div class="notification-list"[^>]*>).*?(</div>\s*\n\s*</div>\s*\n\s*</main)',
        lambda m: m.group(1) + '\n' + nunjucks_list + '\n' + m.group(2),
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL_DIR}/notifications.html", html)

# ============================================================
# 8. REPORTS
# ============================================================
def build_reports():
    html = read(f"{UI_DIR}/reports.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)

    # Inject chart data via inline script using Nunjucks (NOT wrapped in raw)
    chart_script = """
<script>
window.REPORT_DATA = {
  statusCounts: {{ statusCounts | dump | safe }},
  categoryCounts: {{ categoryCounts | dump | safe }},
  totalCost: {{ totalCost }}
};
</script>"""
    html = html.replace('</head>', chart_script + '\n</head>')

    write(f"{TPL_DIR}/reports.html", html)

# ============================================================
# 9. INDEX (Login)
# ============================================================
def build_index():
    html = read(f"{UI_DIR}/index.html")
    html = wrap_inline_scripts(html)
    # Replace the login form action and remove onsubmit
    html = re.sub(
        r'<form[^>]*>',
        '<form method="POST" action="/login">',
        html, count=1
    )
    # Change email input to username
    html = re.sub(
        r'<i data-lucide="mail"([^>]*)></i>\s*<input type="email"[^>]*>',
        r'<i data-lucide="user"\1></i>\n              <input type="text" name="username" class="form-input" placeholder="admin" required>',
        html
    )
    # Remove the password step for local username-only login.
    html = re.sub(
        r'\s*<div class="form-group fade-up delay-4">\s*<div class="input-wrapper">\s*<i data-lucide="key"[^>]*></i>\s*<input type="password"[^>]*>\s*</div>\s*</div>',
        '',
        html,
        count=1,
        flags=re.DOTALL
    )
    html = re.sub(
        r'\s*<div class="form-options fade-up delay-5">.*?</div>',
        '',
        html,
        count=1,
        flags=re.DOTALL
    )
    html = html.replace('Enter your credentials to continue', 'Enter a username to continue')
    html = html.replace('SECURE SSO ENABLED', 'LOCAL USERNAME LOGIN')
    html = html.replace('data-lucide="lock"', 'data-lucide="user-check"')
    
    # Add error display before submit button
    error_block = """{% if error %}
          <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: var(--status-critical); padding: 12px 16px; border-radius: var(--radius-input); font-size: 14px; margin-bottom: 16px;">
            {{ error }}
          </div>
          {% endif %}"""
    html = re.sub(
        r'(<button[^>]*type="submit")',
        error_block + r'\1',
        html, count=1
    )
    write(f"{TPL_DIR}/index.html", html)

# ============================================================
# 10. ASSET ASSIGNMENT
# ============================================================
def build_asset_assignment():
    html = read(f"{UI_DIR}/asset-assignment.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)
    write(f"{TPL_DIR}/asset-assignment.html", html)

# ============================================================
# 11. ASSET DETAIL
# ============================================================
def build_asset_detail():
    html = read(f"{UI_DIR}/asset-detail.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)
    write(f"{TPL_DIR}/asset-detail.html", html)

# ============================================================
# 12. EMPLOYEE PROFILE
# ============================================================
def build_employee_profile():
    html = read(f"{UI_DIR}/employee-profile.html")
    html = fix_nav_links(html)
    html = fix_sidebar_user(html)
    html = fix_topbar_date(html)
    html = wrap_inline_scripts(html)
    html = inject_date_script(html)
    write(f"{TPL_DIR}/employee-profile.html", html)

# ============================================================
# Run all builders
# ============================================================
if __name__ == "__main__":
    print("Rebuilding CognixAsset templates from UI designs...\n")
    build_dashboard()
    build_inventory()
    build_employees()
    build_maintenance()
    build_requests()
    build_transfers()
    build_notifications()
    build_reports()
    build_index()
    build_asset_assignment()
    build_asset_detail()
    build_employee_profile()
    print("\n✅ All templates rebuilt successfully!")
