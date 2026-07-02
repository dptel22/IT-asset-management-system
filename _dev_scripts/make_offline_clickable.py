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

# 1. inventory.html
patch_file('ui/ux/inventory.html', [
    ('<i data-lucide="eye" class="action-icon view" width="16"></i>', 
     '<i data-lucide="eye" class="action-icon view" width="16" onclick="window.location.href=\'asset-detail.html\'" style="cursor:pointer;"></i>'),
    ('<i data-lucide="pen-line" class="action-icon" width="16"></i>', 
     '<i data-lucide="pen-line" class="action-icon" width="16" onclick="window.location.href=\'assets-edit.html\'" style="cursor:pointer;"></i>'),
    ('<button class="btn btn-primary"><i data-lucide="plus" width="16"></i> Add Asset</button>',
     '<button class="btn btn-primary" onclick="window.location.href=\'add-asset.html\'"><i data-lucide="plus" width="16"></i> Add Asset</button>')
])

# 2. asset-detail.html
patch_file('ui/ux/asset-detail.html', [
    ('<button class="btn btn-primary"><i data-lucide="edit" width="16"></i> Edit Asset</button>',
     '<button class="btn btn-primary" onclick="window.location.href=\'assets-edit.html\'"><i data-lucide="edit" width="16"></i> Edit Asset</button>'),
    ('<button class="btn btn-outline"><i data-lucide="edit" width="16"></i> Edit Asset</button>',
     '<button class="btn btn-outline" onclick="window.location.href=\'assets-edit.html\'"><i data-lucide="edit" width="16"></i> Edit Asset</button>')
])

# 3. add-asset.html
patch_file('ui/ux/add-asset.html', [
    ("onsubmit=\"event.preventDefault(); showToast('Asset added successfully', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('Asset added successfully', 'success'); setTimeout(() => window.location.href='inventory.html', 1000);\"")
])

# 4. assets-edit.html
patch_file('ui/ux/assets-edit.html', [
    ("onsubmit=\"event.preventDefault(); showToast('Asset added successfully', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('Asset updated successfully', 'success'); setTimeout(() => window.location.href='inventory.html', 1000);\""),
    ("onsubmit=\"event.preventDefault(); showToast('Asset updated successfully', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('Asset updated successfully', 'success'); setTimeout(() => window.location.href='inventory.html', 1000);\"")
])

# 5. employee-directory.html
patch_file('ui/ux/employee-directory.html', [
    ('<i data-lucide="eye" class="action-icon" width="16"></i>',
     '<i data-lucide="eye" class="action-icon" width="16" onclick="window.location.href=\'employee-profile.html\'" style="cursor:pointer;"></i>'),
    ('<button class="btn btn-outline"><i data-lucide="user-plus" width="16"></i> Add Employee</button>',
     '<button class="btn btn-outline" onclick="window.location.href=\'add-user.html\'"><i data-lucide="user-plus" width="16"></i> Add Employee</button>')
])

# 6. add-user.html
patch_file('ui/ux/add-user.html', [
    ("onsubmit=\"event.preventDefault(); showToast('User created successfully. An invite has been sent to their email.', 'success'); this.reset();\"",
     "onsubmit=\"event.preventDefault(); showToast('User created successfully. An invite has been sent to their email.', 'success'); setTimeout(() => window.location.href='employee-directory.html', 1000);\"")
])

