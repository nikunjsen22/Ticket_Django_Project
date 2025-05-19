"""
Database setup script to ensure migrations are properly applied,
particularly for the CustomUser model which is essential for authentication.
"""
import os
import subprocess
import sys
import time

def setup_database():
    print("========== DATABASE SETUP STARTING ==========")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        print("Making migrations for nikkuapp...")
        subprocess.run([sys.executable, "manage.py", "makemigrations", "nikkuapp"], check=True)
        
        print("Applying migrations with run-syncdb...")
        subprocess.run([sys.executable, "manage.py", "migrate", "--run-syncdb"], check=True)
        
        print("Running specific migration for auth and nikkuapp...")
        subprocess.run([sys.executable, "manage.py", "migrate", "auth"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate", "nikkuapp"], check=True)
        
        # Verify the CustomUser table exists
        try:
            result = subprocess.run(
                [sys.executable, "manage.py", "shell", "-c", 
                 "from django.db import connection; print('Table exists:' if 'nikkuapp_customuser' in connection.introspection.table_names() else 'Table MISSING:')"],
                check=True, capture_output=True, text=True
            )
            print(f"Verification result: {result.stdout}")
        except Exception as e:
            print(f"Verification error: {e}")
        
        print("Database setup complete.")
    except Exception as e:
        print(f"ERROR during database setup: {e}")
        raise

if __name__ == "__main__":
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nikku.settings')
    setup_database()
    print("========== DATABASE SETUP FINISHED ==========") 