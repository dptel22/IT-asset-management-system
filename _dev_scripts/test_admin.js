const fs = require('fs');

async function test() {
    console.log('Logging in...');
    const loginRes = await fetch('http://127.0.0.1:3000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=admin&password=admin'
    });
    const cookie = loginRes.headers.get('set-cookie');
    console.log('Login status:', loginRes.status);
    
    console.log('Fetching /assets/import-template...');
    const tplRes = await fetch('http://127.0.0.1:3000/assets/import-template', {
        headers: { 'cookie': cookie }
    });
    console.log('Status:', tplRes.status);
    const text = await tplRes.text();
    console.log('Response:', text.substring(0, 100));
}
test();
