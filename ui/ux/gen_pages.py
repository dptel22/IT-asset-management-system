import os
import re

base_file = "/Users/rithanyamagesh/Desktop/antigravity/ui/ux/employee-dashboard.html"

with open(base_file, 'r', encoding='utf-8') as f:
    base_html = f.read()

def create_page(filename, main_content_html):
    start_idx = base_html.find('<div class="content-area">')
    end_idx = base_html.find('</main>', start_idx)
    
    prefix = base_html[:start_idx + len('<div class="content-area">')]
    suffix = '\n      </div>\n    ' + base_html[end_idx:]
    
    # We need to strip <div class="main-content"> ... </div> from main_content_html
    # because it will break the layout.
    import re
    content_match = re.search(r'<div class="main-content">(.*)</div>\s*<style>', main_content_html, re.DOTALL)
    if content_match:
        inner_content = content_match.group(1)
        styles_scripts = main_content_html[content_match.end(1) + 6:] # </div> length
        main_content_html = inner_content + '\n' + styles_scripts
    else:
        main_content_html = main_content_html.replace('<div class="main-content">', '')
        
    new_html = prefix + '\n' + main_content_html + suffix
                      
    path = os.path.join("/Users/rithanyamagesh/Desktop/antigravity/ui/ux", filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Created {filename}")

# 1. add-user.html
add_user_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <div class="breadcrumb">
                <a href="employee-dashboard.html">Home</a>
                <i data-lucide="chevron-right" width="14"></i>
                <span>Create New User</span>
              </div>
              <h1 class="page-title">Create New User</h1>
              <p class="text-secondary">Onboard a new employee to the system.</p>
            </div>
          </div>

          <div class="card form-card fade-up">
            <form id="addUserForm" onsubmit="event.preventDefault(); showToast('User created successfully. An invite has been sent to their email.', 'success'); this.reset();">
              <div class="form-grid">
                <div class="form-group">
                  <label>Full Name <span class="required">*</span></label>
                  <input type="text" class="form-control" required placeholder="Enter full name">
                </div>
                
                <div class="form-group">
                  <label>Email Address <span class="required">*</span></label>
                  <input type="email" class="form-control" required placeholder="name@company.com">
                </div>

                <div class="form-group">
                  <label>Phone Number <span class="required">*</span></label>
                  <input type="tel" class="form-control" required placeholder="+91 xxxxxxxxxx">
                </div>

                <div class="form-group">
                  <label>Department <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="" disabled selected>Select Department</option>
                    <option value="IT">IT</option>
                    <option value="HR">HR</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Finance">Finance</option>
                    <option value="Operations">Operations</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Designation <span class="required">*</span></label>
                  <input type="text" class="form-control" required placeholder="e.g. Software Engineer">
                </div>

                <div class="form-group">
                  <label>Role <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="employee" selected>Employee</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Date of Joining <span class="required">*</span></label>
                  <input type="date" class="form-control" required>
                </div>

                <div class="form-group">
                  <label>Reporting Manager <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="" disabled selected>Select Manager</option>
                    <option value="manager1">Ravi Kumar</option>
                    <option value="manager2">Priya Sharma</option>
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

              <div class="form-actions mt-4">
                <button type="submit" class="btn btn-primary">Send Invite Email</button>
              </div>
            </form>
          </div>
        </div>
"""

# 2. add-asset.html
add_asset_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <div class="breadcrumb">
                <a href="employee-dashboard.html">Assets</a>
                <i data-lucide="chevron-right" width="14"></i>
                <span>Add Asset Request</span>
              </div>
              <h1 class="page-title">Add Asset Request</h1>
              <p class="text-secondary">Request a new asset for your work.</p>
            </div>
          </div>

          <div class="card form-card fade-up">
            <form id="addAssetForm" onsubmit="event.preventDefault(); showToast('Asset request submitted successfully.', 'success'); this.reset();">
              <div class="form-group">
                <label>Asset Type <span class="required">*</span></label>
                <select class="form-control" required>
                  <option value="" disabled selected>Select Asset Type</option>
                  <option value="Laptop">Laptop</option>
                  <option value="Monitor">Monitor</option>
                  <option value="Phone">Phone</option>
                  <option value="Desk">Desk</option>
                  <option value="Chair">Chair</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div class="form-group mt-3">
                <label>Reason / Justification <span class="required">*</span></label>
                <textarea class="form-control" rows="4" required placeholder="Why do you need this asset?"></textarea>
              </div>

              <!-- Collapsible Additional Details -->
              <div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border);">
                <button type="button" onclick="const e = document.getElementById('extra-fields'); e.style.display = e.style.display === 'none' ? 'block' : 'none';" style="background:none; border:none; color:var(--text-secondary); display:flex; align-items:center; gap:8px; cursor:pointer; font-family:var(--font-ui); font-size:14px; padding:0;">
                  <i data-lucide="more-horizontal" width="16"></i> Show Additional Details
                </button>
                <div id="extra-fields" style="display:none; margin-top:16px;">
                  <div class="form-grid">
<div class="form-group">
                  <label>Priority <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="Low">Low</option>
                    <option value="Medium" selected>Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Required By Date</label>
                  <input type="date" class="form-control">
                </div>
              </div>

              <div class="form-group mt-3">
                <label>Additional Notes</label>
                <textarea class="form-control" rows="2" placeholder="Any specific requirements..."></textarea>
              </div>

              
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

              <div class="form-actions mt-4">
                <button type="submit" class="btn btn-primary">Submit Request</button>
              </div>
            </form>
          </div>
        </div>
"""

# 3. add-issue.html
add_issue_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <div class="breadcrumb">
                <a href="employee-dashboard.html">Issues</a>
                <i data-lucide="chevron-right" width="14"></i>
                <span>Raise New Issue</span>
              </div>
              <h1 class="page-title">Raise New Issue</h1>
              <p class="text-secondary">Report an issue with your assets or workspace.</p>
            </div>
          </div>

          <div class="card form-card fade-up">
            <form id="addIssueForm" onsubmit="event.preventDefault(); showToast('Issue raised successfully. You will be notified on updates.', 'success'); this.reset();">
              <div class="form-group">
                <label>Issue Title <span class="required">*</span></label>
                <input type="text" class="form-control" required placeholder="Brief description of the problem">
              </div>

              <!-- Collapsible Additional Details -->
              <div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border);">
                <button type="button" onclick="const e = document.getElementById('extra-fields'); e.style.display = e.style.display === 'none' ? 'block' : 'none';" style="background:none; border:none; color:var(--text-secondary); display:flex; align-items:center; gap:8px; cursor:pointer; font-family:var(--font-ui); font-size:14px; padding:0;">
                  <i data-lucide="more-horizontal" width="16"></i> Show Additional Details
                </button>
                <div id="extra-fields" style="display:none; margin-top:16px;">
                  <div class="form-grid">
