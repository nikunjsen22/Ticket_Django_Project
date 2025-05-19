"""
Emergency database initialization script.
This script should be run once to ensure the database schema is properly set up.
"""
import os
import sqlite3
import sys

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nikku.settings')

import django
django.setup()

from django.db import connection
from django.core.management import call_command
from django.contrib.auth import get_user_model

def reset_and_initialize_db():
    print("=============================================")
    print("EMERGENCY DATABASE INITIALIZATION")
    print("=============================================")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    print(f"Database path: {db_path}")
    
    if os.path.exists(db_path):
        print(f"Backing up existing database to {db_path}.bak")
        try:
            if os.path.exists(f"{db_path}.bak"):
                os.remove(f"{db_path}.bak")
            os.rename(db_path, f"{db_path}.bak")
            print("Backup created successfully")
        except Exception as e:
            print(f"Failed to backup database: {e}")
    
    # Create fresh migrations
    print("\nGenerating fresh migrations...")
    call_command('makemigrations')
    
    # Apply migrations
    print("\nApplying all migrations...")
    call_command('migrate', '--run-syncdb')
    
    # Apply specific migrations to ensure auth and nikkuapp are fully migrated
    print("\nApplying specific migrations...")
    call_command('migrate', 'auth')
    call_command('migrate', 'nikkuapp')
    
    # Verify the CustomUser table was created
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nikkuapp_customuser';")
        result = cursor.fetchone()
        if result:
            print("\n✅ nikkuapp_customuser table exists")
        else:
            print("\n❌ ERROR: nikkuapp_customuser table is missing!")
    
    # Create a superuser for initial login
    print("\nCreating superuser for initial access...")
    User = get_user_model()
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser('admin@example.com', 'Admin User', '123456', role='admin')
        print("✅ Superuser created successfully")
    else:
        print("Superuser already exists")
    
    print("\nDatabase initialization complete!")
    print("=============================================")
    print("You can now log in with:")
    print("Email: admin@example.com")
    print("Password: 123456")
    print("=============================================")

if __name__ == "__main__":
    reset_and_initialize_db() 