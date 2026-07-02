import os
import re

template_dir = os.path.dirname(__file__)
partials_dir = os.path.join(template_dir, "partials")

if not os.path.exists(partials_dir):
    os.makedirs(partials_dir)

sidebar_content = """
<aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon"></div>
        <span>CognixAsset</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <a href="/dashboard" class="nav-item">
        <i data-lucide="layout-dashboard"></i>
        <span>Dashboard</span>
      </a>

      {% if user.role == 'employee' %}
        <a href="/profile" class="nav-item">
          <i data-lucide="user"></i>
          <span>My Profile</span>
        </a>
        <a href="/users/new" class="nav-item">
          <i data-lucide="user-plus"></i>
          <span>Create New User</span>
        </a>
        
        <div class="nav-section">Assets</div>
        <a href="/inventory" class="nav-item">
          <i data-lucide="monitor"></i>
          <span>My Assets</span>
        </a>
        <a href="/requests/new" class="nav-item">
          <i data-lucide="plus-circle"></i>
          <span>Add Asset Request</span>
        </a>
        <a href="/requests" class="nav-item">
          <i data-lucide="file-text"></i>
          <span>My Asset Requests</span>
        </a>

        <div class="nav-section">Issues</div>
        <a href="/maintenance" class="nav-item">
          <i data-lucide="alert-circle"></i>
          <span>My Issues</span>
        </a>
        <a href="/maintenance/new" class="nav-item">
          <i data-lucide="plus"></i>
          <span>Raise New Issue</span>
        </a>

        <div class="nav-section">Tasks</div>
        <a href="/tasks" class="nav-item">
          <i data-lucide="check-square"></i>
          <span>My Tasks</span>
        </a>

      {% else %}
        <a href="/employees" class="nav-item">
          <i data-lucide="users"></i>
          <span>Employee Directory</span>
        </a>
        <a href="/users/new" class="nav-item">
          <i data-lucide="user-plus"></i>
          <span>Add Employee</span>
        </a>

        <div class="nav-section">Assets</div>
        <a href="/inventory" class="nav-item">
          <i data-lucide="monitor"></i>
          <span>All Assets</span>
        </a>
        <a href="/assets/new" class="nav-item">
          <i data-lucide="plus-square"></i>
          <span>Add Asset</span>
        </a>
        <a href="/transfers" class="nav-item">
          <i data-lucide="arrow-left-right"></i>
          <span>Transfers</span>
        </a>
        <a href="/maintenance" class="nav-item">
          <i data-lucide="tool"></i>
          <span>Maintenance</span>
        </a>

        <div class="nav-section">Workflows</div>
        <a href="/requests" class="nav-item">
          <i data-lucide="clipboard-list"></i>
          <span>Asset Requests</span>
        </a>
        <a href="/tasks" class="nav-item">
          <i data-lucide="check-square"></i>
          <span>Task Management</span>
        </a>
        <a href="/approvals" class="nav-item">
          <i data-lucide="check-circle"></i>
          <span>Approvals</span>
        </a>

        <div class="nav-section">System</div>
        <a href="/reports" class="nav-item">
          <i data-lucide="bar-chart-2"></i>
          <span>Reports</span>
        </a>
        {% if user.role == 'super_admin' %}
          <a href="/archive" class="nav-item">
            <i data-lucide="archive"></i>
            <span>Archive</span>
          </a>
        {% endif %}
      {% endif %}
      
      <div class="nav-section">Notifications</div>
      <a href="/notifications" class="nav-item">
        <i data-lucide="bell"></i>
        <span>Notifications</span>
        <span class="badge">0</span>
      </a>
    </nav>
</aside>
"""

with open(os.path.join(partials_dir, 'sidebar.html'), 'w', encoding='utf-8') as f:
    f.write(sidebar_content.strip())
print("Created partials/sidebar.html")

for filename in os.listdir(template_dir):
    if not filename.endswith('.html') or filename == 'index.html': # Skip login
        continue
        
    filepath = os.path.join(template_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Need to match the entire aside element.
    # It might span multiple lines.
    content = re.sub(r'<aside class="sidebar">.*?</aside>', '{% include "partials/sidebar.html" %}', content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filename}")
