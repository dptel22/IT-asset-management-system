import re

with open('templates/employee-dashboard.html', 'r') as f:
    html = f.read()

# Replace /requests/new with /assets/new
html = html.replace('href="/requests/new"', 'href="/assets/new"')

with open('templates/employee-dashboard.html', 'w') as f:
    f.write(html)
