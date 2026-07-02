import os
import re

# 1. Update templates/assets-new.html
with open('templates/assets-new.html', 'r') as f:
    t = f.read()
# Remove sl_no field
t = re.sub(r'<div class="form-group">\s*<label>Sl\.no\s*<span class="required">\*</span></label>\s*<input[^>]+name="sl_no"[^>]+>\s*</div>', '', t)
# Make serial_number required and update label
t = t.replace('Serial Number (auto if blank)</label>', 'Serial Number *</label>')
t = re.sub(r'(<input[^>]+name="serial_number"[^>]*?)>', r'\1 required>', t)
# Fix any duplicate required
t = t.replace('required required>', 'required>')
with open('templates/assets-new.html', 'w') as f:
    f.write(t)

# 2. Update templates/assets-edit.html
with open('templates/assets-edit.html', 'r') as f:
    t = f.read()
# Remove sl_no field
t = re.sub(r'<div class="form-group">\s*<label>Sl\.no\s*<span class="required">\*</span></label>\s*<input[^>]+name="sl_no"[^>]+>\s*</div>', '', t)
# Make serial_number required
t = t.replace('Serial Number (auto if blank)</label>', 'Serial Number *</label>')
t = re.sub(r'(<input[^>]+name="serial_number"[^>]*?)>', r'\1 required>', t)
t = t.replace('required required>', 'required>')
with open('templates/assets-edit.html', 'w') as f:
    f.write(t)

# 3. Update templates/asset-detail.html
with open('templates/asset-detail.html', 'r') as f:
    t = f.read()
t = re.sub(r'<div class="info-cell">\s*<div class="info-label">Sl\.no</div>\s*<div class="info-value">.*?</div>\s*</div>', '', t)
with open('templates/asset-detail.html', 'w') as f:
    f.write(t)

# 4. Update templates/inventory.html
with open('templates/inventory.html', 'r') as f:
    t = f.read()
t = t.replace('<th>Sl.no</th>\n', '')
t = re.sub(r'<td>\{\{\s*asset\.sl_no\s*or\s*"—"\s*\}\}</td>\n', '', t)
with open('templates/inventory.html', 'w') as f:
    f.write(t)

# 5. Update templates/employee-profile.html
with open('templates/employee-profile.html', 'r') as f:
    t = f.read()
t = t.replace('<th>Sl.no</th>\n', '')
t = t.replace('<th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Sl.no</th>\n', '')
t = re.sub(r'<td[^>]*>\{\{\s*a\.sl_no\s*or\s*"—"\s*\}\}</td>\n', '', t)
with open('templates/employee-profile.html', 'w') as f:
    f.write(t)

# 6. Update server.js
with open('server.js', 'r') as f:
    s = f.read()
s = s.replace('!sl_no || !monitor_make', '!monitor_make')
s = s.replace('!in_warranty_status) {', '!in_warranty_status || !serial_number) {')

# Remove auto generation
auto_gen = """        if (!serial_number) {
            serial_number = `SN-${uuidv4().substring(0, 8).toUpperCase()}`;
        } else {"""
new_gen = """        if (serial_number) {"""
s = s.replace(auto_gen, new_gen)
s = s.replace('error: \'Serial number already exists. Leave it blank to auto-generate one, or enter a different serial number.\'', 'error: \'Serial number already exists. Please enter a different serial number.\'')
s = s.replace('errorMsg = \'Serial number already exists. Leave it blank to auto-generate one, or enter a different serial number.\'', 'errorMsg = \'Serial number already exists. Please enter a different serial number.\'')

with open('server.js', 'w') as f:
    f.write(s)

# 7. Update ui/ux mockups
# ui/ux/gen_pages.py
with open('ui/ux/gen_pages.py', 'r') as f:
    t = f.read()
t = re.sub(r'<div class="form-group">\s*<label>Sl\.no\s*<span class="required">\*</span></label>\s*<input[^>]+placeholder="Serial Number"[^>]+>\s*</div>', '', t)
with open('ui/ux/gen_pages.py', 'w') as f:
    f.write(t)
os.system("cd ui/ux && python3 gen_pages.py")

# ui/ux/asset-detail.html
with open('ui/ux/asset-detail.html', 'r') as f:
    t = f.read()
t = re.sub(r'<div class="form-group">\s*<label>Sl\.no\s*<span class="required">\*</span></label>\s*<div[^>]*>AST-XXXXX-SN</div>\s*</div>', '', t)
with open('ui/ux/asset-detail.html', 'w') as f:
    f.write(t)

# ui/ux/inventory.html
with open('ui/ux/inventory.html', 'r') as f:
    t = f.read()
t = t.replace('<th>Sl.no</th>\n', '')
t = t.replace('<td>1A2B3C</td>\n', '')
t = t.replace('<td>X9Y8Z7</td>\n', '')
t = t.replace('<td>P5Q6R7</td>\n', '')
with open('ui/ux/inventory.html', 'w') as f:
    f.write(t)

# ui/ux/employee-profile.html
with open('ui/ux/employee-profile.html', 'r') as f:
    t = f.read()
t = t.replace('<th>Sl.no</th>\n', '')
t = t.replace('<th style="text-align:left; padding:8px 12px; font-size:11px; color:var(--text-disabled); font-family:var(--font-data); text-transform:uppercase;">Sl.no</th>\n', '')
t = t.replace('<td>1A2B3C</td>\n', '')
with open('ui/ux/employee-profile.html', 'w') as f:
    f.write(t)

print("Sl.no removed and serial_number updated successfully.")
