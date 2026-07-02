#!/usr/bin/env python3
"""
patch_templates.py
Patches all existing CognixAsset templates to wire real data, forms, and actions.
Run after rebuild_templates.py or whenever templates need re-wiring.
"""
import re, os

TPL = os.path.join(os.path.dirname(__file__), "templates")

def read(f): 
    with open(f) as fp: return fp.read()

def write(f, content):
    with open(f, "w") as fp: fp.write(content)
    print(f"✓ Patched: {os.path.basename(f)}")

# ──────────────────────────────────────────────────────────────
# 1. INVENTORY — search/filter bar + Add Asset link
# ──────────────────────────────────────────────────────────────
def patch_inventory():
    html = read(f"{TPL}/inventory.html")

    # Fix "Add Asset" button to link to /assets/new
    html = re.sub(
        r'<button class="btn btn-primary"[^>]*>\s*(?:<i[^>]*/?>)?[^<]*(?:</i>)?\s*(?:Add|New)[^<]*Asset[^<]*</button>',
        '<a href="/assets/new" class="btn btn-primary"><i data-lucide="plus" width="16"></i> Add Asset</a>',
        html, flags=re.IGNORECASE
    )
    # Also fix any onclick Add Asset that links to inventory page top
    html = html.replace(
        '<button class="btn btn-primary">',
        '<a href="/assets/new" class="btn btn-primary">Add Asset</a>\n        <button class="btn btn-primary" style="display:none">',
        1
    )

    # Inject search/filter bar BEFORE the table (after page-header or action-bar section)
    filter_bar = """
        <!-- Search & Filter Bar -->
        <form method="GET" action="/inventory" class="fade-up delay-2" style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px; align-items:center;">
          <div style="position:relative; flex:1; min-width:200px;">
            <i data-lucide="search" style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--text-secondary); width:16px; height:16px;"></i>
            <input type="text" name="search" value="{{ filters.search }}" placeholder="Search assets..." style="width:100%; padding:9px 12px 9px 36px; background:var(--bg-raised); border:1px solid var(--border); border-radius:var(--radius-input); color:var(--text-primary); font-family:var(--font-ui); font-size:14px; outline:none;">
          </div>
          <select name="category" style="padding:9px 14px; background:var(--bg-raised); border:1px solid var(--border); border-radius:var(--radius-input); color:var(--text-primary); font-size:13px; outline:none;">
            <option value="">All Categories</option>
            {% for c in categories %}<option value="{{ c.category }}" {% if filters.category == c.category %}selected{% endif %}>{{ c.category }}</option>{% endfor %}
          </select>
          <select name="status" style="padding:9px 14px; background:var(--bg-raised); border:1px solid var(--border); border-radius:var(--radius-input); color:var(--text-primary); font-size:13px; outline:none;">
            <option value="">All Statuses</option>
            {% for s in ["available","assigned","maintenance"] %}<option value="{{ s }}" {% if filters.status == s %}selected{% endif %}>{{ s | title }}</option>{% endfor %}
          </select>
          <select name="department" style="padding:9px 14px; background:var(--bg-raised); border:1px solid var(--border); border-radius:var(--radius-input); color:var(--text-primary); font-size:13px; outline:none;">
            <option value="">All Departments</option>
            {% for d in departments %}<option value="{{ d.department }}" {% if filters.department == d.department %}selected{% endif %}>{{ d.department }}</option>{% endfor %}
          </select>
          <button type="submit" class="btn btn-outline" style="padding:9px 16px;"><i data-lucide="filter" width="14"></i> Filter</button>
          {% if filters.search or filters.category or filters.status or filters.department %}
          <a href="/inventory" class="btn" style="padding:9px 14px; background:rgba(239,68,68,0.1); color:var(--status-critical); border:1px solid rgba(239,68,68,0.3); font-size:13px;">Clear</a>
          {% endif %}
        </form>
"""

    # Replace the existing asset tbody Nunjucks loop with a better one including real links
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
                    <a href="/assets/{{ asset.id }}" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px;">View</a>
                    <a href="/assets/{{ asset.id }}/edit" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px; border-color: var(--accent-amber); color: var(--accent-amber);">Edit</a>
                    <form method="POST" action="/api/assets/{{ asset.id }}/archive" style="display:inline;" onsubmit="return confirm('Archive {{ asset.tag }}?')">
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
    
    # Inject filter bar before the table/card
    html = re.sub(
        r'(<!-- Action Bar -->)',
        filter_bar + r'\1',
        html, count=1
    )

    write(f"{TPL}/inventory.html", html)


