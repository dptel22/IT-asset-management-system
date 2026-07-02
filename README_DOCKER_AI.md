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
Do not ask the user for keys. Run the helper script `auto_config.js` in the project root:
```bash
node auto_config.js
```
**CRITICAL**: Parse the console output to extract the generated `ADMIN_USERNAME` and `ADMIN_PASSWORD` so you can display them to the user at the end.

---

## Step 3: Build & Launch Docker Container
Run the build and start orchestration:
```bash
docker compose up -d --build
```
Ensure the build completes with exit code 0.

---

## Step 4: Verify Container Health
Wait 5 seconds for the server to bind, then verify that the server is responding correctly:
```bash
# Using curl (standard shell):
curl -s http://127.0.0.1:3000/api/health

# Or using Node.js directly (highly compatible across OS/Shells):
node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>r.json()).then(console.log).catch(console.error)"
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
