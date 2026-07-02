const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const envExamplePath = path.join(__dirname, '.env.example');
const envPath = path.join(__dirname, '.env');

if (!fs.existsSync(envExamplePath)) {
  console.error('Error: .env.example not found in project root!');
  process.exit(1);
}

if (!fs.existsSync(envPath)) {
  fs.copyFileSync(envExamplePath, envPath);
}

let content = fs.readFileSync(envPath, 'utf8');

// Generate secure tokens
const jwtSecret = crypto.randomBytes(32).toString('hex');
const adminPassword = 'Admin_' + crypto.randomBytes(6).toString('hex') + '!2026';

// Replace values in .env file
content = content.replace(/JWT_SECRET=.*/, 'JWT_SECRET=' + jwtSecret);
content = content.replace(/ADMIN_PASSWORD=.*/, 'ADMIN_PASSWORD=' + adminPassword);
content = content.replace(/COOKIE_SECURE=.*/, 'COOKIE_SECURE=0');

fs.writeFileSync(envPath, content, 'utf8');

console.log('=== CONFIGURATION COMPLETE ===');
console.log('ADMIN_USERNAME=admin');
console.log('ADMIN_PASSWORD=' + adminPassword);
console.log('JWT_SECRET=' + jwtSecret);
console.log('==============================');
