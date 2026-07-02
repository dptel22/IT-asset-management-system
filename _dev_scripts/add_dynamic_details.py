import re

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Update the Category dropdown to add an ID and the new options
    cat_dropdown_pattern = r'<select name="category" required style=".*?">'
    
    # We will just replace the whole select block
    old_select_block = re.search(r'<select name="category".*?</select>', content, re.DOTALL)
    if old_select_block:
        new_select_block = """<select name="category" id="asset-category" required style="width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none; transition: all 0.2s ease;">
                  <option value="">Select category...</option>
                  <option value="System">System</option>
                  <option value="Printer / MFP & Scan">Printer / MFP & Scan</option>
                  <option value="USB / Storage Device">USB / Storage Device</option>
                  <option value="Laptop">Laptop</option>
                  <option value="Desktop">Desktop</option>
                  <option value="Monitor">Monitor</option>
                  <option value="Network">Network</option>
                  <option value="Server">Server</option>
                  <option value="Mobile">Mobile</option>
                </select>"""
        content = content.replace(old_select_block.group(0), new_select_block)

    # 2. Remove the static Additional Details block
    # It starts with <!-- Additional Details Toggle --> and ends at </div> </div> right before <!-- form actions --> or similar
    # Let's use a regex to grab it.
    start_str = "<!-- Additional Details Toggle -->"
    end_str = '<div style="display:flex; gap:12px; margin-top:28px;">'
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx != -1 and end_idx != -1:
        # replace everything between start_idx and end_idx with our container
        new_container = """<!-- Dynamic Additional Details Container -->
            <div id="dynamic-additional-details-container" style="margin-top:24px; display:none; opacity:0; transition: opacity 0.2s ease, transform 0.2s ease; transform: translateY(-10px);">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px; border-top: 1px solid var(--border); padding-top:24px;">
                    <div style="font-size:10px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.1em; font-family:var(--font-data);" id="dynamic-section-title">ADDITIONAL DETAILS</div>
                </div>
                <div id="dynamic-fields-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <!-- JS will inject fields here -->
                </div>
            </div>

            """
        content = content[:start_idx] + new_container + content[end_idx:]

    # 3. Add the JS logic right before </body>
    js_logic = """
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('asset-category');
    const dynamicContainer = document.getElementById('dynamic-additional-details-container');
    const dynamicTitle = document.getElementById('dynamic-section-title');
    const dynamicGrid = document.getElementById('dynamic-fields-grid');

    const inputStyle = 'width:100%; background:var(--bg-raised); border:1px solid var(--border); color:var(--text-primary); padding:10px 14px; border-radius:var(--radius-input); font-family:var(--font-ui); font-size:14px; outline:none;';
    const labelStyle = 'display:block; font-size:10px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; font-family:var(--font-data);';

    function createInput(name, labelText, type='text', placeholder='', subLabel='') {
      let subHtml = subLabel ? `<span style="opacity:0.6; font-size:9px; text-transform:none; margin-left:4px;">${subLabel}</span>` : '';
      return `
        <div>
          <label style="${labelStyle}">${labelText}${subHtml}</label>
          <input type="${type}" name="${name}" placeholder="${placeholder}" style="${inputStyle}">
        </div>
      `;
    }

    function createSelect(name, labelText, options) {
      let optsHtml = options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
      return `
        <div>
          <label style="${labelStyle}">${labelText}</label>
          <select name="${name}" style="${inputStyle}">
            <option value="">Select...</option>
            ${optsHtml}
          </select>
        </div>
      `;
    }

    const fieldConfigs = {
      'System': () => [
        createInput('system_serial_no', 'System Serial No', 'text', '', '(editing in admin)'),
        createInput('host_name', 'Host Name'),
        createInput('group_name', 'Group Name'),
        createInput('division', 'Division'),
        createInput('user_name', 'Name of User'),
        createInput('designation', 'Designation'),
        createInput('ip_address', 'IP Address'),
        createInput('mac_address', 'MAC Address'),
        createSelect('network', 'Network', ['Drona', 'Internet', 'Project', 'Standalone']),
        createSelect('on_drona', 'On Drona (on domain)', ['Yes', 'No']),
        createInput('os_version', 'OS'),
        createSelect('antivirus', 'Antivirus', ['Yes', 'No']),
        createSelect('usb_status', 'USB Status', ['Enabled', 'Disabled']),
        createSelect('admin_privilege', 'Admin Privilege', ['Yes', 'No'])
      ].join(''),
      'Printer / MFP & Scan': () => [
        createInput('brand_make', 'Brand Make'),
        createInput('printer_model', 'Model'),
        createInput('printer_serial_no', 'Serial No'),
        createInput('printer_ip_mac', 'IP Address / MAC'),
        createSelect('printer_network', 'Network', ['Yes', 'No']),
        createInput('printer_group', 'Group'),
        createInput('printer_division', 'Division'),
        createInput('custodian', 'Custodian'),
        createSelect('amc', 'AMC', ['Yes', 'No'])
      ].join(''),
      'USB / Storage Device': () => [
        createSelect('device_type', 'Device Type', ['Portable', 'Pendrive', 'HDD']),
        createInput('usb_brand_make', 'Brand Make'),
        createInput('usb_model', 'Model'),
        createInput('usb_serial_no', 'Serial No'),
        createInput('capacity', 'Capacity'),
        createInput('usb_group', 'Group'),
        createInput('usb_division', 'Division'),
        createInput('usb_custodian', 'Custodian')
      ].join('')
    };

    if (categorySelect) {
      categorySelect.addEventListener('change', function() {
        const val = this.value;
        if (fieldConfigs[val]) {
          dynamicTitle.textContent = `ADDITIONAL DETAILS — ${val.toUpperCase()}`;
          dynamicGrid.innerHTML = fieldConfigs[val]();
          dynamicContainer.style.display = 'block';
          // trigger reflow for animation
          void dynamicContainer.offsetWidth;
          dynamicContainer.style.opacity = '1';
          dynamicContainer.style.transform = 'translateY(0)';
        } else {
          dynamicContainer.style.opacity = '0';
          dynamicContainer.style.transform = 'translateY(-10px)';
          setTimeout(() => {
            dynamicContainer.style.display = 'none';
            dynamicGrid.innerHTML = '';
          }, 200);
        }
      });
      // trigger once on load if there's a pre-selected value
      categorySelect.dispatchEvent(new Event('change'));
    }
  });
</script>
"""
    # Insert before </body>
    content = content.replace("</body>", js_logic + "\n</body>")
    
    with open(filepath, 'w') as f:
        f.write(content)
        
update_file('templates/assets-new.html')
update_file('ui/ux/assets-new.html')
try:
    update_file('ui/ux/add-asset.html')
except FileNotFoundError:
    pass

print("Done")
