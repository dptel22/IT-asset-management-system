const http = require('http');
const baseURL = 'http://localhost:3001';

async function request(path, method = 'GET', data = null, cookie = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(path, baseURL);
        const options = { method, headers: {} };
        if (cookie) options.headers['Cookie'] = cookie;
        if (data) {
            options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
            data = new URLSearchParams(data).toString();
            options.headers['Content-Length'] = Buffer.byteLength(data);
        }
        const req = http.request(url, options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
        });
        req.on('error', reject);
        if (data) req.write(data);
        req.end();
    });
}

async function runTests() {
    const loginRes = await request('/login', 'POST', { username: 'testadmin', password: 'password123' });
    const cookie = loginRes.headers['set-cookie'][0].split(';')[0];
    
    const routes = ['/dashboard', '/inventory', '/assets/new', '/users', '/add-user', '/reports', '/requests', '/archive', '/pending-imports'];
    for (let r of routes) {
        const res = await request(r, 'GET', null, cookie);
        console.log(`[${res.status}] ${r}`);
    }
}
runTests();
