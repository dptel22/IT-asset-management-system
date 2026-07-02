import re

def fix():
    with open('templates/assets-new.html', 'r') as f:
        content = f.read()

    # 1. Remove the "Optional Additional Fields" block I injected
    start_marker = "            <!-- Additional Details Toggle -->"
    end_marker = "              <div style=\"margin-bottom: 24px;\"></div>\n"

    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)
        content = content[:start_idx] + content[end_idx:]
        print("Removed static optional fields from assets-new.html")
    else:
        print("Static optional fields not found (already removed?)")

    # 2. Fix the dynamic title JS
    old_js = "dynamicTitle.textContent = `ADDITIONAL DETAILS — ${val.toUpperCase()}`;"
    new_js = "dynamicTitle.textContent = `${val.toUpperCase()} DETAILS`;"
    
    if old_js in content:
        content = content.replace(old_js, new_js)
        print("Fixed JS dynamic title (em dash)")
    else:
        # Check standard dash just in case
        old_js2 = "dynamicTitle.textContent = `ADDITIONAL DETAILS - ${val.toUpperCase()}`;"
        if old_js2 in content:
            content = content.replace(old_js2, new_js)
            print("Fixed JS dynamic title (hyphen)")
        else:
            print("JS string not found")

    with open('templates/assets-new.html', 'w') as f:
        f.write(content)

fix()
