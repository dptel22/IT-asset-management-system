import re
import os

def patch_file(filepath, replacements):
    if not os.path.exists(filepath): return
    with open(filepath, 'r') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# 1. add-asset.html
patch_file('ui/ux/add-asset.html', [
    ("onsubmit=\"event.preventDefault(); showToast('Asset request submitted successfully.', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('Asset request submitted successfully.', 'success'); setTimeout(() => window.location.href='inventory.html', 1000);\"")
])

# 2. assets-edit.html
patch_file('ui/ux/assets-edit.html', [
    ("onsubmit=\"event.preventDefault(); showToast('Asset request submitted successfully.', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('Asset updated successfully.', 'success'); setTimeout(() => window.location.href='inventory.html', 1000);\"")
])

