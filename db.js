const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.resolve(process.env.DB_PATH || path.join(__dirname, 'database.sqlite'));
fs.mkdirSync(path.dirname(dbPath), { recursive: true });

const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error("Error opening database " + err.message);
    }
});

function initDB() {
    return new Promise((resolve, reject) => {
        db.serialize(() => {
            // Enable foreign keys
            db.run('PRAGMA foreign_keys = ON;');
            db.run('PRAGMA journal_mode = WAL;');
            db.run('PRAGMA busy_timeout = 5000;');

            // Users Table
            db.run(`CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('super_admin', 'admin', 'employee')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`);

            // Employees Table
            db.run(`CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department TEXT NOT NULL,
                location TEXT NOT NULL, designation TEXT, join_date TEXT, manager_id TEXT,
                emergency_contact TEXT,
                address TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )`);

            // Assets Table
            db.run(`CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                asset_tag TEXT UNIQUE NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                purchase_date DATE,
                warranty_date DATE,
                purchase_cost REAL,
                department TEXT,
                location TEXT,
                status TEXT NOT NULL DEFAULT 'available',
                current_owner_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (current_owner_id) REFERENCES employees (id) ON DELETE SET NULL
            )`);

            // Asset Archive Table (Soft Deletes)
            db.run(`CREATE TABLE IF NOT EXISTS asset_archive (
                id TEXT PRIMARY KEY,
                original_asset_id TEXT NOT NULL,
                asset_tag TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT NOT NULL,
                category TEXT NOT NULL,
                purchase_date DATE,
                warranty_date DATE,
                purchase_cost REAL,
                department TEXT,
                location TEXT,
                status TEXT,
                archived_by TEXT NOT NULL,
                archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                FOREIGN KEY (archived_by) REFERENCES users (id)
            )`);

            // Asset History Table
            db.run(`CREATE TABLE IF NOT EXISTS asset_history (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
            )`);

            // Transfers Table
            db.run(`CREATE TABLE IF NOT EXISTS transfers (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                from_employee_id TEXT,
                to_employee_id TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                approved_by TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                completion_date DATETIME,
                notes TEXT,
                transfer_type TEXT NOT NULL DEFAULT 'admin_initiated',
                FOREIGN KEY (asset_id) REFERENCES assets (id),
                FOREIGN KEY (from_employee_id) REFERENCES employees (id),
                FOREIGN KEY (to_employee_id) REFERENCES employees (id),
                FOREIGN KEY (requested_by) REFERENCES users (id),
                FOREIGN KEY (approved_by) REFERENCES users (id)
            )`);

            // Maintenance Table
            db.run(`CREATE TABLE IF NOT EXISTS maintenance (
                id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                reported_by TEXT NOT NULL,
                reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolution_notes TEXT,
                resolved_date DATETIME,
                FOREIGN KEY (asset_id) REFERENCES assets (id),
                FOREIGN KEY (reported_by) REFERENCES users (id)
            )`);

            // Requests Table
            db.run(`CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                request_type TEXT NOT NULL,
                category TEXT,
                justification TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                decision_date DATETIME,
                decided_by TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id),
                FOREIGN KEY (decided_by) REFERENCES users (id)
            )`);

            // Tasks Table
            db.run(`CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                assigned_to TEXT NOT NULL,
                assigned_by TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date DATE,
                status TEXT NOT NULL DEFAULT 'To Do',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_to) REFERENCES employees (id),
                FOREIGN KEY (assigned_by) REFERENCES users (id)
            )`);

            // Approvals Table
            db.run(`CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                request_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                decided_by TEXT,
                decided_date DATETIME,
                notes TEXT,
                FOREIGN KEY (decided_by) REFERENCES users (id)
            )`);

            // Notifications Table
            db.run(`CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )`, (err) => {
                if (err) return reject(err);
                
                const newColumns = [
                    'sl_no TEXT',
                    'monitor_make TEXT',
                    'monitor_serial_no TEXT',
                    'asset_owner_pl_no TEXT',
                    'asset_usage_status TEXT',
                    'in_warranty_status TEXT',
                    'system_serial_no TEXT',
                    'host_name TEXT',
                    'group_name TEXT',
                    'division TEXT',
                    'user_name TEXT',
                    'designation TEXT',
                    'ip_address TEXT',
                    'mac_address TEXT',
                    'network_type TEXT',
                    'drona_domain TEXT',
                    'os_version TEXT',
                    'antivirus_status TEXT',
                    'usb_status TEXT',
                    'admin_privilege TEXT'
                ];

                db.all("PRAGMA table_info(assets)", (err, rows) => {
                    if (err) return reject(err);
                    const existingColumns = rows.map(r => r.name);
                    const pendingMigrations = [];
                    
                    newColumns.forEach(colDef => {
                        const colName = colDef.split(' ')[0];
                        if (!existingColumns.includes(colName)) {
                            pendingMigrations.push(`ALTER TABLE assets ADD COLUMN ${colDef}`);
                        }
                    });
                    if (!existingColumns.includes('hasWarranty')) {
                        pendingMigrations.push(`ALTER TABLE assets ADD COLUMN hasWarranty INTEGER DEFAULT 0`);
                    }
                    if (!existingColumns.includes('warrantyExpiryDate')) {
                        pendingMigrations.push(`ALTER TABLE assets ADD COLUMN warrantyExpiryDate DATE`);
                    }
                    if (!existingColumns.includes('source_type')) {
                        pendingMigrations.push(`ALTER TABLE assets ADD COLUMN source_type TEXT`);
                    }
                    if (!existingColumns.includes('source_user_id')) {
                        pendingMigrations.push(`ALTER TABLE assets ADD COLUMN source_user_id TEXT`);
                    }

                    db.all("PRAGMA table_info(asset_archive)", (err, rowsArchive) => {
                        if (err) return reject(err);
                        const existingArchiveCols = rowsArchive.map(r => r.name);
                        
                        newColumns.forEach(colDef => {
                            const colName = colDef.split(' ')[0];
                            if (!existingArchiveCols.includes(colName)) {
                                pendingMigrations.push(`ALTER TABLE asset_archive ADD COLUMN ${colDef}`);
                            }
                        });
                        if (!existingArchiveCols.includes('hasWarranty')) {
                            pendingMigrations.push(`ALTER TABLE asset_archive ADD COLUMN hasWarranty INTEGER DEFAULT 0`);
                        }
                        if (!existingArchiveCols.includes('warrantyExpiryDate')) {
                            pendingMigrations.push(`ALTER TABLE asset_archive ADD COLUMN warrantyExpiryDate DATE`);
                        }
                        if (!existingArchiveCols.includes('source_type')) {
                            pendingMigrations.push(`ALTER TABLE asset_archive ADD COLUMN source_type TEXT`);
                        }
                        if (!existingArchiveCols.includes('source_user_id')) {
                            pendingMigrations.push(`ALTER TABLE asset_archive ADD COLUMN source_user_id TEXT`);
                        }
                        
                        db.all("PRAGMA table_info(employees)", (err, empRows) => {
                            if (err) return reject(err);
                            const existingEmpCols = empRows.map(r => r.name);
                            if (!existingEmpCols.includes('emergency_contact')) {
                                pendingMigrations.push(`ALTER TABLE employees ADD COLUMN emergency_contact TEXT`);
                            }
                            if (!existingEmpCols.includes('address')) {
                                pendingMigrations.push(`ALTER TABLE employees ADD COLUMN address TEXT`);
                            }
                            
                            db.all("PRAGMA table_info(transfers)", (err, tRows) => {
                                if (err) return reject(err);
                                const existingTCols = tRows.map(r => r.name);
                                if (!existingTCols.includes('transfer_type')) {
                                    pendingMigrations.push(`ALTER TABLE transfers ADD COLUMN transfer_type TEXT NOT NULL DEFAULT 'admin_initiated'`);
                                }
                                db.all("PRAGMA table_info(requests)", (err, requestRows) => {
                                    if (err) return reject(err);
                                    const existingRequestCols = requestRows.map(r => r.name);
                                    if (!existingRequestCols.includes('fulfilled_asset_id')) {
                                        pendingMigrations.push(`ALTER TABLE requests ADD COLUMN fulfilled_asset_id TEXT`);
                                    }
                                    if (pendingMigrations.length === 0) return resolve();
                                    db.exec(pendingMigrations.join(';'), (migrationErr) => {
                                        if (migrationErr) reject(migrationErr);
                                        else resolve();
                                    });
                                });
                            });
                        });
                    });
                });
            });
        });
    });
}

