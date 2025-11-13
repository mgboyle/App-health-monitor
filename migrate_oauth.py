"""
Database migration script to add OAuth 2.0 fields to endpoints table
"""
import sys
from app.app import create_app
from app.models import db

def migrate_oauth_fields():
    """Add OAuth 2.0 fields to existing endpoints table"""
    app = create_app()
    
    with app.app_context():
        # Check if we need to run migration
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('endpoints')]
        
        if 'oauth_flow' in columns:
            print("OAuth fields already exist in the database. No migration needed.")
            return
        
        print("Adding OAuth 2.0 fields to endpoints table...")
        
        # Add OAuth fields to the table
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_flow VARCHAR(50)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_client_id VARCHAR(500)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_client_secret VARCHAR(500)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_token_url VARCHAR(500)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_authorization_url VARCHAR(500)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_scope VARCHAR(500)"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_access_token TEXT"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_refresh_token TEXT"))
            conn.execute(db.text("ALTER TABLE endpoints ADD COLUMN oauth_token_expires_at DATETIME"))
            conn.commit()
        
        print("OAuth 2.0 fields added successfully!")
        print("Migration completed.")

if __name__ == '__main__':
    migrate_oauth_fields()
