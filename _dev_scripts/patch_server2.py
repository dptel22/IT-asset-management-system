with open('server.js', 'r') as f:
    content = f.read()

content = content.replace(
    'const { name, email, department, role, location } = req.body;',
    'let { name, email, department, role, location } = req.body;\n    location = location || "Head Office";'
)
content = content.replace(
    'if (!name || !email || !department || !role || !location)',
    'if (!name || !email || !department || !role)'
)

with open('server.js', 'w') as f:
    f.write(content)
print("server.js location logic patched")
