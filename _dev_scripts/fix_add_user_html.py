import re

with open('templates/add-user.html', 'r') as f:
    content = f.read()

content = content.replace('<input type="tel" class="form-control" required placeholder="+91 xxxxxxxxxx">',
                          '<input type="tel" name="phone" class="form-control" required placeholder="+91 xxxxxxxxxx">')

content = content.replace('<input type="text" class="form-control" required placeholder="e.g. Software Engineer">',
                          '<input type="text" name="designation" class="form-control" required placeholder="e.g. Software Engineer">')

content = content.replace('<input type="date" class="form-control" required>',
                          '<input type="date" name="join_date" class="form-control" required>')

content = content.replace('<select class="form-control" required>',
                          '<select name="manager_id" class="form-control">') # In case manager didn't have name
                          
with open('templates/add-user.html', 'w') as f:
    f.write(content)
