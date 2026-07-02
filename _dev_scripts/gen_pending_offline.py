import re
import os

with open('templates/pending-imports.html', 'r') as f:
    content = f.read()

# Replace variables like {{ asset.asset_tag }} with mock data
content = content.replace('{% for asset in assets %}', '')
content = content.replace('{% endfor %}', '')

content = content.replace('{{ asset.asset_tag }}', '#AST-0099')
content = content.replace('{{ asset.brand }}', 'Dell')
content = content.replace('{{ asset.model }}', 'Latitude 5420')
content = content.replace('{{ asset.category }}', 'Laptop')
content = content.replace('{{ asset.department }}', 'IT')
content = content.replace('{{ asset.asset_usage_status or "—" }}', 'New')
content = content.replace('{{ asset.in_warranty_status or "—" }}', 'Yes')
content = content.replace('{{ asset.asset_owner_pl_no or "—" }}', 'PL-101')
content = content.replace('{{ asset.monitor_make or "—" }}', '—')
content = content.replace('{{ asset.id }}', '1234')

# Replace the {% if status ... %} logic with just one badge
status_block_pattern = re.compile(r'\{% if asset\.status.*?\{% endif %\}', re.DOTALL)
content = status_block_pattern.sub('<span class="badge badge-neutral">Pending</span>', content)

with open('ui/ux/pending-imports.html', 'w') as f:
    f.write(content)

os.system('cp ui/ux/pending-imports.html /Users/rithanyamagesh/Desktop/CognixAsset_offline/pending-imports.html')
print("Offline pending-imports.html generated successfully.")
