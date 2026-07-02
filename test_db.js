const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('database.sqlite');
db.all(`
    SELECT status, count(*) as count
    FROM (
       SELECT status
       FROM requests
       WHERE employee_id = '0b85af6e-3b08-4c9d-99ec-1551191f9b10'

       UNION ALL

       SELECT CASE
           WHEN a.status = 'pending' THEN 'pending'
           WHEN a.status = 'rejected' THEN 'rejected'
           ELSE 'approved'
       END as status
       FROM assets a
       WHERE EXISTS (
           SELECT 1
           FROM asset_history h
           WHERE h.asset_id = a.id
             AND h.event_type = 'Imported'
             AND h.created_by = '0b85af6e-3b08-4c9d-99ec-1551191f9b10'
       )
    )
    GROUP BY status
`, (err, rows) => {
    if (err) console.error(err);
    console.log("TEST:", rows);
});