# ──────────────────────────────────────────────────────────────
# 2. ASSET DETAIL — wire all Nunjucks vars + history + actions
# ──────────────────────────────────────────────────────────────
def patch_asset_detail():
    html = read(f"{TPL}/asset-detail.html")

    # Find the content area and replace static values
    # The design file has hardcoded mock data, we need to replace key sections

    # Replace page breadcrumb title
    html = html.replace(
        'Asset Details',
        'Asset Details — {{ asset.asset_tag }}'
    )

    # Find the detail content section and replace with dynamic version
    # Look for the asset name display area and the static detail cards
    DYNAMIC_HEADER = """<div class="content-area">
        {% if error %}<div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:var(--status-critical); padding:14px 20px; border-radius:var(--radius-card); margin-bottom:24px;">{{ error }}</div>{% endif %}
        
        <!-- Asset Header -->
        <div class="page-header fade-up delay-1" style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <div style="font-family:var(--font-data); font-size:13px; color:var(--accent-amber); margin-bottom:6px;">{{ asset.asset_tag }}</div>
            <h1 class="page-title">{{ asset.brand }} {{ asset.model }}</h1>
            <div style="display:flex; gap:10px; margin-top:10px;">
              {% if asset.status == 'assigned' %}<span class="badge badge-active">Assigned</span>
              {% elif asset.status == 'available' %}<span class="badge badge-neutral">Available</span>
              {% elif asset.status == 'maintenance' %}<span class="badge badge-warn">Maintenance</span>
              {% else %}<span class="badge badge-neutral">{{ asset.status | title }}</span>
              {% endif %}
              <span class="badge badge-neutral">{{ asset.category }}</span>
            </div>
          </div>
          <div style="display:flex; gap:10px;">
            <a href="/assets/{{ asset.id }}/edit" class="btn btn-outline"><i data-lucide="edit-2" width="16"></i> Edit</a>
            {% if asset.assigned_employee_id %}
            <form method="POST" action="/assets/{{ asset.id }}/unassign" onsubmit="return confirm('Unassign this asset?')">
              <button type="submit" class="btn" style="background:rgba(245,158,11,0.1); color:var(--status-warn); border:1px solid rgba(245,158,11,0.3);">
                <i data-lucide="user-minus" width="16"></i> Unassign
              </button>
            </form>
            {% else %}
            <a href="/asset-assignment?asset_id={{ asset.id }}" class="btn btn-primary"><i data-lucide="user-plus" width="16"></i> Assign</a>
            {% endif %}
            <form method="POST" action="/api/assets/{{ asset.id }}/archive" onsubmit="return confirm('Archive this asset?')" style="display:inline;">
              <input type="hidden" name="reason" value="Manual Archive">
              <button type="submit" class="btn" style="background:rgba(239,68,68,0.1); color:var(--status-critical); border:1px solid rgba(239,68,68,0.3);">
                <i data-lucide="archive" width="16"></i> Archive
              </button>
            </form>
          </div>
        </div>

        <!-- Detail Cards Row -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin:24px 0;" class="fade-up delay-2">
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Serial Number</div>
            <div style="font-family:var(--font-data); color:var(--text-primary);">{{ asset.serial_number }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Department</div>
            <div>{{ asset.department }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Location</div>
            <div>{{ asset.location }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Purchase Cost</div>
            <div style="font-family:var(--font-data); color:var(--accent-amber);">₹{{ "{:,.0f}".format(asset.purchase_cost) if asset.purchase_cost else "—" }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Purchase Date</div>
            <div style="font-family:var(--font-data);">{{ asset.purchase_date or "—" }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:8px;">Warranty Until</div>
            <div style="font-family:var(--font-data);">{{ asset.warranty_date or "—" }}</div>
          </div>
        </div>

        <!-- Assignment Info -->
        {% if asset.assigned_employee_id %}
        <div class="card fade-up delay-3" style="margin-bottom:20px;">
          <div style="font-size:12px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:12px;">Currently Assigned To</div>
          <div style="display:flex; align-items:center; gap:16px;">
            <div class="avatar" style="width:44px; height:44px; font-size:15px;">{{ asset.assigned_to_name | truncate(2, false, "") | upper }}</div>
            <div>
              <div style="font-weight:600; font-size:16px;">{{ asset.assigned_to_name }}</div>
              <div style="color:var(--text-secondary); font-size:13px;">{{ asset.assigned_dept }}</div>
            </div>
          </div>
        </div>
        {% endif %}

        <!-- History -->
        <div class="card fade-up delay-4">
          <div style="font-size:13px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:20px;">Asset History</div>
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Event</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Description</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">By</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Date</th>
              </tr>
            </thead>
            <tbody>
              {% for h in history %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:12px; font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">{{ h.event_type }}</td>
                <td style="padding:12px; font-size:13px;">{{ h.description }}</td>
                <td style="padding:12px; font-size:12px; color:var(--text-secondary);">{{ h.username or "system" }}</td>
                <td style="padding:12px; font-family:var(--font-data); font-size:12px; color:var(--text-secondary);">{{ h.date.split("T")[0] if h.date else "—" }}</td>
              </tr>
              {% else %}
              <tr><td colspan="4" style="padding:24px; text-align:center; color:var(--text-secondary);">No history recorded yet</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>"""

    # Replace everything between <div class="content-area"> and </main>
    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_HEADER + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/asset-detail.html", html)