<div class="form-group">
                  <label>Category <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="" disabled selected>Select Category</option>
                    <option value="IT Support">IT Support</option>
                    <option value="HR">HR</option>
                    <option value="Facilities">Facilities</option>
                    <option value="Finance">Finance</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Priority <span class="required">*</span></label>
                  <select class="form-control" required>
                    <option value="Low">Low</option>
                    <option value="Medium" selected>Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>
              </div>

              <div class="form-group mt-3">
                <label>Description <span class="required">*</span></label>
                <textarea class="form-control" rows="5" required placeholder="Detailed explanation of the issue..."></textarea>
              </div>

              <div class="form-grid mt-3">
                <div class="form-group">
                  <label>Related Asset (Optional)</label>
                  <select class="form-control">
                    <option value="">None</option>
                    <option value="asset1">Dell XPS 15 (Laptop)</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Attach Screenshot/File (Max 5MB)</label>
                  <input type="file" class="form-control">
                </div>
              </div>

              
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

              <div class="form-actions mt-4">
                <button type="submit" class="btn btn-primary">Raise Issue</button>
              </div>
            </form>
          </div>
        </div>
"""

# 4. profile.html
profile_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <h1 class="page-title">My Profile</h1>
              <p class="text-secondary">View and manage your personal information.</p>
            </div>
            <div class="header-actions">
              <button class="btn btn-primary" onclick="toggleEdit()"><i data-lucide="edit"></i> Edit Profile</button>
            </div>
          </div>

          <div class="profile-layout" style="display: grid; grid-template-columns: 300px 1fr; gap: 24px; align-items: start;">
            <!-- Left sidebar -->
            <div class="card fade-up text-center">
              <div style="width: 120px; height: 120px; border-radius: 50%; background: var(--border-glow); margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; font-size: 3rem; font-weight: 700;">MI</div>
              <h3>Myra Iyer</h3>
              <p class="text-secondary" style="margin-bottom: 16px;">Software Engineer</p>
              <div class="status-badge status-active" style="display: inline-block;">Active</div>
            </div>

            <!-- Right content -->
            <div class="card fade-up" style="animation-delay: 100ms;">
              <form id="profileForm">
                <h3 class="card-title" style="margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 12px;">Personal Information</h3>
                
                <div class="form-grid">
                  <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" class="form-control" value="Myra Iyer" disabled>
                  </div>
                  <div class="form-group">
                    <label>Employee ID</label>
                    <input type="text" class="form-control" value="EMP-0145" disabled>
                  </div>
                  <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" class="form-control" value="myra.iyer0@cognixasset.com" disabled>
                  </div>
                  <div class="form-group">
                    <label>Phone Number</label>
                    <input type="tel" class="form-control" value="+91 9876543210" disabled id="phoneInput">
                  </div>
                  <div class="form-group">
                    <label>Emergency Contact</label>
                    <input type="tel" class="form-control" value="+91 8765432109" disabled id="emergencyInput">
                  </div>
                  <div class="form-group">
                    <label>Address</label>
                    <input type="text" class="form-control" value="Bengaluru, India" disabled id="addressInput">
                  </div>
                </div>

                <h3 class="card-title" style="margin-top: 32px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 12px;">Company Information</h3>
                
                <div class="form-grid">
                  <div class="form-group">
                    <label>Department</label>
                    <input type="text" class="form-control" value="Engineering" disabled>
                  </div>
                  <div class="form-group">
                    <label>Designation</label>
                    <input type="text" class="form-control" value="Software Engineer" disabled>
                  </div>
                  <div class="form-group">
                    <label>Date of Joining</label>
                    <input type="text" class="form-control" value="2022-06-15" disabled>
                  </div>
                  <div class="form-group">
                    <label>Reporting Manager</label>
                    <input type="text" class="form-control" value="Ravi Kumar" disabled>
                  </div>
                </div>

                <div class="form-actions mt-4" id="saveActions" style="display: none;">
                  <button type="button" class="btn btn-secondary" onclick="toggleEdit()">Cancel</button>
                  <button type="button" class="btn btn-primary" onclick="saveProfile()">Save Changes</button>
                </div>
              </form>
            </div>
          </div>
        </div>
        <style>
          .form-control:disabled {
            background-color: var(--bg-surface);
            color: var(--text-secondary);
            border-color: var(--border);
            cursor: not-allowed;
          }
        </style>
        <script>
          let isEditing = false;
          function toggleEdit() {
            isEditing = !isEditing;
            document.getElementById('phoneInput').disabled = !isEditing;
            document.getElementById('emergencyInput').disabled = !isEditing;
            document.getElementById('addressInput').disabled = !isEditing;
            document.getElementById('saveActions').style.display = isEditing ? 'flex' : 'none';
          }
          function saveProfile() {
            showToast('Profile updated successfully!', 'success');
            toggleEdit();
          }
        </script>
"""

