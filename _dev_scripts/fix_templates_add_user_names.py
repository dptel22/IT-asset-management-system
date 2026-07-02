with open('templates/add-user.html', 'r') as f:
    content = f.read()

content = content.replace('<input type="text" class="form-control"  placeholder="Enter full name">',
                          '<input type="text" name="name" class="form-control"  placeholder="Enter full name">')

content = content.replace('<input type="email" class="form-control"  placeholder="e.g. employee@cognixasset.com">',
                          '<input type="email" name="email" class="form-control"  placeholder="e.g. employee@cognixasset.com">')

content = content.replace('<select class="form-control" >\n                    <option value="" disabled selected>Select Department</option>',
                          '<select name="department" class="form-control" >\n                    <option value="" disabled selected>Select Department</option>')

content = content.replace('<select class="form-control" >\n                    <option value="employee" selected>Employee</option>\n                    <option value="admin">Admin</option>',
                          '<select name="role" class="form-control" >\n                    <option value="employee" selected>Employee</option>\n                    <option value="admin">Admin</option>')

with open('templates/add-user.html', 'w') as f:
    f.write(content)
