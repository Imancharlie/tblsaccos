#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tblsaccos.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, MemberProfile

def create_superuser():
    try:
        # Create superuser
        user = User.objects.create_user(
            username='admin',
            email='admin@tblsaccos.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            user_type='admin',
            phone_number='1234567890',
            employee_id='ADMIN001',
            department='Administration'
        )
        
        # Create MemberProfile
        member_profile = MemberProfile.objects.create(
            user=user,
            bank_name='TBL Bank',
            account_number='ADMIN001',
            salary_number='ADMIN001',
            monthly_salary=0
        )
        
        print(f"Superuser created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@tblsaccos.com")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()






