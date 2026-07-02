import re

for filename in ['templates/assets-new.html', 'templates/assets-edit.html']:
    with open(filename, 'r') as f:
        content = f.read()
    
    # Remove the div containing sl_no
    # The div looks like:
    # <div>
    #   <label style="...">Sl.no *</label>
    #   <input type="text" name="sl_no" ...>
    # </div>
    
    # Since it might be multiline, we use re.DOTALL
    content = re.sub(r'<div>\s*<label[^>]*>Sl\.no \*</label>\s*<input[^>]*name="sl_no"[^>]*>\s*</div>', '', content, flags=re.DOTALL)
    
    with open(filename, 'w') as f:
        f.write(content)
