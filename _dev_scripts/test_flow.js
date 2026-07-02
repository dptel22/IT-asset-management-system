const fs = require('fs');

async function testFlow() {
    console.log("Testing User Login...");
    const userRes = await fetch('http://127.0.0.1:3000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=user1&password=admin'
    });
    const userCookie = userRes.headers.get('set-cookie').split(';')[0];
    
    console.log("Testing User Access to /assets/import-template...");
    const userTpl = await fetch('http://127.0.0.1:3000/assets/import-template', {
        headers: { 'cookie': userCookie }
    });
    console.log("User HTTP Status:", userTpl.status);
    console.log("User HTTP Body:", await userTpl.text());

    console.log("\\nTesting Admin Login...");
    const adminRes = await fetch('http://127.0.0.1:3000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=admin&password=admin'
    });
    const adminCookie = adminRes.headers.get('set-cookie').split(';')[0];

    console.log("Testing Admin Access to /assets/import-template...");
    const adminTpl = await fetch('http://127.0.0.1:3000/assets/import-template', {
        headers: { 'cookie': adminCookie }
    });
    console.log("Admin HTTP Status:", adminTpl.status);
    console.log("Content-Type:", adminTpl.headers.get('content-type'));

    console.log("\\nTesting Admin Upload...");
    const FormData = require('form-data');
    const form = new FormData();
    form.append('excel_file', fs.createReadStream('test_upload.xlsx'));

    const uploadRes = await fetch('http://127.0.0.1:3000/assets/import', {
        method: 'POST',
        headers: {
            'cookie': adminCookie,
            ...form.getHeaders()
        },
        body: form
    });
    const html = await uploadRes.text();
    const match = html.match(/Successfully imported \\d+ rows\\. Skipped \\d+ rows\\./);
    console.log("Upload Result Match:", match ? match[0] : 'No match found');
    
    // Print skipped reasons
    const reasons = html.match(/<li>(.*?)<\/li>/g);
    if (reasons) {
        reasons.forEach(r => console.log(r.replace(/<\/?li>/g, '')));
    }
}
testFlow();
