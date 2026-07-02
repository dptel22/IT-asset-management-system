import re

def patch_sidebar(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 2. Add Logout Button (this time looking for sidebar-footer)
    if 'log-out' not in content:
        logout_html = """
          <div class="nav-section">Account</div>
          <a href="index.html" class="nav-item" style="color: #ef4444; margin-top: 10px;">
            <i data-lucide="log-out"></i>
            <span>Logout</span>
          </a>
        </div>
      </div>

      <div class="sidebar-footer">"""
        
        # Replace the last `</div>\n      </div>\n\n      <div class="sidebar-footer">`
        # Using regex to find the end of sidebar-nav
        pattern = r'(</div>\s*</div>\s*<div class="sidebar-footer">)'
        
        content = re.sub(pattern, logout_html, content, count=1)

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

patch_sidebar('employee-dashboard.html')
patch_sidebar('dashboard.html')
