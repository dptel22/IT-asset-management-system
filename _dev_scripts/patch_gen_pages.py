import re

with open('ui/ux/gen_pages.py', 'r') as f:
    gen_pages_content = f.read()

# Replace the find logic
new_logic = """
    start_idx = base_html.find('<div class="content-area">')
    end_idx = base_html.find('</main>', start_idx)
    
    prefix = base_html[:start_idx + len('<div class="content-area">')]
    suffix = '\\n      </div>\\n    ' + base_html[end_idx:]
    
    # Extract the inner part of main_content_html (which starts with <div class="main-content">)
    # We want to remove the <div class="main-content"> wrapper because we are already in content-area
    inner_match = re.search(r'<div class="main-content">(.*)', main_content_html, re.DOTALL)
    if inner_match:
        content_to_insert = inner_match.group(1)
        # Also remove the last closing div of main-content if it exists
        # Actually it's easier to just strip the first line and we can leave the wrapper, or remove it.
        # But wait, main_content_html is exactly what we appended.
"""

# Let's just do a simpler string replace on gen_pages.py
old_code = """    start_idx = base_html.find('<main class="main-content">')
    end_idx = base_html.find('</main>', start_idx) + len('</main>')
    
    prefix = base_html[:start_idx]
    suffix = base_html[end_idx:]
    
    new_html = prefix + main_content_html + suffix"""

new_code = """    start_idx = base_html.find('<div class="content-area">')
    end_idx = base_html.find('</main>', start_idx)
    
    prefix = base_html[:start_idx + len('<div class="content-area">')]
    suffix = '\\n      </div>\\n    ' + base_html[end_idx:]
    
    # We need to strip <div class="main-content"> ... </div> from main_content_html
    # because it will break the layout.
    import re
    content_match = re.search(r'<div class="main-content">(.*)</div>\\s*<style>', main_content_html, re.DOTALL)
    if content_match:
        inner_content = content_match.group(1)
        styles_scripts = main_content_html[content_match.end(1) + 6:] # </div> length
        main_content_html = inner_content + '\\n' + styles_scripts
    else:
        main_content_html = main_content_html.replace('<div class="main-content">', '')
        
    new_html = prefix + '\\n' + main_content_html + suffix"""

gen_pages_content = gen_pages_content.replace(old_code, new_code)

with open('ui/ux/gen_pages.py', 'w') as f:
    f.write(gen_pages_content)

print("Patched gen_pages.py")
