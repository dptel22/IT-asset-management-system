import os
import re

base_file = "/Users/rithanyamagesh/Desktop/antigravity/ui/ux/dashboard.html"

with open(base_file, 'r', encoding='utf-8') as f:
    base_html = f.read()

approvals_html = """
        <div class="main-content">
          <div class="page-header">
            <div>
              <h1 class="page-title">Approvals</h1>
              <p class="text-secondary">Review and manage pending requests.</p>
            </div>
            <div class="header-actions">
              <div class="search-bar">
                <i data-lucide="search" width="18"></i>
                <input type="text" placeholder="Search approvals...">
              </div>
            </div>
          </div>

          <div class="card table-card fade-up">
            <h3 class="card-title" style="padding: 24px 24px 0;">Pending Approvals</h3>
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Employee Name</th>
                    <th>Request Type</th>
                    <th>Details</th>
                    <th>Submitted On</th>
                    <th style="width: 200px;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><div style="font-weight: 500;">Priya Sharma</div></td>
                    <td><span class="status-badge" style="background: rgba(168, 200, 255, 0.1); color: var(--accent-ice);">Asset Request</span></td>
                    <td>Request for dual monitors (High Priority)</td>
                    <td>2024-10-14</td>
                    <td>
                      <div class="action-buttons" style="justify-content: flex-start;">
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px; height: auto;">Approve</button>
                        <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px; height: auto;">Reject</button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td><div style="font-weight: 500;">Amit Singh</div></td>
                    <td><span class="status-badge" style="background: rgba(168, 200, 255, 0.1); color: var(--accent-ice);">Software Access</span></td>
                    <td>Figma Pro License needed for design team</td>
                    <td>2024-10-13</td>
                    <td>
                      <div class="action-buttons" style="justify-content: flex-start;">
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px; height: auto;">Approve</button>
                        <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px; height: auto;">Reject</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div class="card table-card fade-up" style="animation-delay: 100ms;">
            <h3 class="card-title" style="padding: 24px 24px 0;">Approval History</h3>
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Employee Name</th>
                    <th>Request Type</th>
                    <th>Decision</th>
                    <th>Decided On</th>
                    <th>Decided By</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Ravi Kumar</td>
                    <td>Asset Request (Laptop)</td>
                    <td><span class="status-badge status-active">Approved</span></td>
                    <td>2024-10-12</td>
                    <td>Super Admin</td>
                  </tr>
                  <tr>
                    <td>Neha Gupta</td>
                    <td>Software Access (Adobe CC)</td>
                    <td><span class="status-badge status-critical">Rejected</span></td>
                    <td>2024-10-11</td>
                    <td>Admin</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
"""

start_idx = base_html.find('<main class="main-content">')
end_idx = base_html.find('</main>', start_idx) + len('</main>')

prefix = base_html[:start_idx]
suffix = base_html[end_idx:]

new_html = prefix + approvals_html + suffix
                  
path = os.path.join("/Users/rithanyamagesh/Desktop/antigravity/ui/ux", "approvals.html")
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Created approvals.html")
