#!/usr/bin/env python3
"""
Script to create the notifications table in the database
Run this script to ensure the Notification table exists
"""

from app import create_app, db
from models.models import Notification

def create_notifications_table():
    """Create the notifications table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("[OK] Database tables created successfully!")
            
            # Check if notifications table exists by querying it
            notification_count = Notification.query.count()
            print(f"[OK] Notifications table exists with {notification_count} records")
            
        except Exception as e:
            print(f"[ERROR] Error creating tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Creating notifications table...")
    create_notifications_table()
    print("Done!")