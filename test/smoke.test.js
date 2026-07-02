const test = require('node:test');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const sqlite3 = require('sqlite3').verbose();
const xlsx = require('xlsx');

const projectRoot = path.resolve(__dirname, '..');

async function waitForHealth(baseUrl, child) {
    for (let attempt = 0; attempt < 50; attempt++) {
        if (child.exitCode !== null) throw new Error(`Server exited with code ${child.exitCode}`);
        try {
            const response = await fetch(`${baseUrl}/api/health`);
            if (response.ok) return;
        } catch {}
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('Server did not become healthy');
}

function dbGet(dbPath, sql, params = []) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.get(sql, params, (err, row) => {
            db.close();
            if (err) reject(err);
            else resolve(row);
        });
    });
}

function buildImportWorkbookBuffer(assetTag, serialNumber) {
    const workbook = xlsx.utils.book_new();
    const worksheet = xlsx.utils.json_to_sheet([{
        asset_tag: assetTag,
        brand: 'Dell',
        model: 'Latitude',
        serial_number: serialNumber,
        category: 'Laptop',
        department: 'IT',
        location: 'Head Office',
        warranty_date: '2030-01-01',
        in_warranty_status: 'Yes'
    }]);
    xlsx.utils.book_append_sheet(workbook, worksheet, 'Assets');
    return xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });
}

async function login(baseUrl, username, password) {
    const response = await fetch(`${baseUrl}/login`, {
        method: 'POST',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
        redirect: 'manual'
    });
    assert.equal(response.status, 302);
    return response.headers.get('set-cookie');
}

async function uploadWorkbook(baseUrl, cookie, buffer) {
    const form = new FormData();
    form.append(
        'excel_file',
        new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }),
        'assets.xlsx'
    );
    const response = await fetch(`${baseUrl}/assets/import`, {
        method: 'POST',
        headers: { cookie },
        body: form
    });
    assert.equal(response.status, 200);
    return response.text();
}

test('fresh deployment supports secure login and authenticated inventory', async (t) => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cognixasset-test-'));
    const port = 3300 + Math.floor(Math.random() * 500);
    const baseUrl = `http://127.0.0.1:${port}`;
    const child = spawn(process.execPath, ['server.js'], {
        cwd: projectRoot,
        env: {
            ...process.env,
            NODE_ENV: 'production',
            HOST: '127.0.0.1',
            PORT: String(port),
            DB_PATH: path.join(tempDir, 'database.sqlite'),
            JWT_SECRET: 'test-secret-that-is-long-enough-for-tests',
            ADMIN_USERNAME: 'testadmin',
            ADMIN_PASSWORD: 'StrongTestPassword123!'
        },
        stdio: ['ignore', 'pipe', 'pipe']
    });

    let stderr = '';
    child.stderr.on('data', chunk => { stderr += chunk; });
    t.after(async () => {
        if (child.exitCode === null) child.kill('SIGTERM');
        await new Promise(resolve => child.once('exit', resolve));
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    await waitForHealth(baseUrl, child);

    const failedLogin = await fetch(`${baseUrl}/login`, {
        method: 'POST',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: 'testadmin', password: 'wrong' }),
        redirect: 'manual'
    });
    assert.equal(failedLogin.status, 401);

    const login = await fetch(`${baseUrl}/login`, {
        method: 'POST',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: 'testadmin', password: 'StrongTestPassword123!' }),
        redirect: 'manual'
    });
    assert.equal(login.status, 302, stderr);
    const cookie = login.headers.get('set-cookie');
    assert.match(cookie, /HttpOnly/i);
    assert.match(cookie, /SameSite=Strict/i);

    const inventory = await fetch(`${baseUrl}/inventory`, { headers: { cookie } });
    assert.equal(inventory.status, 200, stderr);
    assert.match(await inventory.text(), /0 total assets in system/);
});

test('rejected Excel imports are archived and removed from live inventory for corrected reupload', async (t) => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cognixasset-import-test-'));
    const dbPath = path.join(tempDir, 'database.sqlite');
    const port = 3800 + Math.floor(Math.random() * 500);
    const baseUrl = `http://127.0.0.1:${port}`;
    const child = spawn(process.execPath, ['server.js'], {
        cwd: projectRoot,
        env: {
            ...process.env,
            NODE_ENV: 'production',
            HOST: '127.0.0.1',
            PORT: String(port),
            DB_PATH: dbPath,
            JWT_SECRET: 'test-secret-that-is-long-enough-for-tests',
            ADMIN_USERNAME: 'testadmin',
            ADMIN_PASSWORD: 'StrongTestPassword123!'
        },
        stdio: ['ignore', 'pipe', 'pipe']
    });

    let stderr = '';
    child.stderr.on('data', chunk => { stderr += chunk; });
    t.after(async () => {
        if (child.exitCode === null) child.kill('SIGTERM');
        await new Promise(resolve => child.once('exit', resolve));
        fs.rmSync(tempDir, { recursive: true, force: true });
    });

    await waitForHealth(baseUrl, child);
    const cookie = await login(baseUrl, 'testadmin', 'StrongTestPassword123!');
    const workbook = buildImportWorkbookBuffer('IMP-REJECT-001', 'SN-REJECT-001');

    const uploadHtml = await uploadWorkbook(baseUrl, cookie, workbook);
    assert.match(uploadHtml, /Successfully imported 1/i, stderr);

    const imported = await dbGet(dbPath, `SELECT id, status FROM assets WHERE asset_tag = ?`, ['IMP-REJECT-001']);
    assert.equal(imported.status, 'pending');

    const rejectAll = await fetch(`${baseUrl}/pending-imports/reject-all`, {
        method: 'POST',
        headers: { cookie },
        redirect: 'manual'
    });
    assert.equal(rejectAll.status, 302, stderr);

    const liveAfterReject = await dbGet(dbPath, `SELECT count(*) as c FROM assets WHERE asset_tag = ?`, ['IMP-REJECT-001']);
    assert.equal(liveAfterReject.c, 0);
    const archivedAfterReject = await dbGet(
        dbPath,
        `SELECT count(*) as c FROM asset_archive WHERE asset_tag = ? AND status = 'rejected' AND source_type = 'excel_import'`,
        ['IMP-REJECT-001']
    );
    assert.equal(archivedAfterReject.c, 1);

    const reuploadHtml = await uploadWorkbook(baseUrl, cookie, workbook);
    assert.match(reuploadHtml, /Successfully imported 1/i, stderr);
    const liveAfterReupload = await dbGet(dbPath, `SELECT count(*) as c FROM assets WHERE asset_tag = ? AND status = 'pending'`, ['IMP-REJECT-001']);
    assert.equal(liveAfterReupload.c, 1);
});
