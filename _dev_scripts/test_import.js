const fs = require('fs');
const xlsx = require('xlsx');

// Create a dummy Excel file
const wb = xlsx.utils.book_new();
const ws = xlsx.utils.json_to_sheet([
    { asset_tag: 'TEST-001', brand: 'Dell', model: 'XPS 15', serial_number: 'SN-001', category: 'Laptop', department: 'IT', status: 'available', monitor_make: 'Dell', monitor_serial_no: 'M-001', asset_owner_pl_no: 'PL-001', asset_usage_status: 'In Use', in_warranty_status: 'Yes' }
]);
xlsx.utils.book_append_sheet(wb, ws, 'Sheet1');
xlsx.writeFile(wb, 'test.xlsx');

console.log('Dummy Excel file created: test.xlsx');
