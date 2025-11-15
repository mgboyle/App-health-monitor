"""
Database migration script to add mTLS support fields to the Endpoint model

This script adds the following columns to the endpoints table:
- mtls_enabled: Boolean flag to enable mTLS
- mtls_cert_source: Source of the certificate ('file' or 'keyvault')
- mtls_cert_path: Path to local certificate file
- mtls_key_path: Path to local private key file
- mtls_keyvault_cert_name: Name of certificate in Azure Key Vault

Usage:
    python migrate_mtls.py
"""

import sqlite3
import os
import sys

def migrate_database(db_path='health_monitor.db'):
    """
    Add mTLS fields to the endpoints table
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("No migration needed - new database will be created with all fields.")
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if migration is needed
    cursor.execute("PRAGMA table_info(endpoints)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'mtls_enabled' in columns:
        print("Migration already applied. No changes needed.")
        conn.close()
        return
    
    print("Adding mTLS support columns...")
    
    try:
        # Add new columns
        cursor.execute("ALTER TABLE endpoints ADD COLUMN mtls_enabled BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE endpoints ADD COLUMN mtls_cert_source VARCHAR(20)")
        cursor.execute("ALTER TABLE endpoints ADD COLUMN mtls_cert_path VARCHAR(500)")
        cursor.execute("ALTER TABLE endpoints ADD COLUMN mtls_key_path VARCHAR(500)")
        cursor.execute("ALTER TABLE endpoints ADD COLUMN mtls_keyvault_cert_name VARCHAR(200)")
        
        conn.commit()
        print("✓ Migration completed successfully!")
        print("\nAdded columns:")
        print("  - mtls_enabled (BOOLEAN)")
        print("  - mtls_cert_source (VARCHAR)")
        print("  - mtls_cert_path (VARCHAR)")
        print("  - mtls_key_path (VARCHAR)")
        print("  - mtls_keyvault_cert_name (VARCHAR)")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database to add mTLS support')
    parser.add_argument('--db', default='health_monitor.db', 
                       help='Path to database file (default: health_monitor.db)')
    
    args = parser.parse_args()
    
    migrate_database(args.db)
