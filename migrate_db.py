#!/usr/bin/env python3
"""
Database migration script to add validation and authentication fields
"""
import os
import sqlite3
import shutil
from datetime import datetime

def migrate_database():
    """Add new columns to existing database"""
    db_path = 'instance/health_monitor.db'
    backup_path = f'instance/health_monitor_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. Run the app first to create it.")
        return
    
    # Create backup
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(endpoints)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add validation fields to endpoints table
        if 'validation_enabled' not in columns:
            print("Adding validation_enabled column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN validation_enabled BOOLEAN DEFAULT 0")
        
        if 'validation_type' not in columns:
            print("Adding validation_type column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN validation_type VARCHAR(20)")
        
        if 'expected_content' not in columns:
            print("Adding expected_content column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN expected_content TEXT")
        
        # Add authentication fields to endpoints table
        if 'auth_type' not in columns:
            print("Adding auth_type column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN auth_type VARCHAR(20)")
        
        if 'auth_username' not in columns:
            print("Adding auth_username column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN auth_username VARCHAR(200)")
        
        if 'auth_password' not in columns:
            print("Adding auth_password column...")
            cursor.execute("ALTER TABLE endpoints ADD COLUMN auth_password VARCHAR(200)")
        
        # Check health_checks table
        cursor.execute("PRAGMA table_info(health_checks)")
        health_check_columns = [col[1] for col in cursor.fetchall()]
        
        # Add validation_error field to health_checks table
        if 'validation_error' not in health_check_columns:
            print("Adding validation_error column to health_checks...")
            cursor.execute("ALTER TABLE health_checks ADD COLUMN validation_error TEXT")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print(f"Backup saved to: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Restoring from backup...")
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("Database restored from backup")
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
