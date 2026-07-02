import re

with open('templates/assets-edit.html', 'r') as f:
    content = f.read()

# 1. Remove `required` from the fields inside the optional block
content = content.replace('name="monitor_make" required', 'name="monitor_make"')
content = content.replace('name="monitor_serial_no" required', 'name="monitor_serial_no"')
content = content.replace('name="asset_owner_pl_no" required', 'name="asset_owner_pl_no"')
content = content.replace('name="asset_usage_status" required', 'name="asset_usage_status"')
content = content.replace('name="in_warranty_status" required', 'name="in_warranty_status"')

# 2. Add Status and Warranty back to the main grid!
# Find where Purchase Cost is.
purchase_cost_block = """              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Purchase Cost (₹)</label>
                <input type="number" name="purchase_cost" step="0.01" value="{{ asset.purchase_cost }}" style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-data); font-size:14px; outline:none;">
              </div>"""

status_warranty_html = """
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

if purchase_cost_block in content and "Status (Usage) *" not in content:
    content = content.replace(purchase_cost_block, purchase_cost_block + status_warranty_html)
    
with open('templates/assets-edit.html', 'w') as f:
    f.write(content)

