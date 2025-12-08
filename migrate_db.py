#!/usr/bin/env python3
"""
Database migration script to add missing columns to the SMART Edu Task Manager database.
"""
import sqlite3
import os

def migrate_database():
    """Add missing columns and tables to the database."""

    # Path to the database
    db_path = 'instance/smart_edu.db'

    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current task table structure
        cursor.execute("PRAGMA table_info(task);")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current task table columns: {columns}")

        # Add file_path column to task table if it doesn't exist
        if 'file_path' not in columns:
            print("Adding 'file_path' column to task table...")
            cursor.execute("ALTER TABLE task ADD COLUMN file_path VARCHAR(500);")
            print("SUCCESS: Successfully added 'file_path' column to task table")
        else:
            print("SUCCESS: 'file_path' column already exists in task table")

        # Check current submission table structure
        cursor.execute("PRAGMA table_info(submission);")
        submission_columns = [column[1] for column in cursor.fetchall()]
        print(f"Current submission table columns: {submission_columns}")

        # Add feedback columns to submission table if they don't exist
        feedback_columns = ['score', 'feedback', 'feedback_provided_at', 'graded_by']
        for col in feedback_columns:
            if col not in submission_columns:
                print(f"Adding '{col}' column to submission table...")
                if col == 'score':
                    cursor.execute("ALTER TABLE submission ADD COLUMN score INTEGER;")
                elif col == 'feedback':
                    cursor.execute("ALTER TABLE submission ADD COLUMN feedback TEXT;")
                elif col == 'feedback_provided_at':
                    cursor.execute("ALTER TABLE submission ADD COLUMN feedback_provided_at DATETIME;")
                elif col == 'graded_by':
                    cursor.execute("ALTER TABLE submission ADD COLUMN graded_by INTEGER;")
                print(f"SUCCESS: Successfully added '{col}' column to submission table")
            else:
                print(f"SUCCESS: '{col}' column already exists in submission table")

        # Check if class table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='class';")
        class_table_exists = cursor.fetchone()
        if not class_table_exists:
            print("Creating 'class' table...")
            cursor.execute("""
                CREATE TABLE class (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES user (id)
                );
            """)
            print("SUCCESS: Successfully created 'class' table")
        else:
            print("SUCCESS: 'class' table already exists")

        # Check if subject table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subject';")
        subject_table_exists = cursor.fetchone()
        if not subject_table_exists:
            print("Creating 'subject' table...")
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
            print("SUCCESS: Successfully created 'subject' table")
        else:
            print("SUCCESS: 'subject' table already exists")
            # Check if there's a unique constraint on name column and remove it
            cursor.execute("PRAGMA table_info(subject);")
            subject_columns = cursor.fetchall()
            for col in subject_columns:
                if col[1] == 'name' and col[5] == 1:  # col[5] is pk flag, but we need to check constraints
                    print("Checking for unique constraints on subject.name...")
                    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='subject' AND sql LIKE '%UNIQUE%';")
                    unique_indexes = cursor.fetchall()
                    for index_sql in unique_indexes:
                        if 'name' in index_sql[0] and 'UNIQUE' in index_sql[0]:
                            print("Found unique constraint on subject.name, removing it...")
                            # Extract index name from SQL
                            import re
                            match = re.search(r'CREATE UNIQUE INDEX (\w+) ON', index_sql[0])
                            if match:
                                index_name = match.group(1)
                                cursor.execute(f"DROP INDEX {index_name};")
                                print(f"SUCCESS: Dropped unique index {index_name}")
                            break
                    break

        # Check if teacher_classes table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacher_classes';")
        teacher_classes_exists = cursor.fetchone()
        if not teacher_classes_exists:
            print("Creating 'teacher_classes' association table...")
            cursor.execute("""
                CREATE TABLE teacher_classes (
                    teacher_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, class_id),
                    FOREIGN KEY (teacher_id) REFERENCES user (id),
                    FOREIGN KEY (class_id) REFERENCES class (id)
                );
            """)
            print("SUCCESS: Successfully created 'teacher_classes' table")
        else:
            print("SUCCESS: 'teacher_classes' table already exists")

        # Check if teacher_subjects table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacher_subjects';")
        teacher_subjects_exists = cursor.fetchone()
        if not teacher_subjects_exists:
            print("Creating 'teacher_subjects' association table...")
            cursor.execute("""
                CREATE TABLE teacher_subjects (
                    teacher_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, subject_id),
                    FOREIGN KEY (teacher_id) REFERENCES user (id),
                    FOREIGN KEY (subject_id) REFERENCES subject (id)
                );
            """)
            print("SUCCESS: Successfully created 'teacher_subjects' table")
        else:
            print("SUCCESS: 'teacher_subjects' table already exists")

        # Check if class_subjects table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='class_subjects';")
        class_subjects_exists = cursor.fetchone()
        if not class_subjects_exists:
            print("Creating 'class_subjects' association table...")
            cursor.execute("""
                CREATE TABLE class_subjects (
                    class_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    PRIMARY KEY (class_id, subject_id),
                    FOREIGN KEY (class_id) REFERENCES class (id),
                    FOREIGN KEY (subject_id) REFERENCES subject (id)
                );
            """)
            print("SUCCESS: Successfully created 'class_subjects' table")
        else:
            print("SUCCESS: 'class_subjects' table already exists")

        # Check if teacher_class_subjects table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teacher_class_subjects';")
        teacher_class_subjects_exists = cursor.fetchone()
        if not teacher_class_subjects_exists:
            print("Creating 'teacher_class_subjects' association table...")
            cursor.execute("""
                CREATE TABLE teacher_class_subjects (
                    teacher_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, class_id, subject_id),
                    FOREIGN KEY (teacher_id) REFERENCES user (id),
                    FOREIGN KEY (class_id) REFERENCES class (id),
                    FOREIGN KEY (subject_id) REFERENCES subject (id)
                );
            """)
            print("SUCCESS: Successfully created 'teacher_class_subjects' table")
        else:
            print("SUCCESS: 'teacher_class_subjects' table already exists")

        # Check user table structure and update class_name to class_id
        cursor.execute("PRAGMA table_info(user);")
        user_columns = [column[1] for column in cursor.fetchall()]
        print(f"Current user table columns: {user_columns}")

        if 'class_name' in user_columns and 'class_id' not in user_columns:
            print("Renaming 'class_name' column to 'class_id' in user table...")
            # SQLite doesn't support direct column rename, so we need to recreate the table
            cursor.execute("PRAGMA foreign_keys=off;")

            # Create new table structure
            cursor.execute("""
                CREATE TABLE user_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password_hash VARCHAR(128) NOT NULL,
                    user_type VARCHAR(20) NOT NULL,
                    subject VARCHAR(100),
                    class_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES class (id)
                );
            """)

            # Copy data
            cursor.execute("""
                INSERT INTO user_new (id, name, email, password_hash, user_type, subject, created_at)
                SELECT id, name, email, password_hash, user_type, subject, created_at FROM user;
            """)

            # Drop old table and rename new one
            cursor.execute("DROP TABLE user;")
            cursor.execute("ALTER TABLE user_new RENAME TO user;")

            cursor.execute("PRAGMA foreign_keys=on;")
            print("SUCCESS: Successfully renamed 'class_name' to 'class_id' in user table")
        elif 'class_id' in user_columns:
            print("SUCCESS: 'class_id' column already exists in user table")
        else:
            print("WARNING: Neither 'class_name' nor 'class_id' found in user table")

        # Commit the changes
        conn.commit()
        print("SUCCESS: Database migration completed successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("Starting database migration...")
    migrate_database()
    print("Migration script completed.")