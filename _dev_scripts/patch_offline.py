import re
import os

with open("ui/ux/gen_pages.py", "r") as f:
    gen_content = f.read()

new_fields = """
              <div class="form-grid mt-3">
                <div class="form-group">
                  <label>Sl.no <span class="required">*</span></label>
                  <input type="text" class="form-control" placeholder="Serial Number" required>
                </div>
                <div class="form-group">
                  <label>Monitor make</label>
                  <input type="text" class="form-control" placeholder="E.g., Dell, LG">
                </div>
                <div class="form-group">
                  <label>Monitor serial no</label>
                  <input type="text" class="form-control" placeholder="Monitor Serial">
                </div>
                <div class="form-group">
                  <label>Asset owner and PL no</label>
                  <input type="text" class="form-control" placeholder="Owner & PL Number">
                </div>
                <div class="form-group">
                  <label>Usage Status <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="In Use">In Use</option>
                    <option value="Condemn">Condemn</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>In warranty <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                    <option value="In Maintenance">In Maintenance</option>
                  </select>
                </div>
              </div>

              <!-- Collapsible Additional Details -->
              <div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border);">
                <button type="button" onclick="const e = document.getElementById('extra-fields'); e.style.display = e.style.display === 'none' ? 'block' : 'none';" style="background:none; border:none; color:var(--text-secondary); display:flex; align-items:center; gap:8px; cursor:pointer; font-family:var(--font-ui); font-size:14px; padding:0;">
                  <i data-lucide="more-horizontal" width="16"></i> Show Additional Details
                </button>
                <div id="extra-fields" style="display:none; margin-top:16px;">
                  <div class="form-grid">
                    <div class="form-group"><label>Hostname</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>OS / Windows version</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>MAC address (Ethernet & Wifi)</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>RAM size</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Storage size and type</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Graphics card</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Any Display port adapter / Dongles</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Keyboard and Mouse details</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Laptop charger details</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Asset PO / Invoice no</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Vendor Details</label><input type="text" class="form-control"></div>
                    <div class="form-group"><label>Date of receipt</label><input type="date" class="form-control"></div>
                    <div class="form-group"><label>Warranty end date</label><input type="date" class="form-control"></div>
                  </div>
                </div>
              </div>
"""

# Inject into gen_pages.py add_asset_html form
if "Additional Details" not in gen_content:
    gen_content = gen_content.replace(
        '<div class="form-actions mt-4">',
        new_fields + '\n              <div class="form-actions mt-4">'
    )
    with open("ui/ux/gen_pages.py", "w") as f:
        f.write(gen_content)
    os.system("cd ui/ux && python3 gen_pages.py")
    print("Patched gen_pages.py and ran it.")

# Patch asset-detail.html
try:
    with open("ui/ux/asset-detail.html", "r") as f:
        ad_content = f.read()
    if "Additional Details" not in ad_content:
        # Find a place to inject. The asset-detail.html has an info-grid or similar.
        ad_content = ad_content.replace(
            '<div class="card fade-up delay-2">',
            new_fields.replace('<input type="text" class="form-control" placeholder="Serial Number" required>', '<div style="font-family:var(--font-data);">AST-XXXXX-SN</div>').replace('<input', '<input disabled') + '\n          <div class="card fade-up delay-2">'
        )
        with open("ui/ux/asset-detail.html", "w") as f:
            f.write(ad_content)
        print("Patched asset-detail.html")
except Exception as e:
    print(e)

# Patch inventory.html
try:
    with open("ui/ux/inventory.html", "r") as f:
        inv_content = f.read()
    if "Sl.no" not in inv_content:
        inv_content = inv_content.replace('<th>Status</th>', '<th>Status</th>\n                <th>Usage</th>\n                <th>Warranty</th>\n                <th>Sl.no</th>')
        inv_content = inv_content.replace('<td><span class="status-badge status-active">Assigned</span></td>', '<td><span class="status-badge status-active">Assigned</span></td>\n                <td>In Use</td>\n                <td>Yes</td>\n                <td>1A2B3C</td>')
        inv_content = inv_content.replace('<td><span class="status-badge status-warning">Maintenance</span></td>', '<td><span class="status-badge status-warning">Maintenance</span></td>\n                <td>Condemn</td>\n                <td>No</td>\n                <td>X9Y8Z7</td>')
        inv_content = inv_content.replace('<td><span class="status-badge status-info">Available</span></td>', '<td><span class="status-badge status-info">Available</span></td>\n                <td>In Use</td>\n                <td>Yes</td>\n                <td>P5Q6R7</td>')
        # Add overflow
        inv_content = inv_content.replace('<div class="table-responsive">', '<div class="table-responsive" style="overflow-x: auto; min-width: 800px;">')
        with open("ui/ux/inventory.html", "w") as f:
            f.write(inv_content)
        print("Patched inventory.html")
except Exception as e:
    print(e)

# Patch employee-profile.html
try:
    with open("ui/ux/employee-profile.html", "r") as f:
        ep_content = f.read()
    if "Sl.no" not in ep_content:
        ep_content = ep_content.replace('<th>Status</th>', '<th>Status</th>\n                    <th>Usage</th>\n                    <th>Warranty</th>\n                    <th>Sl.no</th>')
        ep_content = ep_content.replace('<td><span class="status-badge status-active">Assigned</span></td>', '<td><span class="status-badge status-active">Assigned</span></td>\n                    <td>In Use</td>\n                    <td>Yes</td>\n                    <td>1A2B3C</td>')
        ep_content = ep_content.replace('<div class="table-responsive">', '<div class="table-responsive" style="overflow-x: auto; min-width: 800px;">')
        with open("ui/ux/employee-profile.html", "w") as f:
            f.write(ep_content)
        print("Patched employee-profile.html")
except Exception as e:
    print(e)

