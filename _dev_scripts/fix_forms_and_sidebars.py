import os
import re

def fix_add_user():
    path = "templates/add-user.html"
    with open(path, "r") as f:
        content = f.read()
        
    content = content.replace('type="tel" class="form-control"', 'type="tel" name="phone" class="form-control"')
    content = content.replace('type="date" class="form-control"', 'type="date" name="join_date" class="form-control"')
    
    # Fix designation (which is missing, but there is a 'Job Title / Designation' input?)
    # Let's just fix the Reporting Manager select
    content = content.replace('<select class="form-control" >\n                    <option value="" disabled selected>Select Manager</option>', 
                              '<select name="manager_id" class="form-control" >\n                    <option value="" disabled selected>Select Manager</option>')
    
    with open(path, "w") as f:
        f.write(content)

def fix_add_asset():
    path = "templates/add-asset.html"
    with open(path, "r") as f:
        content = f.read()
        
    content = content.replace('<textarea class="form-control" rows="4" required placeholder="Why do you need this asset?"></textarea>',
                              '<textarea name="justification" class="form-control" rows="4" required placeholder="Why do you need this asset?"></textarea>')
    with open(path, "w") as f:
        f.write(content)

def fix_sidebars():
    d = "templates/"
    for f in os.listdir(d):
        if f.endswith(".html"):
            p = os.path.join(d, f)
            with open(p, "r") as file:
                content = file.read()
            if "<aside class=\"sidebar\">" in content:
                new_content = re.sub(r"<aside class=\"sidebar\">.*?</aside>", "{% include \"partials/sidebar.html\" %}", content, flags=re.DOTALL)
                with open(p, "w") as out:
                    out.write(new_content)
                    
def fix_dashboard_new_request():
    path = "templates/employee-dashboard.html"
    with open(path, "r") as f:
        content = f.read()
    
    content = content.replace('<button class="btn btn-primary" onclick="openModal(\'requestModal\')">',
                              '<a href="/requests/new" class="btn btn-primary" style="text-decoration:none">')
    content = content.replace('</button>\n          <div style="position: relative; cursor: pointer; color: var(--text-secondary);">',
                              '</a>\n          <div style="position: relative; cursor: pointer; color: var(--text-secondary);">')
    
    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    fix_add_user()
    fix_add_asset()
    fix_sidebars()
    fix_dashboard_new_request()
    print("Fixes applied.")
