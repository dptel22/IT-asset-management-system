import re
with open('server.js', 'r') as f:
    content = f.read()

pattern = r"    if \(!monitor_make \|\| !monitor_serial_no \|\| !asset_owner_pl_no \|\| !asset_usage_status \|\| !in_warranty_status \|\| !serial_number\) \{\n        const asset = await get\(`SELECT \* FROM assets WHERE id = \?`, \[req\.params\.id\]\);\n        return res\.render\('assets-edit\.html', \{ asset, error: 'Please fill out all mandatory fields\.' \}\);\n    \}"

content = re.sub(pattern, "", content)

with open('server.js', 'w') as f:
    f.write(content)
