const fs = require('fs');
let content = fs.readFileSync('server.js', 'utf8');

// Patch 1: POST /assets
const target1 = `        const id = uuidv4();
        await run(
            \`INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?)\`,
            [id, asset_tag, brand, model, serial_number, category,
             purchase_date || null, warranty_date || null,
             parseFloat(purchase_cost) || 0, department, location, status || 'available',
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege]
        );`;

const replacement1 = `        let current_owner_id = null;
        if (req.body.owner_email) {
            const emp = await get(\`SELECT id FROM employees WHERE email = ?\`, [String(req.body.owner_email).trim()]);
            if (emp) current_owner_id = emp.id;
        }
        if (!current_owner_id && req.body.employee_id) {
            const emp = await get(\`SELECT id FROM employees WHERE id = ?\`, [String(req.body.employee_id).trim()]);
            if (emp) current_owner_id = emp.id;
        }
        if (!current_owner_id && user_name) {
            const emp = await get(\`SELECT id FROM employees WHERE name = ?\`, [String(user_name).trim()]);
            if (emp) current_owner_id = emp.id;
        }

        let final_status = status || 'available';
        if (current_owner_id && (!status || status === 'available' || status === 'pending')) {
            final_status = 'assigned';
        }

        const id = uuidv4();
        console.log(\`[DEBUG] Manual Asset Creation - ID: \${id}, owner_email: \${req.body.owner_email}, user_name: \${user_name}, resolved emp_id: \${current_owner_id}, final status: \${final_status}\`);
        
        await run(
            \`INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
            sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
            system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
            network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?)\`,
            [id, asset_tag, brand, model, serial_number, category,
             purchase_date || null, warranty_date || null,
             parseFloat(purchase_cost) || 0, department, location, final_status,
             sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
             system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
             network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id]
        );`;

content = content.replace(target1, replacement1);

// Patch 2: POST /assets/import
const target2 = `            const id = uuidv4();
            await run(
                \`INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
                sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?)\`,
                [id, asset_tag, brand || 'Unknown', model || 'Unknown', serial_number, category || 'Other',
                 purchase_date || null, warranty_date || null,
                 parseFloat(purchase_cost) || 0, department || 'Unknown', location || 'Unknown', 'pending',
                 sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                 system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                 network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id]
            );`;

const replacement2 = `            const id = uuidv4();
            console.log(\`[DEBUG] Excel Import - Asset ID: \${id}, owner_email: \${owner_email}, resolved emp_id: \${current_owner_id}, final status: pending\`);
            await run(
                \`INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status,
                sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?, ?,?,?,?,?,?, ?)\`,
                [id, asset_tag, brand || 'Unknown', model || 'Unknown', serial_number, category || 'Other',
                 purchase_date || null, warranty_date || null,
                 parseFloat(purchase_cost) || 0, department || 'Unknown', location || 'Unknown', 'pending',
                 sl_no, monitor_make, monitor_serial_no, asset_owner_pl_no, asset_usage_status, in_warranty_status,
                 system_serial_no, host_name, group_name, division, user_name, designation, ip_address, mac_address,
                 network_type, drona_domain, os_version, antivirus_status, usb_status, admin_privilege, current_owner_id]
            );`;

content = content.replace(target2, replacement2);

// Patch 3: /employee-profile
const target3 = `    const assigned_assets = await query(
        \`SELECT * FROM assets WHERE current_owner_id = ? ORDER BY created_at DESC\`, [id]
    );`;

const replacement3 = `    const assigned_assets = await query(
        \`SELECT * FROM assets WHERE current_owner_id = ? ORDER BY created_at DESC\`, [id]
    );
    console.log(\`[DEBUG] Profile load - Employee ID: \${id}, Assets found: \${assigned_assets.length}\`);`;

content = content.replace(target3, replacement3);

fs.writeFileSync('server.js', content, 'utf8');
console.log('Patch complete.');
