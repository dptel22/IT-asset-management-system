const fs = require('fs');

const content = fs.readFileSync('server.js', 'utf8');

const routeContent = `
app.get('/archive/export', requireAuth, requireSuperAdmin, async (req, res) => {
    try {
        const archived_assets = await query(\`
            SELECT aa.*, u.username as archived_by_name
            FROM asset_archive aa
            LEFT JOIN users u ON aa.archived_by = u.id
            ORDER BY aa.archived_at DESC
        \`);
        
        // Generate CSV
        const header = ['Asset ID', 'Name', 'Serial', 'Category', 'Archived By', 'Archived At', 'Reason'];
        const csvRows = [header.join(',')];
        
        for (const asset of archived_assets) {
            const row = [
                asset.asset_id,
                ` + "`\"${(asset.name || '').replace(/\"/g, '\"\"')}\"`" + `,
                ` + "`\"${(asset.serial || '').replace(/\"/g, '\"\"')}\"`" + `,
                ` + "`\"${(asset.category || '').replace(/\"/g, '\"\"')}\"`" + `,
                ` + "`\"${(asset.archived_by_name || '').replace(/\"/g, '\"\"')}\"`" + `,
                asset.archived_at,
                ` + "`\"${(asset.reason || '').replace(/\"/g, '\"\"')}\"`" + `
            ];
            csvRows.push(row.join(','));
        }
        
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="archived_assets.csv"');
        res.send(csvRows.join('\\n'));
    } catch (e) {
        console.error('Export error:', e);
        res.status(500).send('Error generating export');
    }
});
`;

if (!content.includes('/archive/export')) {
    const updated = content.replace("app.get('/archive', requireAuth, requireSuperAdmin, async (req, res) => {", routeContent + "\\napp.get('/archive', requireAuth, requireSuperAdmin, async (req, res) => {");
    fs.writeFileSync('server.js', updated);
    console.log("Updated server.js");
} else {
    console.log("server.js already has the route");
}
