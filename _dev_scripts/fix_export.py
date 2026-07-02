import re

# 1. Update inventory.html
with open('templates/inventory.html', 'r') as f:
    inv_content = f.read()

inv_content = inv_content.replace(
    '<button class="btn btn-outline">\n              <i data-lucide="download" width="16" height="16"></i> Export CSV\n            </button>',
    '<a href="/inventory/export" class="btn btn-outline" style="text-decoration:none;">\n              <i data-lucide="download" width="16" height="16"></i> Export CSV\n            </a>'
)

with open('templates/inventory.html', 'w') as f:
    f.write(inv_content)

# 2. Add /inventory/export route to server.js
with open('server.js', 'r') as f:
    server_content = f.read()

inventory_export_route = """app.get('/inventory/export', requireAuth, async (req, res) => {
    try {
        const assets = await query(`
            SELECT a.*, e.name as current_owner_name
            FROM assets a
            LEFT JOIN employees e ON a.current_owner_id = e.id
            ORDER BY a.asset_tag ASC
        `);

        if (!assets || assets.length === 0) {
            return res.status(404).send('No assets found to export.');
        }

        const headers = ['Asset Tag', 'Brand', 'Model', 'Serial Number', 'Category', 'Department', 'Location', 'Status', 'Current Owner', 'Purchase Date', 'Warranty Date', 'Purchase Cost'];
        let csvContent = headers.join(',') + '\\n';

        assets.forEach(asset => {
            const row = [
                asset.asset_tag,
                asset.brand,
                asset.model,
                asset.serial_number,
                asset.category,
                asset.department,
                asset.location,
                asset.status,
                asset.current_owner_name || '',
                asset.purchase_date || '',
                asset.warranty_date || '',
                asset.purchase_cost || ''
            ].map(val => {
                let str = String(val || '').replace(/"/g, '""');
                return `"${str}"`;
            });
            csvContent += row.join(',') + '\\n';
        });

        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="inventory_assets.csv"');
        res.send(csvContent);
    } catch (err) {
        console.error('Export inventory error:', err);
        res.status(500).send('Error exporting inventory data');
    }
});
"""

# Insert it right after app.get('/inventory'
pattern = r"app\.get\('/inventory', requireAuth, async \(req, res\) => \{.*?\n\}\);\n"
match = re.search(pattern, server_content, re.DOTALL)
if match:
    end_idx = match.end()
    server_content = server_content[:end_idx] + "\n" + inventory_export_route + "\n" + server_content[end_idx:]
    with open('server.js', 'w') as f:
        f.write(server_content)
    print("Added /inventory/export")
else:
    print("Could not find /inventory route")
