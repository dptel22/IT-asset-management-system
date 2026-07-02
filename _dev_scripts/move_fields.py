import re

with open('ui/ux/gen_pages.py', 'r') as f:
    content = f.read()

# We want to extract the block of 5 fields and move it into the extra-fields div
# The block starts with <div class="form-grid mt-3"> right before <!-- Collapsible Additional Details -->

pattern = r'(<div class="form-grid mt-3">.*?</div>\s*)(<!-- Collapsible Additional Details -->\s*<div.*?>\s*<button.*?>\s*<i.*?></i> Show Additional Details\s*</button>\s*<div id="extra-fields".*?>\s*<div class="form-grid">)'
# We will swap them: Put the Collapsible Additional Details wrapper first, then inside the extra-fields form-grid, put the contents of the 5 fields.

def replacer(match):
    fields_block = match.group(1)
    # remove the outer <div class="form-grid mt-3"> and </div> from fields_block
    inner_fields = re.sub(r'^<div class="form-grid mt-3">\s*', '', fields_block)
    inner_fields = re.sub(r'\s*</div>\s*$', '', inner_fields)
    
    wrapper = match.group(2)
    return wrapper + "\n" + inner_fields + "\n"

content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open('ui/ux/gen_pages.py', 'w') as f:
    f.write(content)

