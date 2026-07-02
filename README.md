# CognixAsset

CognixAsset is a LAN-deployable IT asset management app built with Node.js, Express, Nunjucks, and SQLite.

## Run Locally

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set the required bootstrap password and start the local app:
   ```bash
   set ADMIN_PASSWORD=ChangeMe12345!
   npm start
   ```

3. Open:
   ```text
   http://localhost:3000
   ```

The startup script initializes the SQLite schema and seeds demo data when the database is new or empty.

## Login

Passwords are required. On a fresh database, the server creates the bootstrap account from `ADMIN_USERNAME` and `ADMIN_PASSWORD`.

Existing seeded development databases use these credentials:

- Username: `admin`, `admin1`, or `user1`
- Password: `admin`

## Docker LAN Deployment

1. Copy `.env.example` to `.env` and replace both secrets.
2. Build and run the service:
   ```bash
   docker compose up -d --build
   ```
3. Open `http://SERVER_LAN_IP:3000` from another device on the LAN.
4. Allow inbound TCP port `3000` in the host firewall only for the trusted LAN.

The named `cognix_data` volume stores `/data/database.sqlite`. Rebuilding the image does not remove that volume.

Back up the database before upgrades:

```bash
docker compose stop cognixasset
docker run --rm -v cognixasset_cognix_data:/data -v "${PWD}:/backup" alpine cp /data/database.sqlite /backup/database.sqlite.backup
docker compose start cognixasset
```

Do not run multiple application replicas against the same SQLite database volume.

## Release Checks

```bash
npm run check
npm test
docker compose config
docker compose build
```

## Local Stack

- Backend: Node.js + Express
- Templates: Nunjucks HTML in `templates/`
- Styling: design-matched CSS embedded in the generated templates, with shared reference styles in `static/css/style.css`
- Database: local SQLite via `sqlite3`
- Auth: local username login with a JWT cookie

## Project Files

- `server.js` defines the local web server, routes, login, health check, and page data queries.
- `db.js` creates the SQLite schema and exposes async query helpers.
- `seed.js` generates users, employees, assets, history, transfers, maintenance tickets, requests, and notifications.
- `start-dev.js` performs local bootstrapping and starts the server.
- `rebuild_templates.py` rebuilds app templates from the sibling UI design folder at `/Users/rithanyamagesh/Desktop/antigravity/ui/ux`.

## Health Check

After the server starts, check local backend/database status at:

```text
http://localhost:3000/api/health
```
