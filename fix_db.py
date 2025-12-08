#!/usr/bin/env python3
"""
Script to fix database constraints for subject table
"""
import sqlite3
import os

def fix_database():
    """Remove unique constraint from subject.name by recreating the table"""

    db_path = 'instance/smart_edu.db'

    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current table structure
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='subject';")
        table_sql = cursor.fetchone()
        print(f"Current subject table SQL: {table_sql[0] if table_sql else 'Not found'}")

        # Backup existing data
        cursor.execute("SELECT id, name, description, created_by, created_at FROM subject;")
        subjects_data = cursor.fetchall()
        print(f"Found {len(subjects_data)} subjects to preserve")

        # Drop existing table
        cursor.execute("DROP TABLE subject;")
        print("Dropped old subject table")

        # Create new table without UNIQUE constraint
        cursor.execute("""
            CREATE TABLE subject (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES user (id)
            );
        """)
        print("Created new subject table without UNIQUE constraint")

        # Restore data
        for subject in subjects_data:
            cursor.execute("""
                INSERT INTO subject (id, name, description, created_by, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, subject)
        print(f"Restored {len(subjects_data)} subjects")

        conn.commit()
        print("Database fix completed successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("Starting database fix...")
    fix_database()
    print("Fix script completed.")