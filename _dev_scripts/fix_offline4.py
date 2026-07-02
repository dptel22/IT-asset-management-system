import re

# Fix add-user.html offline mockup
with open('ui/ux/add-user.html', 'r') as f:
    content = f.read()

# Remove required attributes to prevent HTML5 validation from blocking submit
content = content.replace('required', '')

# Ensure form has onsubmit
if 'onsubmit' not in content:
    content = content.replace('<form method="POST" action="/employees">', 
                              '<form id="addUserForm" onsubmit="event.preventDefault(); showToast(\'User created successfully.\', \'success\'); setTimeout(() => window.location.href=\'employee-directory.html\', 1000);">')
else:
    content = re.sub(r'onsubmit=".*?"', 'onsubmit="event.preventDefault(); showToast(\'User created successfully. An invite has been sent to their email.\', \'success\'); setTimeout(() => window.location.href=\'employee-directory.html\', 1000);"', content)

with open('ui/ux/add-user.html', 'w') as f:
    f.write(content)

