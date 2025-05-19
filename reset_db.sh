#!/bin/bash
# Emergency database reset script for Render deployment

echo "==== EMERGENCY DATABASE RESET ===="
echo "Running from directory: $(pwd)"

# Make sure we're in the correct directory
cd /opt/render/project/src || { echo "Failed to cd to /opt/render/project/src"; exit 1; }
echo "Changed to directory: $(pwd)"

# Run Python reset script
echo "Running database reset script..."
python init_db.py

echo "==== DATABASE RESET COMPLETE ===="

# Additional diagnostic information
echo "Database file information:"
ls -la db.sqlite3*

echo "Table information:"
python manage.py shell -c "from django.db import connection; print('Tables:', connection.introspection.table_names())"

echo "Application can now be restarted" 