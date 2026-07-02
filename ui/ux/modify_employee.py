import re

def modify_dashboard_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <h1 class="page-title">Employee Dashboard</h1>
              <p class="text-secondary">Welcome back, here is your personal overview.</p>
            </div>
            <div class="header-actions">
              <button class="btn btn-primary"><i data-lucide="plus"></i> New Request</button>
            </div>
          </div>

          <!-- ROW 1: KPI Cards -->
          <div class="kpi-grid">
            <div class="card kpi-card fade-up" style="animation-delay: 100ms;">
              <div class="kpi-header">
                <h3 class="kpi-title">Tasks Assigned to Me</h3>
                <div class="kpi-icon" style="background: rgba(168, 200, 255, 0.1); color: var(--accent-ice);">
                  <i data-lucide="check-square"></i>
                </div>
              </div>
              <div class="kpi-value">12</div>
            </div>

            <div class="card kpi-card fade-up" style="animation-delay: 150ms;">
              <div class="kpi-header">
                <h3 class="kpi-title">Tasks Completed</h3>
                <div class="kpi-icon" style="background: rgba(34, 197, 94, 0.1); color: var(--status-active);">
                  <i data-lucide="check-circle"></i>
                </div>
              </div>
              <div class="kpi-value">8</div>
            </div>

            <div class="card kpi-card fade-up" style="animation-delay: 200ms;">
              <div class="kpi-header">
                <h3 class="kpi-title">Tasks Pending</h3>
                <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.1); color: var(--status-warn);">
                  <i data-lucide="clock"></i>
                </div>
              </div>
              <div class="kpi-value">4</div>
            </div>

            <div class="card kpi-card fade-up" style="animation-delay: 250ms;">
              <div class="kpi-header">
                <h3 class="kpi-title">Open Issues</h3>
                <div class="kpi-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--status-critical);">
                  <i data-lucide="alert-triangle"></i>
                </div>
              </div>
              <div class="kpi-value">1</div>
            </div>
            
            <div class="card kpi-card fade-up" style="animation-delay: 300ms;">
              <div class="kpi-header">
                <h3 class="kpi-title">Assets Assigned</h3>
                <div class="kpi-icon" style="background: rgba(244, 162, 38, 0.1); color: var(--accent-amber);">
                  <i data-lucide="monitor"></i>
                </div>
              </div>
              <div class="kpi-value">2</div>
            </div>
          </div>

          <!-- ROW 2: Feed / Tables -->
          <div class="feed-row" style="grid-template-columns: 1fr;">
            
            <div class="card fade-up" style="animation-delay: 400ms;">
              <h3 class="card-title"><i data-lucide="check-square" width="20" height="20" class="text-secondary"></i> My Recent Tasks</h3>
              <div class="table-responsive">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Task Name</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Due Date</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Update Q3 Financial Report</td>
                      <td><span class="status-badge status-critical">High</span></td>
                      <td><span class="status-badge status-warning">In Progress</span></td>
                      <td>2024-10-15</td>
                      <td><button class="btn btn-icon"><i data-lucide="eye"></i></button></td>
                    </tr>
                    <tr>
                      <td>Review Vendor Contracts</td>
                      <td><span class="status-badge status-warning">Medium</span></td>
                      <td><span class="status-badge status-active">Done</span></td>
                      <td>2024-10-10</td>
                      <td><button class="btn btn-icon"><i data-lucide="eye"></i></button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="card fade-up" style="animation-delay: 450ms;">
              <h3 class="card-title"><i data-lucide="alert-circle" width="20" height="20" class="text-secondary"></i> My Recent Issues</h3>
              <div class="table-responsive">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Issue Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Raised On</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Monitor flickers occasionally</td>
                      <td>IT Support</td>
                      <td><span class="status-badge status-warning">Open</span></td>
                      <td>2024-10-12</td>
                      <td><button class="btn btn-icon"><i data-lucide="eye"></i></button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="card fade-up" style="animation-delay: 500ms;">
              <h3 class="card-title"><i data-lucide="monitor" width="20" height="20" class="text-secondary"></i> My Recent Assets</h3>
              <div class="table-responsive">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Asset Name</th>
                      <th>Type</th>
                      <th>Assigned Date</th>
                      <th>Condition</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Dell XPS 15</td>
                      <td>Laptop</td>
                      <td>2023-01-15</td>
                      <td>Good</td>
                      <td><button class="btn btn-icon"><i data-lucide="eye"></i></button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
"""
    start_idx = content.find('<main class="main-content">')
    end_idx = content.find('</main>', start_idx) + len('</main>')
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + new_content + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated content in {filepath}")

modify_dashboard_content("/Users/rithanyamagesh/Desktop/antigravity/ui/ux/employee-dashboard.html")
