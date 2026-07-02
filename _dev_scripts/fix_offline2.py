import re

with open('ui/ux/gen_pages.py', 'r') as f:
    content = f.read()

# Generate assets_edit_html
if "assets_edit_html = " not in content:
    # Let's replace create_page("add-asset.html", add_asset_html)
    # with logic to also create assets-edit.html
    replacement = """
create_page("add-asset.html", add_asset_html)

assets_edit_html = add_asset_html.replace('Add New Asset', 'Edit Asset').replace('Register a new hardware or software asset', 'Update details for an existing asset').replace('Submit Asset', 'Save Changes')
# Set some dummy values
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter brand (e.g. Dell, Apple)">', '<input type="text" class="form-control" required value="Apple">')
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter model name">', '<input type="text" class="form-control" required value="MacBook Pro 16">')
assets_edit_html = assets_edit_html.replace('<input type="text" class="form-control" required placeholder="Enter unique serial number">', '<input type="text" class="form-control" required value="C02XX123456">')

create_page("assets-edit.html", assets_edit_html)
"""
    content = content.replace('create_page("add-asset.html", add_asset_html)', replacement)

# Fix links in inventory.html and asset-detail.html in gen_pages.py if any (actually those are in index.html, dashboard.html, inventory.html directly via the other script?)
# Wait, inventory.html is generated from fullstack_implementation_blueprint.md or python scripts?
# Actually, the base templates for offline are generated from a base string. But in this case the user was working on the offline files.

with open('ui/ux/gen_pages.py', 'w') as f:
    f.write(content)



