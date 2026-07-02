import re

with open('templates/employee-directory.html', 'r') as f:
    content = f.read()

# Replace button
content = content.replace(
    '<button class="btn btn-outline"><i data-lucide="user-plus" width="16"></i> Add Employee</button>',
    '<a href="/employees/new" class="btn btn-outline"><i data-lucide="user-plus" width="16"></i> Add Employee</a>'
)

with open('templates/employee-directory.html', 'w') as f:
    f.write(content)
