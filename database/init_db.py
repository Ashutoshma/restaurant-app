"""Initialize both PostgreSQL and Firestore databases"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Initialize all databases"""
    print("=" * 50)
    print("Initializing Restaurant Ordering App Databases")
    print("=" * 50)
    
    # Initialize PostgreSQL
    print("\n[1/2] Initializing PostgreSQL...")
    try:
        from database.postgres import db as postgres_db
        postgres_db.create_tables()
        postgres_db.seed_data()
        print("✓ PostgreSQL initialized successfully")
    except Exception as e:
        print(f"✗ PostgreSQL initialization failed: {e}")
        sys.exit(1)
    
    # Initialize Firestore
    print("\n[2/2] Initializing Firestore...")
    try:
        from database.firestore import firestore_db
        firestore_db.seed_data()
        print("✓ Firestore initialized successfully")
    except Exception as e:
        print(f"✗ Firestore initialization failed: {e}")
        print("  Ensure GOOGLE_APPLICATION_CREDENTIALS is set")
    
    print("\n" + "=" * 50)
    print("Database initialization complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()
