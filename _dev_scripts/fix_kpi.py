import re

with open('templates/employee-dashboard.html', 'r') as f:
    content = f.read()

content = re.sub(r'<div class="kpi-value">3</div>\s*<div class="kpi-label">My Assets</div>', 
                 '<div class="kpi-value">{{ stats.total_assets }}</div>\n            <div class="kpi-label">My Assets</div>', content)

content = re.sub(r'<div class="kpi-value">1</div>\s*<div class="kpi-label">Pending Requests</div>', 
                 '<div class="kpi-value">{{ stats.pending_requests }}</div>\n            <div class="kpi-label">Pending Requests</div>', content)

content = re.sub(r'<div class="kpi-value">1</div>\s*<div class="kpi-label">Warranty Expiring</div>', 
                 '<div class="kpi-value">{{ my_issues | length if my_issues else 0 }}</div>\n            <div class="kpi-label">My Issues</div>', content)

with open('templates/employee-dashboard.html', 'w') as f:
    f.write(content)

print("Updated KPIs in employee-dashboard.html")
