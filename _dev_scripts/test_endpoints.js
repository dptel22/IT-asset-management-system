const http = require('http');
const req = http.request({
  hostname: 'localhost',
  port: 3000,
  path: '/login',
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': Buffer.byteLength('username=emp1&password=password123&role=employee')
  }
}, res => {
  const cookie = res.headers['set-cookie'][0].split(';')[0];
  
  http.get({ hostname: 'localhost', port: 3000, path: '/employee/asset-requests/status', headers: { 'Cookie': cookie } }, r => {
    let d = ''; r.on('data', c => d+=c); r.on('end', () => console.log('Asset reqs:', r.statusCode, d));
  });
  http.get({ hostname: 'localhost', port: 3000, path: '/employee/transfer-requests/status', headers: { 'Cookie': cookie } }, r => {
    let d = ''; r.on('data', c => d+=c); r.on('end', () => console.log('Transfer reqs:', r.statusCode, d));
  });
});
req.write('username=emp1&password=password123&role=employee');
req.end();
