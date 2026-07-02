import re

def fix_template(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # The grid currently has everything inside <div id="additional-details"...>
    # We need to split the grid into two.
    # The fields before "Monitor Make" go back to the top grid.
    # The fields starting with "Monitor Make" stay in the additional-details grid.
    
    # Let's find the additional details grid content
    pattern = r'(<div id="additional-details".*?>\s*<div.*?>)(.*?)(<div>\s*<label[^>]*>Monitor Make.*)'
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        print("Could not match in", filepath)
        return
        
    main_fields = match.group(2)
    additional_fields = match.group(3)
    
    # Remove main_fields from additional-details
    content = content[:match.start(2)] + additional_fields + content[match.end(3):]
    
    # Now put main_fields back above the additional details toggle
    # There should be an empty or existing <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;"> above it.
    # Let's find the <!-- Additional Details Toggle --> and insert it in the grid above it.
    
    # Search for the grid closing before the toggle
    grid_close_pattern = r'(\s*)(</div>\s*<!-- Additional Details Toggle -->)'
    content = re.sub(grid_close_pattern, r'\1' + main_fields + r'\2', content, count=1)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print("Fixed", filepath)

fix_template('templates/assets-new.html')
fix_template('templates/assets-edit.html')
