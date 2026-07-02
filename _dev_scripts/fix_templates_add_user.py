with open('ui/ux/add-user.html', 'r') as f:
    content = f.read()

# Replace offline form with live form logic
old_form = '<form id="addUserForm" onsubmit="event.preventDefault(); showToast(\'User created successfully.\', \'success\'); setTimeout(() => window.location.href=\'employee-directory.html\', 1000);">'
new_form = '<form id="addUserForm" method="POST" action="/employees">\n              {% if error %}\n              <div style="background:var(--status-critical); color:white; padding:12px; border-radius:var(--radius-input); margin-bottom:20px; font-family:var(--font-ui); font-size:14px;">\n                {{ error }}\n              </div>\n              {% endif %}'

content = content.replace(old_form, new_form)
content = content.replace('onsubmit="event.preventDefault(); showToast(\'User created successfully. An invite has been sent to their email.\', \'success\'); setTimeout(() => window.location.href=\'employee-directory.html\', 1000);"', 'method="POST" action="/employees"')

# Add names to inputs
content = content.replace('<input type="tel" class="form-control" placeholder="+91 xxxxxxxxxx">',
                          '<input type="tel" name="phone" class="form-control" placeholder="+91 xxxxxxxxxx">')
content = content.replace('<input type="text" class="form-control" placeholder="e.g. Software Engineer">',
                          '<input type="text" name="designation" class="form-control" placeholder="e.g. Software Engineer">')
content = content.replace('<input type="date" class="form-control">',
                          '<input type="date" name="join_date" class="form-control">')
content = content.replace('<select class="form-control">',
                          '<select name="manager_id" class="form-control">')

with open('templates/add-user.html', 'w') as f:
    f.write(content)
