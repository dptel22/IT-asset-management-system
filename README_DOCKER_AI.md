# AI Agent Instructions: Deploying CognixAsset via Docker

Dear AI Assistant / Agent,

Please read these instructions to automatically build, configure, and launch the CognixAsset IT Asset Management System on this machine. Follow the steps sequentially.

---

## Step 1: Verify Docker Daemon Status
Ensure Docker Desktop is running. Run this command to check the daemon:
```bash
docker info --format "{{json .Name}}"
```
- **If it succeeds**: Proceed to Step 2.
- **If it fails**: Output a clear warning to the User asking them to start **Docker Desktop** on Windows/Mac, wait 10 seconds, and try again.

---

## Step 2: Auto-Configure the `.env` File
Do not ask the user for keys. Generate them programmatically.
1. Read `.env.example`.
2. Generate a secure, random 64-character hexadecimal `JWT_SECRET`.
3. Choose a strong random initial `ADMIN_PASSWORD` (minimum 12 characters, including numbers and special characters).
4. Create a `.env` file from `.env.example` with these values replaced.

*You can run this Node script directly in the terminal to do this step:*
```bash
node -e "
const fs = require('fs');
const crypto = require('crypto');
if (!fs.existsSync('.env')) {
  fs.copyFileSync('.env.example', '.env');
}
let content = fs.readFileSync('.env', 'utf8');
const jwtSecret = crypto.randomBytes(32).toString('hex');
const adminPassword = 'Admin_' + crypto.randomBytes(6).toString('hex') + '!2026';
content = content.replace(/JWT_SECRET=.*/, 'JWT_SECRET=' + jwtSecret);
content = content.replace(/ADMIN_PASSWORD=.*/, 'ADMIN_PASSWORD=' + adminPassword);
content = content.replace(/COOKIE_SECURE=.*/, 'COOKIE_SECURE=0');
fs.writeFileSync('.env', content, 'utf8');
console.log('=== CONFIGURATION COMPLETE ===');
console.log('ADMIN_USERNAME=admin');
console.log('ADMIN_PASSWORD=' + adminPassword);
console.log('JWT_SECRET=' + jwtSecret);
console.log('==============================');
"
```
**CRITICAL**: Log the generated `ADMIN_USERNAME` and `ADMIN_PASSWORD` to the user so they know their login credentials!

---

## Step 3: Build & Launch Docker Container
Run the build and start orchestration:
```bash
docker compose up -d --build
```
Ensure the build completes with exit code 0.

---

## Step 4: Verify Container Health
Wait 5 seconds for the server to bind, then test the healthcheck endpoint:
```bash
curl -s http://127.0.0.1:3000/api/health
```
Verify the output JSON contains `"status":"ok"`.

---

## Step 5: Seed Demo Database (Optional)
Run the seed script inside the running container to populate the database with test assets and employees:
```bash
docker compose exec cognixasset node seed.js
```

---

## Step 6: Print Final Instructions to User
Output the following summary to the user:
- URL: `http://localhost:3000`
- Admin Username: `admin`
- Admin Password: *(The password generated in Step 2)*
- Confirm that the deployment is complete and healthy!