// Wrapper for async queries
const query = (sql, params = []) => {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

const run = (sql, params = []) => {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function(err) {
            if (err) reject(err);
            else resolve(this);
        });
    });
};

const get = (sql, params = []) => {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
};

function transaction(work) {
    return new Promise((resolve, reject) => {
        const txRun = (sql, params = []) => new Promise((res, rej) => {
            db.run(sql, params, function(err) { if (err) rej(err); else res(this); });
        });
        const txGet = (sql, params = []) => new Promise((res, rej) => {
            db.get(sql, params, (err, row) => { if (err) rej(err); else res(row); });
        });
        const txQuery = (sql, params = []) => new Promise((res, rej) => {
            db.all(sql, params, (err, rows) => { if (err) rej(err); else res(rows); });
        });

        db.serialize(async () => {
            try {
                await txRun('PRAGMA foreign_keys = ON');
                await txRun('BEGIN IMMEDIATE');
                try {
                    const result = await work({ run: txRun, get: txGet, query: txQuery });
                    await txRun('COMMIT');
                    resolve(result);
                } catch (err) {
                    try { await txRun('ROLLBACK'); } catch {}
                    reject(err);
                }
            } catch (err) {
                reject(err);
            }
        });
    });
}

module.exports = {
    db,
    initDB,
    query,
    run,
    get,
    transaction
};
