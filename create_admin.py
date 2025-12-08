#!/usr/bin/env python3
"""
Script to create the initial admin user for SMART Edu Task Manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import User

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(user_type='admin').first()
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return admin
        
        # Create admin user
        admin = User(
            name='System Administrator',
            email='admin@smartedu.com',
            user_type='admin'
        )
        admin.set_password('admin123')  # Change this in production!
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
        print(f"WARNING: Change this password after first login!")
        
        return admin

if __name__ == '__main__':
    create_admin_user()