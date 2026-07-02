#!/bin/bash
echo "Testing User Login..."
USER_COOKIE=$(curl -s -i -X POST -d "username=user1&password=admin" http://127.0.0.1:3000/login | grep "set-cookie:" | awk '{print $2}' | tr -d '\r')
echo "User Cookie: $USER_COOKIE"

echo "Testing User Access to /assets/import-template..."
USER_HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Cookie: $USER_COOKIE" http://127.0.0.1:3000/assets/import-template)
echo "User HTTP Status: $USER_HTTP_STATUS (Expected: 403)"

echo "Testing Admin Login..."
ADMIN_COOKIE=$(curl -s -i -X POST -d "username=admin&password=admin" http://127.0.0.1:3000/login | grep "set-cookie:" | awk '{print $2}' | tr -d '\r')
echo "Admin Cookie: $ADMIN_COOKIE"

echo "Testing Admin Access to /assets/import-template..."
curl -s -D - -H "Cookie: $ADMIN_COOKIE" http://127.0.0.1:3000/assets/import-template -o downloaded.xlsx | head -n 5

echo "Testing Admin Upload..."
curl -s -H "Cookie: $ADMIN_COOKIE" -F "excel_file=@test_upload.xlsx" http://127.0.0.1:3000/assets/import > upload_result.html
grep -o "Successfully imported [0-9]* rows. Skipped [0-9]* rows." upload_result.html
