#!/bin/bash
ADMIN_COOKIE=$(curl -s -i -X POST -d "username=admin&password=admin" http://127.0.0.1:3000/login | grep -i "set-cookie:" | awk '{print $2}' | tr -d '\r;')
curl -s -D - -H "Cookie: $ADMIN_COOKIE" -F "excel_file=@test_upload.xlsx" http://127.0.0.1:3000/assets/import > upload_result.html
grep -o "Successfully imported [0-9]* rows. Skipped [0-9]* rows." upload_result.html
grep -o "<li>.*</li>" upload_result.html
