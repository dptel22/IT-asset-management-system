import re

with open('templates/inventory.html', 'r') as f:
    inv = f.read()

# Extract <head>
head_match = re.search(r'(<head>.*?</head>)', inv, re.DOTALL)
head_content = head_match.group(1)
# Replace title
head_content = head_content.replace('Asset Inventory', 'Archive')

# The archive template should look like this:
archive_html = f"""<!DOCTYPE html>
<html lang="en">
{head_content}
<body>
  <div class="app-container">
    {{% include "partials/sidebar.html" %}}
    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumb">
          System / Archive
          <span class="top-bar-date" id="current-date"></span>
        </div>
        <div class="top-bar-actions">
          <div style="position: relative; cursor: pointer; color: var(--text-secondary);">
            <i data-lucide="bell" stroke-width="1.5"></i>
          </div>
        </div>
      </header>

      <!-- Content Area -->
      <div class="content-area">
        <div class="page-header fade-up delay-1">
          <h1 class="page-title">Archived Assets</h1>
          <p class="page-subtitle">Assets removed from active inventory.</p>
        </div>

        <div class="table-container fade-up delay-3">
          <table class="table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Serial</th>
                <th>Category</th>
                <th>Archived By</th>
                <th>Date</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {{% for a in archived_assets %}}
              <tr>
                <td>
                  <div class="td-id">{{{{ a.asset_tag }}}}</div>
                  <div class="td-name">{{{{ a.brand }}}} {{{{ a.model }}}}</div>
                </td>
                <td class="td-meta">{{{{ a.serial_number }}}}</td>
                <td><span class="badge badge-neutral">{{{{ a.category }}}}</span></td>
                <td>{{{{ a.archived_by_name or '—' }}}}</td>
                <td class="td-meta">{{{{ a.archived_at | datestr }}}}</td>
                <td class="td-meta">{{{{ a.reason or '—' }}}}</td>
              </tr>
              {{% else %}}
              <tr><td colspan="6" class="td-meta" style="text-align:center;padding:32px;">No archived assets yet</td></tr>
              {{% endfor %}}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
  <script>
    if(window.lucide) lucide.createIcons();
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', {{ weekday: 'long', month: 'short', day: 'numeric' }});
  </script>
</body>
</html>
"""

with open('templates/archive.html', 'w') as f:
    f.write(archive_html)

print("Fixed templates/archive.html")
