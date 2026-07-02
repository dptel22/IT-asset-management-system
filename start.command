#!/bin/bash
# Move to the directory where this script is located
cd "$(dirname "$0")"

echo "============================================="
echo "   Starting CognixAsset (Fully Offline Mode) "
echo "============================================="
echo ""
echo "Initializing offline SQLite database and starting server..."
node start-dev.js
