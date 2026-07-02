import re

with open('server.js', 'r') as f:
    content = f.read()

# Replace:
# let { name, email, department, role, location } = req.body;
# location = location || "Head Office";
# with:
# let { name, email, department, role, location, phone, designation, join_date, manager_id } = req.body;
# location = location || "Head Office";

content = content.replace(
    'let { name, email, department, role, location } = req.body;',
    'let { name, email, department, role, location, phone, designation, join_date, manager_id } = req.body;'
)

# Replace the INSERT query:
# await run(`INSERT INTO employees (id, user_id, name, email, department, designation, location, join_date, status, emergency_contact, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, 
#           [emp_id, user_id, name, email, department, role, location, new Date().toISOString(), "Active", null, null]);

# Wait, the INSERT query uses `role` for designation! 
# Let's change it to use `phone`, `designation`, `join_date` (with fallback).

old_insert = r"await run\(`INSERT INTO employees \(id, user_id, name, email, department, designation, location, join_date, status, emergency_contact, address\) VALUES \(\?, \?, \?, \?, \?, \?, \?, \?, \?, \?, \?\)\`, \s*\[emp_id, user_id, name, email, department, role, location, new Date\(\)\.toISOString\(\), \"Active\", null, null\]\);"
new_insert = r"""await run(`INSERT INTO employees (id, user_id, name, email, phone, department, designation, location, join_date, manager_id, status, emergency_contact, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, 
                  [emp_id, user_id, name, email, phone || null, department, designation || role, location, join_date || new Date().toISOString(), manager_id || null, "Active", null, null]);"""

content = re.sub(old_insert, new_insert, content, flags=re.DOTALL)

with open('server.js', 'w') as f:
    f.write(content)
