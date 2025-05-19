"""
Database setup script to ensure migrations are properly applied,
particularly for the CustomUser model which is essential for authentication.
"""
import os
import subprocess
import sys

def setup_database():
    print("Setting up database...")
    
    # Run the migrations in the correct order
    subprocess.run([sys.executable, "manage.py", "makemigrations", "nikkuapp"], check=True)
    subprocess.run([sys.executable, "manage.py", "migrate", "--run-syncdb"], check=True)
    
    print("Database setup complete.")

if __name__ == "__main__":
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nikku.settings')
    setup_database() 