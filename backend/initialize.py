"""
Initialize script for Breathe ESG deployment.
Runs migrations, creates sample data, and ensures everything is ready.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def initialize():
    """Initialize the application."""
    print("=" * 60)
    print("Breathe ESG - Database Initialization")
    print("=" * 60)
    print()
    
    # Run migrations
    print("[1/3] Running migrations...")
    try:
        call_command('migrate', verbosity=0)
        print("✓ Migrations completed")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False
    
    print()
    
    # Create demo user if doesn't exist
    print("[2/3] Setting up demo user...")
    try:
        user, created = User.objects.get_or_create(
            username='analyst@breatheesg.com',
            defaults={
                'email': 'analyst@breatheesg.com',
                'first_name': 'Demo',
                'last_name': 'Analyst',
            }
        )
        user.set_password('demo1234')
        user.save()
        
        # Ensure token exists
        token, token_created = Token.objects.get_or_create(user=user)
        
        if created:
            print(f"✓ Created demo user: analyst@breatheesg.com")
        else:
            print(f"✓ Demo user exists: analyst@breatheesg.com")
        
        print(f"  Token: {token.key[:20]}...")
    except Exception as e:
        print(f"✗ User setup failed: {e}")
        return False
    
    print()
    
    # Populate sample data
    print("[3/3] Populating sample data...")
    try:
        call_command('populate_sample_data', verbosity=0)
        print("✓ Sample data populated")
    except Exception as e:
        print(f"✗ Sample data population failed: {e}")
        # Don't fail here - sample data is optional
    
    print()
    print("=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)
    print()
    print("Demo Login Credentials:")
    print("  Email:    analyst@breatheesg.com")
    print("  Password: demo1234")
    print()
    
    return True


if __name__ == '__main__':
    success = initialize()
    sys.exit(0 if success else 1)
