const fs = require('fs');
const http = require('http');
const FormData = require('form-data');

async function testUpload() {
  const form = new FormData();
  form.append('excel_file', fs.createReadStream('test.xlsx'));

  const options = {
    hostname: '127.0.0.1',
    port: 3000,
    path: '/assets/import',
    method: 'POST',
    headers: form.getHeaders()
  };
  
  // Since we don't have a valid cookie for requireAuth, let's see what the response is.
  // Actually, I can just mock req.user in a small express server, but we want to test the real one.
  const req = http.request(options, res => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log(`STATUS: ${res.statusCode}`);
      console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
      // console.log(`BODY: ${data}`);
    });
  });

  req.on('error', e => {
    console.error(`problem with request: ${e.message}`);
  });

  form.pipe(req);
}

testUpload();
