import re

def fix_template(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # We need to extract the block of 5 custom fields and move them inside <div id="additional-details"...>
    
    # The block of fields starts with:
    # <div>\n                  <label style="display:block; ...">Monitor Make *</label>
    # and ends right before:
    #             </div>\n\n            <!-- Additional Details Toggle -->
    
    pattern = r'(<div>\s*<label.*?Monitor Make \*.*?)(\s*</div>\s*<!-- Additional Details Toggle -->)'
    match = re.search(pattern, content, flags=re.DOTALL)
    
    if match:
        fields_block = match.group(1)
        # Remove fields from original position
        content = content[:match.start()] + match.group(2) + content[match.end():]
        
        # Now find the start of the grid inside additional-details
        # <div id="additional-details" style="display: none; margin-top: 20px;">
        #   <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        
        insert_pattern = r'(<div id="additional-details".*?>\s*<div.*?>)'
        content = re.sub(insert_pattern, r'\1\n' + fields_block + '\n', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"Could not find fields block in {filepath}")

fix_template('templates/assets-new.html')
fix_template('templates/assets-edit.html')
