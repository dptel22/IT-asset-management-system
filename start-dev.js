const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const dbFile = path.resolve(__dirname, 'database.sqlite');
const serverScript = path.resolve(__dirname, 'server.js');

async function main() {
    console.log("=== CognixAsset Startup Sequence ===");
    
    let shouldSeed = false;
    
    // 1. Check if DB exists
    if (!fs.existsSync(dbFile)) {
        console.log("[1] No database found. SQLite file will be created automatically.");
        shouldSeed = true;
    } else {
        console.log("[1] Database already exists.");
    }
    
    // Initialize schema
    const { initDB, get } = require('./db.js');
    console.log("[2] Initializing database schema...");
    await initDB();
    console.log("    Schema initialized successfully.");

    const userCount = await get(`SELECT count(*) as count FROM users`);
    if (userCount.count === 0) {
        shouldSeed = true;
    }

    // 2. Seed Data if the DB file is new or the schema is empty
    if (shouldSeed) {
        console.log("[3] Seeding database with realistic local demo data...");
        const { seedData } = require('./seed.js');
        await seedData();
        console.log("    Seeding complete.");
    } else {
        console.log(`[3] Database already seeded with ${userCount.count} users. Skipping generation.`);
    }

    // 3. Start Backend
    console.log("[4] Starting Express server...");
    const serverProcess = spawn(process.execPath, [serverScript], { stdio: 'inherit' });

    // 4. Open Browser
    setTimeout(async () => {
        console.log("[5] Opening browser to http://localhost:3000");
        try {
            const open = (await import('open')).default;
            await open('http://localhost:3000');
        } catch (e) {
            console.log("Could not open browser automatically.");
        }
    }, 1500); // Wait briefly for server to bind

    serverProcess.on('close', (code) => {
        console.log(`Server process exited with code ${code}`);
    });
}

main().catch(console.error);
