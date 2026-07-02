import re

with open('templates/assets-edit.html', 'r') as f:
    content = f.read()

mandatory_html = """
              <!-- Mandatory Additional Fields -->
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Sl.no *</label>
                <input type="text" name="sl_no" required value="{{ asset.sl_no }}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Monitor Make *</label>
                <input type="text" name="monitor_make" required value="{{ asset.monitor_make }}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Monitor Serial No *</label>
                <input type="text" name="monitor_serial_no" required value="{{ asset.monitor_serial_no }}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Asset Owner and PL No *</label>
                <input type="text" name="asset_owner_pl_no" required value="{{ asset.asset_owner_pl_no }}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Status (Usage) *</label>
                <select name="asset_usage_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="In Use" {% if asset.asset_usage_status == 'In Use' %}selected{% endif %}>In Use</option>
                  <option value="Condemn" {% if asset.asset_usage_status == 'Condemn' %}selected{% endif %}>Condemn</option>
                </select>
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">In Warranty *</label>
                <select name="in_warranty_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="Yes" {% if asset.in_warranty_status == 'Yes' %}selected{% endif %}>Yes</option>
                  <option value="No" {% if asset.in_warranty_status == 'No' %}selected{% endif %}>No</option>
                  <option value="In Maintenance" {% if asset.in_warranty_status == 'In Maintenance' %}selected{% endif %}>In Maintenance</option>
                </select>
              </div>
"""

optional_html = """
            </div>

            <!-- Additional Details Toggle -->
            <div style="margin-top:20px;">
              <button type="button" onclick="document.getElementById('additional-details').style.display = document.getElementById('additional-details').style.display === 'none' ? 'block' : 'none'" style="background:transparent; border:none; color:var(--text-secondary); cursor:pointer; display:flex; align-items:center; gap:8px; font-family:var(--font-ui); font-size:14px; padding:0;">
                <i data-lucide="more-horizontal" width="16"></i> Additional Details
              </button>
            </div>

            <!-- Optional Additional Fields -->
            <div id="additional-details" style="display: none; margin-top: 20px;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
"""

fields = [
    ("system_serial_no", "System Serial No"),
    ("host_name", "Host Name"),
    ("group_name", "Group Name"),
    ("division", "Division"),
    ("user_name", "User Name"),
    ("designation", "Designation"),
    ("ip_address", "IP Address"),
    ("mac_address", "MAC Address"),
    ("network_type", "Network Type (LAN/WAN/WiFi)"),
    ("drona_domain", "Drona / Domain"),
    ("os_version", "OS Version"),
    ("antivirus_status", "Antivirus Status"),
    ("usb_status", "USB Status"),
    ("admin_privilege", "Admin Privilege")
]

for field, label in fields:
    optional_html += f"""
                <div>
                  <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">{label}</label>
                  <input type="text" name="{field}" value="{{{{ asset.{field} }}}}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                </div>"""

optional_html += """
              </div>
            </div>
"""

# Replace in content
target = "            </div>\n            <div style=\"display:flex; gap:12px; margin-top:28px;\">"
new_content = content.replace(target, mandatory_html + optional_html + "\n            <div style=\"display:flex; gap:12px; margin-top:28px;\">")

with open('templates/assets-edit.html', 'w') as f:
    f.write(new_content)

print("assets-edit.html patched.")
