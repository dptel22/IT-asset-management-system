import re

with open('templates/inventory.html', 'r') as f:
    content = f.read()

# Add overflow-x: auto to table-container
content = content.replace('<div class="table-container fade-up delay-3">', '<div class="table-container fade-up delay-3" style="overflow-x: auto;">')

# Update table headers
old_thead = """            <thead>
              <tr>
                <th style="width: 48px; text-align:center;"><input type="checkbox" class="custom-checkbox"></th>
                <th>Asset ID</th>
                <th>Asset Name</th>
                <th>Category</th>
                <th>Current Owner</th>
                <th>Department</th>
                <th>Location</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th style="width: 100px;">Actions</th>
              </tr>
            </thead>"""

# The body actually has:
# 1. tag and name (Asset ID and Name)
# 2. category
# 3. department
# 4. status
# 5. assigned_employee.name
# 6. actions
# So the original thead was mismatched!
new_thead = """            <thead>
              <tr>
                <th>Asset ID / Name</th>
                <th>Category</th>
                <th>Department</th>
                <th>Status</th>
                <th>Usage</th>
                <th>Warranty</th>
                <th>Current Owner & PL No</th>
                <th>Monitor Make</th>
                <th>Sl.no</th>
                <th style="width: 100px;">Actions</th>
              </tr>
            </thead>"""

content = content.replace(old_thead, new_thead)

# Update table body
old_tbody = """              {% for asset in assets %}
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
              </tr>"""

new_tbody = """              {% for asset in assets %}
              <tr>
                <td>
                  <div style="font-family: var(--font-data); font-size: 13px; color: var(--accent-amber);">{{ asset.asset_tag }}</div>
                  <div style="font-size: 13px;">{{ asset.brand }} {{ asset.model }}</div>
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
                <td><span class="badge badge-neutral">{{ asset.asset_usage_status or "—" }}</span></td>
                <td><span class="badge badge-neutral">{{ asset.in_warranty_status or "—" }}</span></td>
                <td>{{ asset.asset_owner_pl_no or "—" }}</td>
                <td>{{ asset.monitor_make or "—" }}</td>
                <td>{{ asset.sl_no or "—" }}</td>
                <td>
                  <div style="display:flex; gap:8px;">
                    <a href="/assets/{{ asset.id }}" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px;">View</a>
                    <a href="/assets/{{ asset.id }}/edit" class="btn btn-outline" style="padding: 4px 10px; font-size: 12px; border-color: var(--accent-amber); color: var(--accent-amber);">Edit</a>
                    <form method="POST" action="/api/assets/{{ asset.id }}/archive" style="display:inline;" onsubmit="return confirm('Archive {{ asset.asset_tag }}?')">
                      <input type="hidden" name="reason" value="Manual Archive">
                      <button type="submit" class="btn" style="padding: 4px 10px; font-size: 12px; background: rgba(239,68,68,0.1); color: var(--status-critical); border: 1px solid rgba(239,68,68,0.3);">Archive</button>
                    </form>
                  </div>
                </td>
              </tr>"""

content = content.replace(old_tbody, new_tbody)

with open('templates/inventory.html', 'w') as f:
    f.write(content)

print("inventory.html patched.")
