import re

with open('templates/employee-dashboard.html', 'r') as f:
    html = f.read()

# Top bar button
html = re.sub(
    r'<button class="btn btn-primary" onclick="openModal\(\'requestModal\'\)">\s*<i data-lucide="plus"></i> New Request\s*</button>',
    r'<a href="/requests/new" class="btn btn-primary">\n            <i data-lucide="plus"></i> Add Asset\n          </a>',
    html, flags=re.IGNORECASE|re.DOTALL
)

html = re.sub(
    r'<button class="btn btn-primary" onclick="openModal\(\'requestModal\'\)">\s*<i data-lucide="plus"></i> New Request\s*</a>',
    r'<a href="/requests/new" class="btn btn-primary">\n            <i data-lucide="plus"></i> Add Asset\n          </a>',
    html, flags=re.IGNORECASE|re.DOTALL
)

# Quick Actions
html = re.sub(
    r'<a href="requests\.html" class="quick-action-btn">\s*<div class="qa-icon" style="background: rgba\(168,200,255,0\.1\); color: var\(--accent-ice\);">\s*<i data-lucide="plus-circle"></i>\s*</div>\s*<div>\s*<div class="qa-label">New Request</div>',
    r'<a href="/requests/new" class="quick-action-btn">\n            <div class="qa-icon" style="background: rgba(168,200,255,0.1); color: var(--accent-ice);">\n              <i data-lucide="plus-circle"></i>\n            </div>\n            <div>\n              <div class="qa-label">Add Asset</div>',
    html, flags=re.IGNORECASE|re.DOTALL
)

html = re.sub(
    r'<a href="add-issue\.html" class="quick-action-btn">',
    r'<a href="/maintenance/new" class="quick-action-btn">',
    html, flags=re.IGNORECASE
)

html = re.sub(
    r'<a href="requests\.html" class="quick-action-btn">\s*<div class="qa-icon" style="background: rgba\(34,197,94,0\.1\); color: var\(--status-active\);">\s*<i data-lucide="history"></i>\s*</div>\s*<div>\s*<div class="qa-label">My History</div>',
    r'<a href="/requests" class="quick-action-btn">\n            <div class="qa-icon" style="background: rgba(34,197,94,0.1); color: var(--status-active);">\n              <i data-lucide="history"></i>\n            </div>\n            <div>\n              <div class="qa-label">Add Asset Requests</div>',
    html, flags=re.IGNORECASE|re.DOTALL
)

# Replace '<!-- Replaced KPI -->' with nothing if I already did it, but I used string replacement which worked?
# Wait, string replacement of hero section worked. Let me check.
with open('templates/employee-dashboard.html', 'w') as f:
    f.write(html)
