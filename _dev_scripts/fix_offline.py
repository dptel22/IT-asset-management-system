import re

with open('ui/ux/gen_pages.py', 'r') as f:
    content = f.read()

# 1. Fix Add Employee button
content = content.replace(
    '<button class="btn btn-outline"><i data-lucide="user-plus" width="16"></i> Add Employee</button>',
    '<button class="btn btn-outline" onclick="window.location.href=\\\'add-user.html\\\'"><i data-lucide="user-plus" width="16"></i> Add Employee</button>'
)

# 2. Add Edit Asset HTML (duplicate of add_asset_html)
# Let's see if add_asset_html is in the file
if "add_asset_html =" in content:
    # We will generate assets_edit_html from add_asset_html
    # but first let's just create it directly in the generation loop at the bottom.
    pass

with open('ui/ux/gen_pages.py', 'w') as f:
    f.write(content)
