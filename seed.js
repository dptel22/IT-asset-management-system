const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcrypt');
const { db, run, query } = require('./db');

const locations = ['Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Pune'];
const departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales'];

// Realistic Indian Names
const firstNames = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advik', 'Pranav', 'Kabir', 'Ritvik', 'Rohan', 'Dhruv', 'Ananya', 'Diya', 'Suhana', 'Aaradhya', 'Anika', 'Aadhya', 'Saanvi', 'Myra', 'Kriti', 'Neha', 'Pooja', 'Priya', 'Riya', 'Roshni', 'Sneha', 'Shruti', 'Simran', 'Tanvi', 'Vaishnavi'];
const lastNames = ['Sharma', 'Verma', 'Gupta', 'Malhotra', 'Bhatia', 'Kaur', 'Singh', 'Patel', 'Desai', 'Joshi', 'Mehta', 'Iyer', 'Menon', 'Nair', 'Reddy', 'Rao', 'Choudhury', 'Das', 'Sen', 'Bose', 'Dutta', 'Banerjee', 'Kapoor', 'Khanna', 'Chawla', 'Agarwal', 'Mishra'];

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomItem(arr) {
    return arr[getRandomInt(0, arr.length - 1)];
}

function getRandomDate(start, end) {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

async function seedData() {
    console.log("Starting database seeding...");

    const passwordHash = await bcrypt.hash('admin', 10);

    // 1. Create Users & Employees
    console.log("Generating users and employees...");
    const employees = [];
    const users = [];

    // Super Admin
    const superAdminUserId = uuidv4();
    const superAdminEmpId = uuidv4();
    users.push({ id: superAdminUserId, username: 'admin', password: passwordHash, role: 'super_admin' });
    employees.push({ id: superAdminEmpId, user_id: superAdminUserId, name: 'Sanjay Kumar', email: 'superadmin@cognixasset.com', phone: '9876543210', department: 'IT', location: 'Bengaluru', status: 'active' });

    // 3 Admins
    for (let i = 0; i < 3; i++) {
        const userId = uuidv4();
        const empId = uuidv4();
        const fname = getRandomItem(firstNames);
        const lname = getRandomItem(lastNames);
        const username = `admin${i+1}`;
        const email = `${fname.toLowerCase()}.${lname.toLowerCase()}_admin@cognixasset.com`;
        users.push({ id: userId, username: username, password: passwordHash, role: 'admin' });
        employees.push({ id: empId, user_id: userId, name: `${fname} ${lname}`, email: email, phone: `987654321${i+1}`, department: 'IT', location: getRandomItem(locations), status: 'active' });
    }

    // 35 Employees
    for (let i = 0; i < 35; i++) {
        const userId = uuidv4();
        const empId = uuidv4();
        const fname = getRandomItem(firstNames);
        const lname = getRandomItem(lastNames);
        const username = `user${i+1}`;
        const email = `${fname.toLowerCase()}.${lname.toLowerCase()}${i}@cognixasset.com`;
        users.push({ id: userId, username: username, password: passwordHash, role: 'employee' });
        employees.push({ id: empId, user_id: userId, name: `${fname} ${lname}`, email: email, phone: `98${getRandomInt(10000000, 99999999)}`, department: getRandomItem(departments), location: getRandomItem(locations), status: 'active' });
    }

    for (const u of users) {
        await run(`INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)`, [u.id, u.username, u.password, u.role]);
    }
    for (const e of employees) {
        await run(`INSERT INTO employees (id, user_id, name, email, phone, department, location, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, [e.id, e.user_id, e.name, e.email, e.phone, e.department, e.location, e.status]);
    }

    // 2. Generate Assets
    console.log("Generating assets...");
    const assets = [];
    const assetCategories = [
        { type: 'Laptop', count: 80, brands: ['Dell Latitude', 'Dell Precision', 'HP Elitebook', 'Lenovo ThinkPad'] },
        { type: 'Desktop', count: 20, brands: ['Dell Optiplex', 'HP ProDesk'] },
        { type: 'Monitor', count: 30, brands: ['Dell', 'LG', 'Samsung'] },
        { type: 'Printer', count: 10, brands: ['HP LaserJet', 'Epson EcoTank', 'Canon imageCLASS'] },
        { type: 'Network', count: 10, brands: ['Cisco', 'Aruba', 'Ubiquiti'] },
        { type: 'Server', count: 5, brands: ['Dell PowerEdge', 'HPE ProLiant'] },
        { type: 'Mobile', count: 10, brands: ['Apple iPhone', 'Samsung Galaxy'] }
    ];

    const today = new Date();
    const fiveYearsAgo = new Date(today.getFullYear() - 5, today.getMonth(), today.getDate());
    
    let tagCounter = 1000;
    for (const cat of assetCategories) {
        for (let i = 0; i < cat.count; i++) {
            const assetId = uuidv4();
            const brandInfo = getRandomItem(cat.brands);
            const purchaseDate = getRandomDate(fiveYearsAgo, today);
            const warrantyDate = new Date(purchaseDate.getTime() + (3 * 365 * 24 * 60 * 60 * 1000)); // 3 years warranty
            
            // Randomly assign 60% of assets
            const isAssigned = Math.random() > 0.4;
            const currentOwner = isAssigned ? getRandomItem(employees).id : null;
            const status = isAssigned ? 'assigned' : getRandomItem(['available', 'maintenance']);
            
            assets.push({
                id: assetId,
                asset_tag: `AST-${tagCounter++}`,
                brand: brandInfo.split(' ')[0],
                model: brandInfo.substring(brandInfo.indexOf(' ') + 1) || brandInfo,
                serial_number: `SN-${uuidv4().substring(0,8).toUpperCase()}`,
                category: cat.type,
                purchase_date: purchaseDate.toISOString().split('T')[0],
                warranty_date: warrantyDate.toISOString().split('T')[0],
                purchase_cost: getRandomInt(500, 3000),
                department: getRandomItem(departments),
                location: getRandomItem(locations),
                status: status,
                current_owner_id: currentOwner
            });
        }
    }

    for (const a of assets) {
        await run(`INSERT INTO assets (id, asset_tag, brand, model, serial_number, category, purchase_date, warranty_date, purchase_cost, department, location, status, current_owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, 
        [a.id, a.asset_tag, a.brand, a.model, a.serial_number, a.category, a.purchase_date, a.warranty_date, a.purchase_cost, a.department, a.location, a.status, a.current_owner_id]);
    }

    // 3. Generate History
    console.log("Generating asset history...");
    const eventTypes = ['Purchased', 'Added', 'Assigned', 'Reassigned', 'Maintenance Start', 'Maintenance End', 'Returned'];
    
    for (const a of assets) {
        const numEvents = getRandomInt(3, 10);
        let eventDate = new Date(a.purchase_date);
        
        for (let i = 0; i < numEvents; i++) {
            eventDate = new Date(eventDate.getTime() + getRandomInt(1, 30) * 24 * 60 * 60 * 1000); // add 1-30 days
            if (eventDate > today) break;
            
            const eventType = getRandomItem(eventTypes);
            await run(`INSERT INTO asset_history (id, asset_id, event_type, description, date, created_by) VALUES (?, ?, ?, ?, ?, ?)`, 
            [uuidv4(), a.id, eventType, `Asset ${eventType.toLowerCase()} log entry.`, eventDate.toISOString(), superAdminUserId]);
        }
    }

    // 4. Generate Transfers
    console.log("Generating transfers...");
    const createTransfers = async (count, status) => {
        for(let i=0; i<count; i++) {
            await run(`INSERT INTO transfers (id, asset_id, from_employee_id, to_employee_id, requested_by, approved_by, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, 
            [uuidv4(), getRandomItem(assets).id, getRandomItem(employees).id, getRandomItem(employees).id, getRandomItem(users).id, superAdminUserId, status, `Transfer note for ${status}`]);
        }
    };
    await createTransfers(20, 'completed');
    await createTransfers(10, 'pending');
    await createTransfers(5, 'rejected');

    // 5. Generate Maintenance
    console.log("Generating maintenance tickets...");
    const createMaintenance = async (count, status) => {
        for(let i=0; i<count; i++) {
            await run(`INSERT INTO maintenance (id, asset_id, issue_description, status, reported_by, resolution_notes) VALUES (?, ?, ?, ?, ?, ?)`, 
            [uuidv4(), getRandomItem(assets).id, `Issue with performance/hardware.`, status, getRandomItem(users).id, status === 'completed' ? 'Replaced parts and tested.' : null]);
        }
    };
    await createMaintenance(15, 'completed');
    await createMaintenance(8, 'in_progress');
    await createMaintenance(5, 'awaiting_parts');
    await createMaintenance(5, 'pending');

    // 6. Generate Requests
    console.log("Generating requests...");
    const createRequests = async (count, status) => {
        for(let i=0; i<count; i++) {
            await run(`INSERT INTO requests (id, employee_id, request_type, category, justification, status, decided_by) VALUES (?, ?, ?, ?, ?, ?, ?)`, 
            [uuidv4(), getRandomItem(employees).id, 'New Hardware', 'Laptop', 'Required for new project', status, status !== 'pending' ? superAdminUserId : null]);
        }
    };
    await createRequests(15, 'approved');
    await createRequests(10, 'pending');
    await createRequests(5, 'rejected');

    // 7. Generate Notifications
    console.log("Generating notifications...");
    for (let i = 0; i < 120; i++) {
        const type = getRandomItem(['info', 'warning', 'success', 'critical']);
        await run(`INSERT INTO notifications (id, user_id, title, message, type, is_read) VALUES (?, ?, ?, ?, ?, ?)`, 
        [uuidv4(), getRandomItem(users).id, `System Alert: ${type}`, `This is a generated notification detailing a system event.`, type, getRandomInt(0, 1)]);
    }

    console.log("Database seeded successfully!");
}

module.exports = { seedData };
