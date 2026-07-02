import re

def fix_server():
    with open('server.js', 'r') as f:
        content = f.read()

    # Remove the bad validation block
    pattern = r"    if \(!monitor_make \|\| !monitor_serial_no.*?return res\.render\('assets-new\.html', \{ error: 'Please fill out all mandatory fields\.', values: req\.body, req \}\);\n    \}"
    content = re.sub(pattern, "", content, flags=re.DOTALL)

    # And for assets/:id/edit if there's any
    pattern2 = r"    if \(!monitor_make \|\| !monitor_serial_no.*?return res\.render\('assets-edit\.html', \{ error: 'Please fill out all mandatory fields\.', asset, req \}\);\n    \}"
    content = re.sub(pattern2, "", content, flags=re.DOTALL)

    with open('server.js', 'w') as f:
        f.write(content)
    print("Fixed server.js")

def fix_html(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # 1. We will replace the whole <!-- Mandatory Additional Fields --> block
    # and put back ONLY asset_usage_status and in_warranty_status as standard fields.
    
    start_str = "<!-- Mandatory Additional Fields -->"
    end_str = "</div> <!-- Close grid -->"
    
    if start_str in content and end_str in content:
        start_idx = content.find(start_str)
        end_idx = content.find(end_str, start_idx) + len(end_str)
        
        replacement = """
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">Status (Usage) *</label>
                <select name="asset_usage_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="In Use" {% set curr_aus = values.asset_usage_status if values else (asset.asset_usage_status if asset else '') %} {% if curr_aus == 'In Use' %}selected{% endif %}>In Use</option>
                  <option value="Condemn" {% if curr_aus == 'Condemn' %}selected{% endif %}>Condemn</option>
                </select>
              </div>
              <div>
                <label style="display:block; font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);">In Warranty *</label>
                <select name="in_warranty_status" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;">
                  <option value="">Select...</option>
                  <option value="Yes" {% set curr_warr = values.in_warranty_status if values else (asset.in_warranty_status if asset else '') %} {% if curr_warr == 'Yes' %}selected{% endif %}>Yes</option>
                  <option value="No" {% if curr_warr == 'No' %}selected{% endif %}>No</option>
                  <option value="In Maintenance" {% if curr_warr == 'In Maintenance' %}selected{% endif %}>In Maintenance</option>
                </select>
              </div>
            </div> <!-- Close grid -->
"""
        content = content[:start_idx] + replacement + content[end_idx:]
        print(f"Removed redundant fields from {filename}")
    
    # 2. Add sl_no and asset_owner_pl_no to System category in JS
    js_sys = "createInput('system_serial_no', 'System Serial No', 'text', '', '(editing in admin)'),"
    if js_sys in content and "createInput('sl_no'" not in content:
        content = content.replace(js_sys, js_sys + "\n        createInput('sl_no', 'Sl.no'),\n        createInput('asset_owner_pl_no', 'Asset Owner PL No'),")
        
    # 3. Add Monitor category to fieldConfigs
    if "'Monitor': () => [" not in content:
        monitor_js = """'Monitor': () => [
        createInput('monitor_make', 'Monitor Make'),
        createInput('monitor_serial_no', 'Monitor Serial No')
      ].join(''),"""
        content = content.replace("'Printer / MFP & Scan':", monitor_js + "\n      'Printer / MFP & Scan':")

    with open(filename, 'w') as f:
        f.write(content)
    print(f"Fixed {filename}")

fix_server()
fix_html('templates/assets-new.html')
fix_html('templates/assets-edit.html')
