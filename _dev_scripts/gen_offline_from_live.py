import re

with open('templates/assets-new.html', 'r') as f:
    content = f.read()

# Replace variables like {{ values.department }} with empty string or default
content = re.sub(r'\{\{ values\.[^}]+\}\}', '', content)
# Replace {% ... %} with empty string
content = re.sub(r'\{%.*?%\}', '', content)
# Fix form tag for offline
content = re.sub(r'<form method="POST" action="/assets/.*?" class="fade-up">', 
                 '<form id="addAssetForm" onsubmit="event.preventDefault(); showToast(\'Asset added successfully\', \'success\'); setTimeout(() => window.location.href=\'inventory.html\', 1000);" class="fade-up">', content)
content = content.replace('<form method="POST" action="/assets" class="fade-up">', 
                          '<form id="addAssetForm" onsubmit="event.preventDefault(); showToast(\'Asset added successfully\', \'success\'); setTimeout(() => window.location.href=\'inventory.html\', 1000);" class="fade-up">')

with open('ui/ux/add-asset.html', 'w') as f:
    f.write(content)

with open('templates/assets-edit.html', 'r') as f:
    content = f.read()

content = re.sub(r'\{\{ values\.[^}]+\}\}', '', content)
content = re.sub(r'\{\{ asset\.[^}]+\}\}', '', content)
content = re.sub(r'\{%.*?%\}', '', content)
content = re.sub(r'<form method="POST" action="/assets/.*?" class="fade-up">', 
                 '<form id="addAssetForm" onsubmit="event.preventDefault(); showToast(\'Asset updated successfully\', \'success\'); setTimeout(() => window.location.href=\'inventory.html\', 1000);" class="fade-up">', content)

with open('ui/ux/assets-edit.html', 'w') as f:
    f.write(content)

