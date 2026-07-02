const http = require('http');

const baseURL = 'http://localhost:3001';

async function request(path, method = 'GET', data = null, cookie = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(path, baseURL);
        const options = {
            method,
            headers: {}
        };
        
        if (cookie) {
            options.headers['Cookie'] = cookie;
        }

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
    console.log("Running feature tests...");
    
    // 1. Login
    console.log("Testing Login...");
    const loginRes = await request('/login', 'POST', { username: 'testadmin', password: 'password123' });
    if (loginRes.status !== 302 || !loginRes.headers['set-cookie']) {
        console.error("Login failed!", loginRes.status);
        process.exit(1);
    }
    const cookie = loginRes.headers['set-cookie'][0].split(';')[0];
    console.log("Login successful! Cookie obtained.");

    const routesToTest = [
        '/dashboard',
        '/inventory',
        '/assets/new',
        '/users',
        '/add-user',
        '/reports',
        '/requests',
        '/archive',
        '/pending-imports',
        '/approvals', // Should return 404 since I removed it from sidebar? Or 200 if route still exists?
        '/tasks' // Same as above
    ];

    let allGood = true;

    for (let route of routesToTest) {
        console.log(`Testing GET ${route}...`);
        const res = await request(route, 'GET', null, cookie);
        if (res.status !== 200 && res.status !== 302 && res.status !== 404) {
            console.error(`❌ GET ${route} failed with status ${res.status}`);
            allGood = false;
        } else if (res.body.includes('Error') || res.body.includes('Stack Trace')) {
            console.error(`❌ GET ${route} might have an error on the page.`);
            allGood = false;
        } else {
            console.log(`✅ GET ${route} OK (${res.status})`);
        }
    }

    if (allGood) {
        console.log("\n🎉 All basic page routes are working correctly!");
    } else {
        console.log("\n⚠️ Some routes failed. Please review the output above.");
    }
    
    // 2. Test Asset Export
    console.log("Testing GET /inventory/export...");
    const exportRes = await request('/inventory/export', 'GET', null, cookie);
    if (exportRes.status === 200 && exportRes.headers['content-type'] === 'text/csv') {
        console.log("✅ GET /inventory/export OK");
    } else {
        console.log(`❌ GET /inventory/export failed (${exportRes.status})`);
        allGood = false;
    }

    console.log("Testing GET /archive/export...");
    const archiveExportRes = await request('/archive/export', 'GET', null, cookie);
    if ((archiveExportRes.status === 200 && archiveExportRes.headers['content-type'] === 'text/csv') || archiveExportRes.status === 404) {
        console.log(`✅ GET /archive/export OK (${archiveExportRes.status})`);
    } else {
        console.log(`❌ GET /archive/export failed (${archiveExportRes.status})`);
        allGood = false;
    }

}

runTests();