# 5. tasks.html
tasks_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <h1 class="page-title">My Tasks</h1>
              <p class="text-secondary">Track and manage your assigned tasks.</p>
            </div>
            <div class="header-actions">
              <div class="search-bar">
                <i data-lucide="search" width="18"></i>
                <input type="text" placeholder="Search tasks...">
              </div>
            </div>
          </div>

          <div class="card table-card fade-up">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Task ID</th>
                    <th>Task Name</th>
                    <th>Assigned By</th>
                    <th>Priority</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th style="width: 100px;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="font-data">TSK-1001</td>
                    <td style="font-weight: 500;">Update Q3 Financial Report</td>
                    <td>Ravi Kumar</td>
                    <td><span class="status-badge status-critical">High</span></td>
                    <td>2024-10-15</td>
                    <td>
                      <select class="form-control" style="padding: 4px 8px; height: auto;">
                        <option value="todo">To Do</option>
                        <option value="in_progress" selected>In Progress</option>
                        <option value="done">Done</option>
                      </select>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button class="btn btn-icon" title="View details"><i data-lucide="eye"></i></button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td class="font-data">TSK-1002</td>
                    <td style="font-weight: 500;">Submit timesheets</td>
                    <td>Priya Sharma</td>
                    <td><span class="status-badge status-warning">Medium</span></td>
                    <td class="text-critical" style="font-weight: 600;">2024-10-01</td>
                    <td>
                      <span class="status-badge status-critical">Overdue</span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button class="btn btn-icon" title="View details"><i data-lucide="eye"></i></button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
"""

create_page("add-user.html", add_user_html)

create_page("add-asset.html", add_asset_html)

assets_edit_html = add_asset_html.replace('Add New Asset', 'Edit Asset').replace('Register a new hardware or software asset', 'Update details for an existing asset').replace('Submit Asset', 'Save Changes')
# Set some dummy values
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter brand (e.g. Dell, Apple)">', '<input type="text" class="form-control" required value="Apple">')
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter model name">', '<input type="text" class="form-control" required value="MacBook Pro 16">')
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter unique serial number">', '<input type="text" class="form-control" required value="C02XX123456">')

create_page("assets-edit.html", assets_edit_html)

create_page("add-issue.html", add_issue_html)
create_page("profile.html", profile_html)
create_page("tasks.html", tasks_html)
