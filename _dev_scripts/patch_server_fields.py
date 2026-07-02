import re

with open('server.js', 'r') as f:
    content = f.read()

# Replace POST /assets
create_route = re.search(r"app\.post\('/assets', requireAuth, async \(req, res\) => \{.*?(?=\n// Asset Detail)", content, re.DOTALL).group(0)

new_create_route = """app.post('/assets', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    let { 
        asset_tag, brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
        sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
        system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
        network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege
    } = req.body;
    
    asset_tag = asset_tag ? asset_tag.trim() : '';
    serial_number = serial_number ? serial_number.trim() : '';

    if (!sl_no || !monitor_make || !monitor_serial_no || !asset_owner_pl_no || !asset_usage_status || !in_warranty_status) {
        return res.render('assets-new.html', { error: 'Please fill out all mandatory fields.', values: req.body });
    }

    try {
        if (!asset_tag) {
            const last = await get(`SELECT asset_tag FROM assets WHERE asset_tag LIKE 'AST-%' ORDER BY CAST(SUBSTR(asset_tag, 5) AS INTEGER) DESC LIMIT 1`);
            const num = last ? parseInt(last.asset_tag.replace('AST-', ''), 10) : 999;
            asset_tag = `AST-${num + 1}`;
        } else {
            const existingTag = await get(`SELECT id FROM assets WHERE asset_tag = ?`, [asset_tag]);
            if (existingTag) {
                return res.render('assets-new.html', { error: 'Asset tag already exists. Leave it blank to auto-generate one, or enter a different tag.', values: req.body });
            }
        }
        
        if (!serial_number) {
            serial_number = `SN-${uuidv4().substring(0, 8).toUpperCase()}`;
        } else {
            const existingSerial = await get(`SELECT id FROM assets WHERE serial_number = ?`, [serial_number]);
            if (existingSerial) {
                return res.render('assets-new.html', { error: 'Serial number already exists. Leave it blank to auto-generate one, or enter a different serial number.', values: req.body });
            }
        }

        const id = uuidv4();
        await run(
            `INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?)`,
            [id, asset_tag, brand, model, serial_number, category,
             purchase_date || null, warranty_date || null,
             parseFloat(purchase_cost) || 0, department, location, status || 'available',
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege]
        );
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), id, 'Added', `Asset ${asset_tag} added to inventory.`, req.user.id]
        );
        res.redirect('/inventory');
    } catch (err) {
        console.error('Create asset error:', err.message);
        let errorMsg = 'Could not create asset. Please check the details and try again.';
        if (err.message && err.message.includes('assets.asset_tag')) {
            errorMsg = 'Asset tag already exists. Leave it blank to auto-generate one, or enter a different tag.';
        } else if (err.message && err.message.includes('assets.serial_number')) {
            errorMsg = 'Serial number already exists. Leave it blank to auto-generate one, or enter a different serial number.';
        }
        res.render('assets-new.html', { error: errorMsg, values: req.body });
    }
});"""

content = content.replace(create_route, new_create_route)

# Replace POST /assets/:id/edit
edit_route = re.search(r"app\.post\('/assets/:id/edit', requireAuth, async \(req, res\) => \{.*?(?=\n// Unassign Asset)", content, re.DOTALL).group(0)

new_edit_route = """app.post('/assets/:id/edit', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { 
        brand, model, serial_number, category, department, location, purchase_date, warranty_date, purchase_cost, status,
        sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
        system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
        network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege
    } = req.body;
    
    if (!sl_no || !monitor_make || !monitor_serial_no || !asset_owner_pl_no || !asset_usage_status || !in_warranty_status) {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        return res.render('assets-edit.html', { asset, error: 'Please fill out all mandatory fields.' });
    }

    try {
        await run(
            `UPDATE assets SET brand=?, model=?, serial_number=?, category=?, department=?, location=?,
             purchase_date=?, warranty_date=?, purchase_cost=?, status=?,
             sl_no=?, monitor_make=?, monitor_serial_no=?, asset_owner_pl_no=?, asset_usage_status=?, in_warranty_status=?,
             system_serial_no=?, host_name=?, group_name=?, division=?, user_name=?, designation=?, ip_address=?, mac_address=?,
             network_type=?, drona_domain=?, os_version=?, antivirus_status=?, usb_status=?, admin_privilege=?
             WHERE id=?`,
            [brand, model, serial_number, category, department, location,
             purchase_date || null, warranty_date || null, parseFloat(purchase_cost) || 0, status,
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege,
             req.params.id]
        );
        await run(
            `INSERT INTO asset_history (id, asset_id, event_type, description, created_by) VALUES (?,?,?,?,?)`,
            [uuidv4(), req.params.id, 'Updated', `Asset details updated by ${req.user.username}.`, req.user.id]
        );
        res.redirect(`/assets/${req.params.id}`);
    } catch (err) {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        res.render('assets-edit.html', { asset, error: err.message });
    }
});"""

content = content.replace(edit_route, new_edit_route)

# Replace POST /api/assets/:id/archive to include new columns in asset_archive
archive_route = re.search(r"app\.post\('/api/assets/:id/archive', requireAuth, async \(req, res\) => \{.*?(?=\n// ============================================================)", content, re.DOTALL).group(0)

new_archive_route = """app.post('/api/assets/:id/archive', requireAuth, async (req, res) => {
    if (req.user.role === 'employee') return res.status(403).send('Forbidden');
    const { reason } = req.body;
    try {
        const asset = await get(`SELECT * FROM assets WHERE id = ?`, [req.params.id]);
        if (!asset) return res.status(404).send('Not found');
        await run(
            `INSERT INTO asset_archive (id, original_asset_id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status, archived_by, reason,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?)`,
            [uuidv4(), asset.id, asset.asset_tag, asset.brand, asset.model, asset.serial_number,
             asset.category, asset.purchase_date, asset.warranty_date, asset.purchase_cost,
             asset.department, asset.location, asset.status, req.user.id, reason || 'Manual Archive',
             asset.sl_no, asset.monitor_make, asset.monitor_serial_no, asset.asset_owner_pl_no, asset.asset_usage_status, asset.in_warranty_status,
             asset.system_serial_no, asset.host_name, asset.group_name, asset.division, asset.user_name, asset.designation, asset.ip_address, asset.mac_address,
             asset.network_type, asset.drona_domain, asset.os_version, asset.antivirus_status, asset.usb_status, asset.admin_privilege]
        );
        await run(`DELETE FROM maintenance WHERE asset_id = ?`, [req.params.id]);
        await run(`DELETE FROM transfers WHERE asset_id = ?`, [req.params.id]);
        await run(`DELETE FROM assets WHERE id = ?`, [req.params.id]);
        res.redirect('/inventory');
    } catch (err) {
        res.status(500).send('Error archiving asset');
    }
});"""

content = content.replace(archive_route, new_archive_route)

with open('server.js', 'w') as f:
    f.write(content)

print("server.js patched.")
