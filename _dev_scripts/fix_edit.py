import re

with open('templates/assets-edit.html', 'r') as f:
    content = f.read()

# 1. Remove the broken "<!-- Mandatory Additional Fields -->\n\n</div>" block
content = content.replace("              <!-- Mandatory Additional Fields -->\n              \n              </div>\n", "")

# 2. Extract Status (Usage) and In Warranty from the hidden block and insert them right before the grid close.
status_usage = """              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Status (Usage) *</label>
                <select name="asset_usage_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="In Use" {% if asset.asset_usage_status == 'In Use' %}selected{% endif %}>In Use</option>
                  <option value="Condemn" {% if asset.asset_usage_status == 'Condemn' %}selected{% endif %}>Condemn</option>
                </select>
              </div>"""

in_warranty = """              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">In Warranty *</label>
                <select name="in_warranty_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="Yes" {% if asset.in_warranty_status == 'Yes' %}selected{% endif %}>Yes</option>
                  <option value="No" {% if asset.in_warranty_status == 'No' %}selected{% endif %}>No</option>
                  <option value="In Maintenance" {% if asset.in_warranty_status == 'In Maintenance' %}selected{% endif %}>In Maintenance</option>
                </select>
              </div>"""

# Remove them from their current location (if they exist exactly as formatted)
content = re.sub(r'              <div>\n                <label style=".*?">Status \(Usage\) \*</label>\n                <select name="asset_usage_status" required style=".*?">\n                  <option value="">Select\.\.\.</option>\n                  <option value="In Use" \{% if asset.asset_usage_status == \'In Use\' %\}selected\{% endif %\}>In Use</option>\n                  <option value="Condemn" \{% if asset.asset_usage_status == \'Condemn\' %\}selected\{% endif %\}>Condemn</option>\n                </select>\n              </div>\n', '', content)
content = re.sub(r'              <div>\n                <label style=".*?">In Warranty \*</label>\n                <select name="in_warranty_status" required style=".*?">\n                  <option value="">Select\.\.\.</option>\n                  <option value="Yes" \{% if asset.in_warranty_status == \'Yes\' %\}selected\{% endif %\}>Yes</option>\n                  <option value="No" \{% if asset.in_warranty_status == \'No\' %\}selected\{% endif %\}>No</option>\n                  <option value="In Maintenance" \{% if asset.in_warranty_status == \'In Maintenance\' %\}selected\{% endif %\}>In Maintenance</option>\n                </select>\n              </div>\n', '', content)

# Insert them before the first <!-- Additional Details Toggle --> which was right after the main grid
if "            <!-- Additional Details Toggle -->" in content:
    idx = content.find("            <!-- Additional Details Toggle -->")
    # find the previous </div> which closed the grid
    # Wait, the previous block I deleted was exactly before it. I'll just insert it before <!-- Additional Details Toggle -->
    # Actually, we need to put it IN the grid!
    pass

# Wait, let's just do a simpler string replacement.

with open('templates/assets-edit.html', 'w') as f:
    f.write(content)
