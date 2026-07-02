import re

with open('templates/asset-detail.html', 'r') as f:
    content = f.read()

# Replace header panel
content = content.replace(
    '<h1 class="asset-name">Dell XPS 15 9530</h1>',
    '<h1 class="asset-name">{{ asset.brand }} {{ asset.model }}</h1>'
)
content = content.replace(
    '<span style="color: var(--accent-ice);">LP-0421</span>',
    '<span style="color: var(--accent-ice);">{{ asset.asset_tag }}</span>'
)
content = content.replace(
    '<span class="badge badge-active" style="padding:4px 8px; font-size:12px;">ACTIVE</span>',
    '<span class="badge badge-active" style="padding:4px 8px; font-size:12px; text-transform:uppercase;">{{ asset.status }}</span>'
)
content = content.replace(
    'Serial #JK8942X <div class="meta-dot"></div> Bangalore HQ <div class="meta-dot"></div> Added Jan 2024',
    'Serial #{{ asset.serial_number }} <div class="meta-dot"></div> {{ asset.location }} <div class="meta-dot"></div> Added {{ asset.created_at | truncate(10, true, "") }}'
)
content = content.replace(
    '<span class="stat-value">₹1,84,000</span>',
    '<span class="stat-value">₹{{ asset.purchase_cost or "0" }}</span>'
)
content = content.replace(
    '<span class="stat-value" style="color: var(--accent-amber);">₹1,32,000</span>',
    '<span class="stat-value" style="color: var(--accent-amber);">₹{{ asset.purchase_cost or "0" }}</span>'
)
content = content.replace(
    '<span class="stat-value">1y 4m</span>',
    '<span class="stat-value">{{ asset.purchase_date or "N/A" }}</span>'
)
content = content.replace(
    '<span class="stat-value" style="color: var(--accent-ice);">Dec 2026</span>',
    '<span class="stat-value" style="color: var(--accent-ice);">{{ asset.warranty_date or "N/A" }}</span>'
)

# Replace info-grid
old_info_grid = """          <div class="info-grid fade-up delay-2">
            <div class="info-cell">
              <div class="info-label">Brand</div>
              <div class="info-value">Dell</div>
            </div>
            <div class="info-cell">
              <div class="info-label">Model</div>
              <div class="info-value">XPS 15 9530</div>
            </div>
            <div class="info-cell">
              <div class="info-label">Processor</div>
              <div class="info-value">Intel Core i7-13700H</div>
            </div>
            <div class="info-cell">
              <div class="info-label">RAM</div>
              <div class="info-value">32GB DDR5</div>
            </div>
            <div class="info-cell">
              <div class="info-label">Storage</div>
              <div class="info-value">1TB NVMe SSD</div>
            </div>
            <div class="info-cell">
              <div class="info-label">OS</div>
              <div class="info-value">Windows 11 Pro</div>
            </div>
          </div>"""

new_info_grid = """          <div class="info-grid fade-up delay-2">
            <div class="info-cell"><div class="info-label">Brand</div><div class="info-value">{{ asset.brand or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Model</div><div class="info-value">{{ asset.model or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Category</div><div class="info-value">{{ asset.category or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Department</div><div class="info-value">{{ asset.department or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Sl.no</div><div class="info-value">{{ asset.sl_no or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Monitor Make</div><div class="info-value">{{ asset.monitor_make or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Monitor Serial No</div><div class="info-value">{{ asset.monitor_serial_no or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Asset Owner & PL No</div><div class="info-value">{{ asset.asset_owner_pl_no or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Usage Status</div><div class="info-value">{{ asset.asset_usage_status or "N/A" }}</div></div>
            <div class="info-cell"><div class="info-label">Warranty Status</div><div class="info-value">{{ asset.in_warranty_status or "N/A" }}</div></div>
          </div>

          <div style="margin-top:20px;">
            <button type="button" onclick="document.getElementById('additional-details-view').style.display = document.getElementById('additional-details-view').style.display === 'none' ? 'block' : 'none'" style="background:transparent; border:none; color:var(--text-secondary); cursor:pointer; display:flex; align-items:center; gap:8px; font-family:var(--font-ui); font-size:14px; padding:0;">
              <i data-lucide="more-horizontal" width="16"></i> Additional Details
            </button>
          </div>

          <div id="additional-details-view" style="display: none; margin-top: 20px;">
            <div class="info-grid">
              <div class="info-cell"><div class="info-label">System Serial No</div><div class="info-value">{{ asset.system_serial_no or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Host Name</div><div class="info-value">{{ asset.host_name or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Group Name</div><div class="info-value">{{ asset.group_name or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Division</div><div class="info-value">{{ asset.division or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">User Name</div><div class="info-value">{{ asset.user_name or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Designation</div><div class="info-value">{{ asset.designation or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">IP Address</div><div class="info-value">{{ asset.ip_address or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">MAC Address</div><div class="info-value">{{ asset.mac_address or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Network Type</div><div class="info-value">{{ asset.network_type or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Drona / Domain</div><div class="info-value">{{ asset.drona_domain or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">OS Version</div><div class="info-value">{{ asset.os_version or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Antivirus Status</div><div class="info-value">{{ asset.antivirus_status or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">USB Status</div><div class="info-value">{{ asset.usb_status or "N/A" }}</div></div>
              <div class="info-cell"><div class="info-label">Admin Privilege</div><div class="info-value">{{ asset.admin_privilege or "N/A" }}</div></div>
            </div>
          </div>
"""

content = content.replace(old_info_grid, new_info_grid)

# Ensure Edit Asset button routes to the correct place
content = content.replace('<button class="btn btn-primary"><i data-lucide="pen-line"></i> Edit Asset</button>', '<a href="/assets/{{ asset.id }}/edit" class="btn btn-primary" style="text-decoration:none;"><i data-lucide="pen-line"></i> Edit Asset</a>')

with open('templates/asset-detail.html', 'w') as f:
    f.write(content)

print("asset-detail.html patched.")