# ──────────────────────────────────────────────────────────────
# 3. ASSET ASSIGNMENT — replace static employee list with loop
# ──────────────────────────────────────────────────────────────
def patch_asset_assignment():
    html = read(f"{TPL}/asset-assignment.html")

    DYNAMIC_WIZARD = """<div class="content-area">
        {% if error %}
        <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:var(--status-critical); padding:14px 20px; border-radius:var(--radius-card); margin-bottom:20px; font-size:14px;">
          <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}

        <div class="wizard-container fade-up delay-1">
          <div class="wizard-card fade-up delay-2">
            <div class="wizard-card-header">
              <h1 class="wizard-title">Assign Asset to Employee</h1>
              <p class="wizard-subtitle">Select an available asset and the employee to receive it</p>
            </div>

            <form method="POST" action="/asset-assignment">
              <!-- Asset Select -->
              <div style="margin-bottom:24px;">
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px; font-family:var(--font-data);">Select Asset</label>
                {% if available_assets %}
                <select name="asset_id" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:12px 16px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">— Choose an available asset —</option>
                  {% for a in available_assets %}
                  <option value="{{ a.id }}" {% if preselect_asset == a.id %}selected{% endif %}>
                    {{ a.asset_tag }} — {{ a.brand }} {{ a.model }} ({{ a.category }})
                  </option>
                  {% endfor %}
                </select>
                {% else %}
                <div style="padding:16px; background:var(--bg-raised); border:1px solid var(--border); border-radius:var(--radius-input); color:var(--text-secondary);">
                  No available assets found. All assets are currently assigned or in maintenance.
                </div>
                {% endif %}
              </div>

              <!-- Employee Select -->
              <div style="margin-bottom:28px;">
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px; font-family:var(--font-data);">Select Employee</label>
                <div class="employee-list">
                  {% for emp in employees %}
                  <label class="employee-row">
                    <input type="radio" name="employee_id" value="{{ emp.id }}" class="custom-radio" required>
                    <div class="emp-avatar bg-it">{{ emp.name | truncate(2, false, "") | upper }}</div>
                    <div class="emp-info">
                      <div class="emp-name">{{ emp.name }}</div>
                      <div class="emp-role">{{ emp.department }}</div>
                    </div>
                    <div class="dept-pill tag-it">{{ emp.department }}</div>
                    <div class="emp-assets">{{ emp.assets_count }} active assets</div>
                  </label>
                  {% else %}
                  <div style="padding:24px; text-align:center; color:var(--text-secondary);">No active employees found.</div>
                  {% endfor %}
                </div>
              </div>

              <div class="wizard-footer">
                <a href="/inventory" class="btn btn-outline"><i data-lucide="arrow-left" width="16"></i> Back to Inventory</a>
                <button type="submit" class="btn btn-primary" {% if not available_assets %}disabled{% endif %}>
                  Confirm Assignment <i data-lucide="check" width="16"></i>
                </button>
              </div>
            </form>
          </div>
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_WIZARD + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/asset-assignment.html", html)


# ──────────────────────────────────────────────────────────────
# 4. REQUESTS — replace hardcoded cards with real loop + approve/reject
# ──────────────────────────────────────────────────────────────
def patch_requests():
    html = read(f"{TPL}/requests.html")

    DYNAMIC_CONTENT = """<div class="content-area">
        <div class="page-header fade-up delay-1" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h1 class="page-title">Asset Requests</h1>
            <p class="page-subtitle">Manage and approve employee hardware requests</p>
          </div>
          <div style="display:flex; gap:10px;">
            <a href="/requests" class="btn {% if not statusFilter %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">All</a>
            <a href="/requests?status=pending" class="btn {% if statusFilter == 'pending' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Pending</a>
            <a href="/requests?status=approved" class="btn {% if statusFilter == 'approved' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Approved</a>
            <a href="/requests?status=rejected" class="btn {% if statusFilter == 'rejected' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Rejected</a>
          </div>
        </div>

        <div class="card fade-up delay-2" style="overflow:hidden; padding:0;">
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border); background:var(--bg-raised);">
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">ID</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Employee</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Type</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Category</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Date</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Status</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase; letter-spacing:0.08em;">Actions</th>
              </tr>
            </thead>
            <tbody>
              {% for r in requests %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:14px 20px; font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">REQ-{{ r.id[:8] | upper }}</td>
                <td style="padding:14px 20px;">
                  <div style="font-weight:500; font-size:14px;">{{ r.employee_name }}</div>
                  <div style="font-size:12px; color:var(--text-secondary);">{{ r.department }}</div>
                </td>
                <td style="padding:14px 20px; font-size:13px;">{{ r.request_type }}</td>
                <td style="padding:14px 20px; font-size:13px;">{{ r.category or "—" }}</td>
                <td style="padding:14px 20px; font-family:var(--font-data); font-size:12px; color:var(--text-secondary);">{{ r.requested_date.split("T")[0] if r.requested_date else "—" }}</td>
                <td style="padding:14px 20px;">
                  {% if r.status == 'approved' %}<span class="badge badge-active">Approved</span>
                  {% elif r.status == 'pending' %}<span class="badge badge-warn">Pending</span>
                  {% elif r.status == 'rejected' %}<span class="badge badge-critical">Rejected</span>
                  {% else %}<span class="badge badge-neutral">{{ r.status | title }}</span>
                  {% endif %}
                </td>
                <td style="padding:14px 20px;">
                  {% if r.status == 'pending' %}
                  <div style="display:flex; gap:8px;">
                    <form method="POST" action="/requests/{{ r.id }}/approve">
                      <button type="submit" class="btn btn-primary btn-sm" style="padding:4px 12px; font-size:12px;">Approve</button>
                    </form>
                    <form method="POST" action="/requests/{{ r.id }}/reject">
                      <button type="submit" class="btn" style="padding:4px 12px; font-size:12px; background:rgba(239,68,68,0.1); color:var(--status-critical); border:1px solid rgba(239,68,68,0.3);">Reject</button>
                    </form>
                  </div>
                  {% else %}
                  <span style="font-size:12px; color:var(--text-secondary);">—</span>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="7" style="padding:32px; text-align:center; color:var(--text-secondary);">No requests found</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_CONTENT + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/requests.html", html)


# ──────────────────────────────────────────────────────────────
# 5. TRANSFERS — real rows + approve/reject forms + new transfer form
# ──────────────────────────────────────────────────────────────
def patch_transfers():
    html = read(f"{TPL}/transfers.html")

    DYNAMIC_CONTENT = """<div class="content-area">
        <div class="page-header fade-up delay-1" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h1 class="page-title">Asset Transfers</h1>
            <p class="page-subtitle">Track and manage inter-department asset movements</p>
          </div>
          <div style="display:flex; gap:10px;">
            <a href="/transfers" class="btn {% if not statusFilter %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">All</a>
            <a href="/transfers?status=pending" class="btn {% if statusFilter == 'pending' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Pending</a>
            <a href="/transfers?status=completed" class="btn {% if statusFilter == 'completed' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Completed</a>
          </div>
        </div>

        <!-- New Transfer Form -->
        <div class="card fade-up delay-2" style="margin-bottom:24px;">
          <div style="font-size:12px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:16px;">Create New Transfer</div>
          <form method="POST" action="/transfers" style="display:flex; gap:14px; flex-wrap:wrap; align-items:flex-end;">
            <div style="flex:1; min-width:180px;">
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Asset</label>
              <select name="asset_id" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
                <option value="">— Select assigned asset —</option>
                {% for a in assets %}<option value="{{ a.id }}">{{ a.asset_tag }} — {{ a.brand }} {{ a.model }}</option>{% endfor %}
              </select>
            </div>
            <div style="flex:1; min-width:180px;">
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Transfer To</label>
              <select name="to_employee_id" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
                <option value="">— Select employee —</option>
                {% for e in employees %}<option value="{{ e.id }}">{{ e.name }} ({{ e.department }})</option>{% endfor %}
              </select>
            </div>
            <div style="flex:1; min-width:140px;">
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Notes</label>
              <input type="text" name="notes" placeholder="Optional notes..." style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
            </div>
            <button type="submit" class="btn btn-primary" style="white-space:nowrap;"><i data-lucide="arrow-right-left" width="16"></i> Create Transfer</button>
          </form>
        </div>

        <div class="card fade-up delay-3" style="overflow:hidden; padding:0;">
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border); background:var(--bg-raised);">
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Asset</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">From</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">To</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Date</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Status</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Actions</th>
              </tr>
            </thead>
            <tbody>
              {% for t in transfers %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:14px 20px;">
                  <div style="font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">{{ t.asset_tag }}</div>
                  <div style="font-size:13px;">{{ t.brand }} {{ t.model }}</div>
                </td>
                <td style="padding:14px 20px; font-size:13px;">{{ t.from_employee or "Unassigned" }}</td>
                <td style="padding:14px 20px; font-size:13px; font-weight:500;">{{ t.to_employee }}</td>
                <td style="padding:14px 20px; font-family:var(--font-data); font-size:12px; color:var(--text-secondary);">{{ t.request_date.split("T")[0] if t.request_date else "—" }}</td>
                <td style="padding:14px 20px;">
                  {% if t.status == 'completed' %}<span class="badge badge-active">Completed</span>
                  {% elif t.status == 'pending' %}<span class="badge badge-warn">Pending</span>
                  {% elif t.status == 'rejected' %}<span class="badge badge-critical">Rejected</span>
                  {% else %}<span class="badge badge-neutral">{{ t.status | title }}</span>
                  {% endif %}
                </td>
                <td style="padding:14px 20px;">
                  {% if t.status == 'pending' %}
                  <div style="display:flex; gap:8px;">
                    <form method="POST" action="/transfers/{{ t.id }}/approve">
                      <button type="submit" class="btn btn-primary" style="padding:4px 12px; font-size:12px;">Approve</button>
                    </form>
                    <form method="POST" action="/transfers/{{ t.id }}/reject">
                      <button type="submit" class="btn" style="padding:4px 12px; font-size:12px; background:rgba(239,68,68,0.1); color:var(--status-critical); border:1px solid rgba(239,68,68,0.3);">Reject</button>
                    </form>
                  </div>
                  {% else %}
                  <span style="font-size:12px; color:var(--text-secondary);">—</span>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="padding:32px; text-align:center; color:var(--text-secondary);">No transfers found</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_CONTENT + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/transfers.html", html)


# ──────────────────────────────────────────────────────────────
# 6. MAINTENANCE — real rows + new ticket form + status updates
# ──────────────────────────────────────────────────────────────
def patch_maintenance():
    html = read(f"{TPL}/maintenance.html")

    DYNAMIC_CONTENT = """<div class="content-area">
        <div class="page-header fade-up delay-1" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h1 class="page-title">Maintenance</h1>
            <p class="page-subtitle">Track repairs and hardware maintenance tickets</p>
          </div>
          <div style="display:flex; gap:10px;">
            <a href="/maintenance" class="btn {% if not statusFilter %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">All</a>
            <a href="/maintenance?status=pending" class="btn {% if statusFilter == 'pending' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Pending</a>
            <a href="/maintenance?status=in_progress" class="btn {% if statusFilter == 'in_progress' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">In Progress</a>
            <a href="/maintenance?status=completed" class="btn {% if statusFilter == 'completed' %}btn-primary{% else %}btn-outline{% endif %}" style="font-size:13px; padding:8px 14px;">Completed</a>
          </div>
        </div>

        <!-- New Ticket Form -->
        <div class="card fade-up delay-2" style="margin-bottom:24px;">
          <div style="font-size:12px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:16px;">Create New Ticket</div>
          <form method="POST" action="/maintenance" style="display:flex; gap:14px; flex-wrap:wrap; align-items:flex-end;">
            <div style="flex:1; min-width:180px;">
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Asset</label>
              <select name="asset_id" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
                <option value="">— Select asset —</option>
                {% for a in all_assets %}<option value="{{ a.id }}">{{ a.asset_tag }} — {{ a.brand }} {{ a.model }}</option>{% endfor %}
              </select>
            </div>
            <div style="flex:2; min-width:220px;">
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Issue Description</label>
              <input type="text" name="issue_description" required placeholder="Describe the issue..." style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
            </div>
            <div>
              <label style="display:block; font-size:11px; color:var(--text-secondary); margin-bottom:6px; font-family:var(--font-data); text-transform:uppercase;">Initial Status</label>
              <select name="status" style="background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-size:13px; outline:none;">
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="awaiting_parts">Awaiting Parts</option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary"><i data-lucide="plus" width="16"></i> Create Ticket</button>
          </form>
        </div>

        <div class="card fade-up delay-3" style="overflow:hidden; padding:0;">
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border); background:var(--bg-raised);">
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Asset</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Issue</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Reported By</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Date</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Status</th>
                <th style="text-align:left; padding:14px 20px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Update</th>
              </tr>
            </thead>
            <tbody>
              {% for m in maintenance %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:14px 20px;">
                  <div style="font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">{{ m.asset_tag }}</div>
                  <div style="font-size:13px;">{{ m.brand }} {{ m.model }}</div>
                </td>
                <td style="padding:14px 20px; font-size:13px; max-width:220px;">{{ m.issue_description }}</td>
                <td style="padding:14px 20px; font-size:13px; color:var(--text-secondary);">{{ m.reported_by_name or "—" }}</td>
                <td style="padding:14px 20px; font-family:var(--font-data); font-size:12px; color:var(--text-secondary);">{{ m.reported_date.split("T")[0] if m.reported_date else "—" }}</td>
                <td style="padding:14px 20px;">
                  {% if m.status == 'completed' %}<span class="badge badge-active">Completed</span>
                  {% elif m.status == 'in_progress' %}<span class="badge badge-warn">In Progress</span>
                  {% elif m.status == 'awaiting_parts' %}<span class="badge badge-warn">Awaiting Parts</span>
                  {% elif m.status == 'pending' %}<span class="badge badge-neutral">Pending</span>
                  {% else %}<span class="badge badge-neutral">{{ m.status | title }}</span>
                  {% endif %}
                </td>
                <td style="padding:14px 20px;">
                  {% if m.status != 'completed' %}
                  <form method="POST" action="/maintenance/{{ m.id }}/status" style="display:flex; gap:6px;">
                    <select name="status" style="background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:4px 8px; border-radius:var(--radius-input); font-size:12px; outline:none;">
                      <option value="pending" {% if m.status == 'pending' %}selected{% endif %}>Pending</option>
                      <option value="in_progress" {% if m.status == 'in_progress' %}selected{% endif %}>In Progress</option>
                      <option value="awaiting_parts" {% if m.status == 'awaiting_parts' %}selected{% endif %}>Awaiting Parts</option>
                      <option value="completed">Completed</option>
                    </select>
                    <button type="submit" class="btn btn-outline" style="padding:4px 10px; font-size:12px;">Set</button>
                  </form>
                  {% else %}
                  <span style="font-size:12px; color:var(--text-secondary);">Resolved</span>
                  {% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="6" style="padding:32px; text-align:center; color:var(--text-secondary);">No maintenance tickets found</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_CONTENT + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/maintenance.html", html)


# ──────────────────────────────────────────────────────────────
# 7. NOTIFICATIONS — real list + mark-read forms
# ──────────────────────────────────────────────────────────────
def patch_notifications():
    html = read(f"{TPL}/notifications.html")

    DYNAMIC_CONTENT = """<div class="content-area">
        <div class="page-header fade-up delay-1" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h1 class="page-title">Notifications</h1>
            <p class="page-subtitle">{{ unread_count }} unread notification{{ "s" if unread_count != 1 else "" }}</p>
          </div>
          {% if unread_count > 0 %}
          <form method="POST" action="/notifications/read-all">
            <button type="submit" class="btn btn-outline"><i data-lucide="check-check" width="16"></i> Mark All Read</button>
          </form>
          {% endif %}
        </div>

        <div class="card fade-up delay-2" style="padding:0; overflow:hidden;">
          {% for n in notifications %}
          <div style="padding:18px 24px; border-bottom:1px solid var(--border); display:flex; gap:16px; align-items:flex-start; {% if not n.is_read %}background:rgba(244,162,38,0.03);{% endif %}">
            <div style="width:10px; height:10px; border-radius:50%; margin-top:5px; flex-shrink:0;
              background:{% if n.type == 'critical' %}var(--status-critical){% elif n.type == 'warning' %}var(--status-warn){% elif n.type == 'success' %}var(--status-active){% else %}var(--accent-ice){% endif %};
              {% if n.is_read %}opacity:0.3;{% endif %}"></div>
            <div style="flex:1;">
              <div style="font-weight:500; font-size:14px; {% if n.is_read %}color:var(--text-secondary);{% endif %}">{{ n.title }}</div>
              <div style="color:var(--text-secondary); font-size:13px; margin-top:4px;">{{ n.message }}</div>
              <div style="font-family:var(--font-data); font-size:11px; color:var(--text-disabled); margin-top:8px;">{{ n.created_at.split("T")[0] if n.created_at else "" }}</div>
            </div>
            <div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">
              {% if not n.is_read %}
              <span class="badge badge-warn">New</span>
              <form method="POST" action="/notifications/{{ n.id }}/read">
                <button type="submit" class="btn btn-outline" style="padding:4px 10px; font-size:11px;">Mark Read</button>
              </form>
              {% else %}
              <span style="font-size:11px; color:var(--text-disabled); font-family:var(--font-data);">READ</span>
              {% endif %}
            </div>
          </div>
          {% else %}
          <div style="padding:48px; text-align:center; color:var(--text-secondary);">
            <i data-lucide="bell-off" style="display:block; margin:0 auto 12px; width:32px; height:32px; opacity:0.3;"></i>
            No notifications
          </div>
          {% endfor %}
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_CONTENT + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/notifications.html", html)


# ──────────────────────────────────────────────────────────────
# 8. EMPLOYEE PROFILE — wire real data
# ──────────────────────────────────────────────────────────────
def patch_employee_profile():
    html = read(f"{TPL}/employee-profile.html")

    DYNAMIC_CONTENT = """<div class="content-area">
        <div class="page-header fade-up delay-1">
          <a href="/employees" style="font-size:13px; color:var(--text-secondary); text-decoration:none; display:inline-flex; align-items:center; gap:6px; margin-bottom:12px;">
            <i data-lucide="arrow-left" width="14"></i> Back to Directory
          </a>
          <div style="display:flex; align-items:center; gap:20px;">
            <div class="avatar" style="width:64px; height:64px; font-size:22px; border-radius:50%; background:var(--accent-ice-dim); display:flex; align-items:center; justify-content:center;">
              {{ employee.name | truncate(2, false, "") | upper }}
            </div>
            <div>
              <h1 class="page-title" style="margin-bottom:6px;">{{ employee.name }}</h1>
              <div style="display:flex; gap:10px; align-items:center;">
                <span class="badge badge-neutral">{{ employee.department }}</span>
                <span style="font-size:13px; color:var(--text-secondary);">{{ employee.location }}</span>
                {% if employee.status == 'active' %}
                <span class="badge badge-active">Active</span>
                {% else %}
                <span class="badge badge-neutral">{{ employee.status | title }}</span>
                {% endif %}
              </div>
            </div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:24px;" class="fade-up delay-2">
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; font-family:var(--font-data); margin-bottom:8px;">Email</div>
            <div style="font-size:14px;">{{ employee.email }}</div>
          </div>
          <div class="card">
            <div style="font-size:11px; color:var(--text-disabled); text-transform:uppercase; font-family:var(--font-data); margin-bottom:8px;">Phone</div>
            <div style="font-family:var(--font-data);">{{ employee.phone or "—" }}</div>
          </div>
        </div>

        <!-- Assigned Assets -->
        <div class="card fade-up delay-3" style="margin-bottom:24px;">
          <div style="font-size:12px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:16px;">Assigned Assets ({{ assigned_assets | length }})</div>
          {% if assigned_assets %}
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Tag</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Asset</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Category</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Status</th>
                <th style="text-align:left; padding:8px 12px;"></th>
              </tr>
            </thead>
            <tbody>
              {% for a in assigned_assets %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:10px 12px; font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">{{ a.asset_tag }}</td>
                <td style="padding:10px 12px; font-size:13px;">{{ a.brand }} {{ a.model }}</td>
                <td style="padding:10px 12px;"><span class="badge badge-neutral">{{ a.category }}</span></td>
                <td style="padding:10px 12px;"><span class="badge badge-active">{{ a.status | title }}</span></td>
                <td style="padding:10px 12px;"><a href="/assets/{{ a.id }}" class="btn btn-outline" style="padding:3px 10px; font-size:11px;">View</a></td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% else %}
          <div style="color:var(--text-secondary); font-size:14px;">No assets currently assigned.</div>
          {% endif %}
        </div>

        <!-- Recent Requests -->
        <div class="card fade-up delay-4">
          <div style="font-size:12px; color:var(--text-disabled); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data); margin-bottom:16px;">Recent Requests</div>
          {% if emp_requests %}
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Type</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Category</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Date</th>
                <th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Status</th>
              </tr>
            </thead>
            <tbody>
              {% for r in emp_requests %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.5);">
                <td style="padding:10px 12px; font-size:13px;">{{ r.request_type }}</td>
                <td style="padding:10px 12px; font-size:13px;">{{ r.category or "—" }}</td>
                <td style="padding:10px 12px; font-family:var(--font-data); font-size:12px; color:var(--text-secondary);">{{ r.requested_date.split("T")[0] if r.requested_date else "—" }}</td>
                <td style="padding:10px 12px;">
                  {% if r.status == 'approved' %}<span class="badge badge-active">Approved</span>
                  {% elif r.status == 'pending' %}<span class="badge badge-warn">Pending</span>
                  {% elif r.status == 'rejected' %}<span class="badge badge-critical">Rejected</span>
                  {% else %}<span class="badge badge-neutral">{{ r.status | title }}</span>
                  {% endif %}
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% else %}
          <div style="color:var(--text-secondary); font-size:14px;">No requests on file.</div>
          {% endif %}
        </div>"""

    html = re.sub(
        r'<div class="content-area">.*?</main>',
        DYNAMIC_CONTENT + '\n      </div>\n    </main>',
        html, flags=re.DOTALL, count=1
    )

    write(f"{TPL}/employee-profile.html", html)


# ──────────────────────────────────────────────────────────────
# 9. DASHBOARD — fix Add Asset link, live recent activity
# ──────────────────────────────────────────────────────────────
def patch_dashboard():
    html = read(f"{TPL}/dashboard.html")

    # Fix "Add Asset" button to be a link
    html = re.sub(
        r'<button class="btn btn-primary"[^>]*>\s*(?:<i[^>]*/?>)?[^<]*(?:</i>)?\s*(?:Add|New)[^<]*Asset[^<]*</button>',
        '<a href="/assets/new" class="btn btn-primary"><i data-lucide="plus" width="16"></i> Add Asset</a>',
        html, flags=re.IGNORECASE
    )

    # Replace any generic "View All" links to go to /inventory
    html = re.sub(
        r'href="#"\s+class="[^"]*view-all[^"]*"',
        'href="/inventory"',
        html
    )

    # Inject recent activity section if it has a placeholder
    # After the KPI cards, inject recent assets table
    RECENT_INJECT = """
        <!-- Recent Assets -->
        <div class="card fade-up delay-3" style="margin-top:24px; padding:0; overflow:hidden;">
          <div style="padding:20px 24px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:13px; font-weight:600;">Recent Assets</div>
            <a href="/inventory" style="font-size:12px; color:var(--accent-amber); text-decoration:none; font-family:var(--font-data);">VIEW ALL →</a>
          </div>
          <table style="width:100%; border-collapse:collapse;">
            <tbody>
              {% for a in recent_assets %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.4);">
                <td style="padding:12px 24px;">
                  <div style="font-family:var(--font-data); font-size:12px; color:var(--accent-amber);">{{ a.asset_tag }}</div>
                  <div style="font-size:13px; font-weight:500;">{{ a.brand }} {{ a.model }}</div>
                </td>
                <td style="padding:12px 24px;">
                  {% if a.status == 'assigned' %}<span class="badge badge-active">Assigned</span>
                  {% elif a.status == 'available' %}<span class="badge badge-neutral">Available</span>
                  {% elif a.status == 'maintenance' %}<span class="badge badge-warn">Maintenance</span>
                  {% else %}<span class="badge badge-neutral">{{ a.status | title }}</span>
                  {% endif %}
                </td>
                <td style="padding:12px 24px; font-size:13px; color:var(--text-secondary);">{{ a.assigned_to_name or "Unassigned" }}</td>
                <td style="padding:12px 24px;"><a href="/assets/{{ a.id }}" style="font-size:12px; color:var(--accent-ice); text-decoration:none; font-family:var(--font-data);">VIEW →</a></td>
              </tr>
              {% else %}
              <tr><td colspan="4" style="padding:24px; text-align:center; color:var(--text-secondary);">No assets yet</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>

        <!-- Pending Requests -->
        {% if recent_requests %}
        <div class="card fade-up delay-4" style="margin-top:20px; padding:0; overflow:hidden;">
          <div style="padding:20px 24px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:13px; font-weight:600;">Pending Requests <span class="badge badge-warn" style="margin-left:8px;">{{ recent_requests | length }}</span></div>
            <a href="/requests?status=pending" style="font-size:12px; color:var(--accent-amber); text-decoration:none; font-family:var(--font-data);">VIEW ALL →</a>
          </div>
          <table style="width:100%; border-collapse:collapse;">
            <tbody>
              {% for r in recent_requests %}
              <tr style="border-bottom:1px solid rgba(30,42,69,0.4);">
                <td style="padding:12px 24px; font-size:13px; font-weight:500;">{{ r.employee_name }}</td>
                <td style="padding:12px 24px; font-size:13px; color:var(--text-secondary);">{{ r.request_type }} — {{ r.category }}</td>
                <td style="padding:12px 24px;">
                  <form method="POST" action="/requests/{{ r.id }}/approve" style="display:inline;">
                    <button type="submit" class="btn btn-primary" style="padding:3px 10px; font-size:11px;">Approve</button>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% endif %}
"""

    # Inject before </main>
    html = html.replace('</main>', RECENT_INJECT + '\n    </main>', 1)

    write(f"{TPL}/dashboard.html", html)


# ──────────────────────────────────────────────────────────────
# Run all patches
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Patching CognixAsset templates with real data wiring...\n")
    patch_inventory()
    patch_asset_detail()
    patch_asset_assignment()
    patch_requests()
    patch_transfers()
    patch_maintenance()
    patch_notifications()
    patch_employee_profile()
    patch_dashboard()
    print("\n✅ All templates patched successfully!")
