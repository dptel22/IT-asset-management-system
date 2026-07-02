const xlsx = require('xlsx');

const headers = ['asset_tag', 'brand', 'model', 'serial_number', 'category', 'department', 'location', 'purchase_date', 'warranty_date', 'purchase_cost', 'status', 'sl_no', 'monitor_make', 'monitor_serial_no', 'asset_owner_pl_no', 'asset_usage_status', 'in_warranty_status', 'system_serial_no', 'host_name', 'group_name', 'division', 'user_name', 'designation', 'ip_address', 'mac_address', 'network_type', 'drona_domain', 'os_version', 'antivirus_status', 'usb_status', 'admin_privilege', 'owner_email'];

const rows = [
    headers,
    ['TEST-1', 'Test Brand', 'Model X', 'TEST-SN-1', 'Cat1', 'Dep', 'Loc', '', '', '100', 'available', 'sl1', 'Mon', 'MonSN1', 'pl1', 'u', 'w', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'superadmin@cognixasset.com'],
    ['', 'Test Brand', 'Model Y', 'TEST-SN-2', 'Cat1', 'Dep', 'Loc', '', '', '100', 'available', 'sl1', 'Mon', 'MonSN2', 'pl1', 'u', 'w', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ['TEST-1', 'Test Brand', 'Model Z', 'TEST-SN-3', 'Cat1', 'Dep', 'Loc', '', '', '100', 'available', 'sl1', 'Mon', 'MonSN3', 'pl1', 'u', 'w', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ['TEST-4', 'Test Brand', 'Model W', 'TEST-SN-4', 'Cat1', 'Dep', 'Loc', '', '', '100', 'available', 'sl1', 'Mon', 'MonSN4', 'pl1', 'u', 'w', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'invalid@example.com']
];

const ws = xlsx.utils.aoa_to_sheet(rows);
const wb = xlsx.utils.book_new();
xlsx.utils.book_append_sheet(wb, ws, 'Template');
xlsx.writeFile(wb, '/Users/rithanyamagesh/Desktop/antigravity/test_upload.xlsx');
console.log('Created test_upload.xlsx');
