with open('templates/add-user.html', 'r') as f:
    content = f.read()

content = content.replace('<input type="email" class="form-control"  placeholder="name@company.com">',
                          '<input type="email" name="email" class="form-control"  placeholder="name@company.com">')

content = content.replace('<select class="form-control" >\n                    <option value="employee" selected>Employee</option>',
                          '<select name="role" class="form-control" >\n                    <option value="employee" selected>Employee</option>')

with open('templates/add-user.html', 'w') as f:
    f.write(content)
