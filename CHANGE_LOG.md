# CognixAsset Change Log

## 2026-06-10

### Fixed

- Updated local startup so an existing but empty SQLite database is seeded automatically.
- Made `server.js` initialize the SQLite schema before listening, so `npm start` and `npm run dev` both use the same local schema.
- Simplified login to username-only local access.
- Fixed the fallback page route so missing pages return a clean 404 instead of calling `.catch()` on `res.render`.
- Replaced stale FastAPI/Supabase documentation with accurate Express/SQLite instructions.

### Current Local Stack

- Node.js + Express backend
- Nunjucks-rendered frontend templates
- Local SQLite database
- Seeded local users: `admin`, `admin1` to `admin3`, and `user1` to `user35`
