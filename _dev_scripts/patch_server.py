import re

with open('server.js', 'r') as f:
    server_content = f.read()

employees_routes = """
app.get('/employees/new', requireAuth, requireAdmin, (req, res) => {
    res.render('add-user.html', { error: null });
});

app.post('/employees', requireAuth, requireAdmin, async (req, res) => {
    const { name, email, department, role, location } = req.body;
    try {
        if (!name || !email || !department || !role || !location) {
            return res.render('add-user.html', { error: 'Please fill all mandatory fields' });
        }
        
        // Ensure email isn't used
        const existingEmp = await get(`SELECT id FROM employees WHERE email = ?`, [email]);
        if (existingEmp) return res.render('add-user.html', { error: 'Email already exists' });
        
        // The username will just be the prefix of email
        const username = email.split('@')[0];
        
        // See if username is taken, append random if so
        let finalUsername = username;
        let existingUser = await get(`SELECT id FROM users WHERE username = ?`, [finalUsername]);
        if (existingUser) {
            finalUsername = username + Math.floor(Math.random() * 1000);
        }

        const user_id = uuidv4();
        await run(`INSERT INTO users (id, username, password, role) VALUES (?, ?, 'Welcome123!', ?)`, [user_id, finalUsername, role]);
        
        const emp_id = uuidv4();
        await run(`INSERT INTO employees (id, user_id, name, email, department, location) VALUES (?, ?, ?, ?, ?, ?)`, 
                  [emp_id, user_id, name, email, department, location]);
                  
        res.redirect('/employees');
    } catch (err) {
        res.render('add-user.html', { error: err.message });
    }
});

app.get('/employees', requireAuth, requireAdmin, async (req, res) => {
"""

profile_post_route = """
app.get('/profile', requireAuth, async (req, res) => {
    const employee = await get(`SELECT * FROM employees WHERE user_id = ?`, [req.user.id]);
    res.render('profile.html', { employee, success: req.query.success });
});

app.post('/profile', requireAuth, async (req, res) => {
    const { phone, emergency_contact, address } = req.body;
    try {
        await run(
            `UPDATE employees SET phone=?, emergency_contact=?, address=? WHERE user_id=?`,
            [phone, emergency_contact, address, req.user.id]
        );
        res.redirect('/profile?success=1');
    } catch(err) {
        res.redirect('/profile?error=' + encodeURIComponent(err.message));
    }
});
"""

# Replace employees route
server_content = server_content.replace(
    "app.get('/employees', requireAuth, requireAdmin, async (req, res) => {",
    employees_routes.strip() + " {"
)

# Replace profile route
old_profile_route = """app.get('/profile', requireAuth, async (req, res) => {
    const employee = await get(`SELECT * FROM employees WHERE user_id = ?`, [req.user.id]);
    res.render('profile.html', { employee });
});"""

server_content = server_content.replace(old_profile_route, profile_post_route.strip())

with open('server.js', 'w') as f:
    f.write(server_content)
print("server.js patched")
