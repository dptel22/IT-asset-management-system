import re

with open('ui/ux/add-asset.html', 'r') as f:
    content = f.read()

# Add the 5 fields to the extra-fields div
extra_fields_html = """
              <div class="form-grid mt-3">
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
                  <input type="text" class="form-control" placeholder="Owner and PL Number">
                </div>
                <div class="form-group">
                  <label>Usage Status</label>
                  <select class="form-control">
                    <option value="" disabled selected>Select Status</option>
                    <option value="New">New</option>
                    <option value="Used">Used</option>
                    <option value="Refurbished">Refurbished</option>
                  </select>
                </div>
                <div class="form-group" style="grid-column: 1 / -1;">
                  <label style="display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" style="width:16px;height:16px;">
                    In warranty
                  </label>
                </div>
              </div>
"""

# Insert it before "Additional Notes" inside extra-fields
target_str = '<div class="form-group mt-3">\n                <label>Additional Notes</label>'
if 'Monitor make' not in content:
    content = content.replace(target_str, extra_fields_html + '\n              ' + target_str)

with open('ui/ux/add-asset.html', 'w') as f:
    f.write(content)

