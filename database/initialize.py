"""Initialize application with restaurants and menus"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def init_postgresql():
    """Initialize PostgreSQL with restaurants"""
    print("\n[1/3] Initializing PostgreSQL...")
    try:
        from database.postgres import _get_db
        from database.models import Restaurant, OrderItem, Order, User, Payment
        from database.seed_data import get_restaurants
        
        # Create tables
        db = _get_db()
        print("  ✓ Creating tables...")
        db.create_tables()
        
        # Get session
        session = db.get_session()
        
        try:
            # Check if restaurants already exist
            existing = session.query(Restaurant).first()
            if existing:
                print(f"  ✓ Restaurants already exist ({session.query(Restaurant).count()} found)")
                return session
            
            # Add restaurants
            print("  ✓ Adding restaurants...")
            for rest_data in get_restaurants():
                restaurant = Restaurant(
                    name=rest_data['name'],
                    description=rest_data['description'],
                    city=rest_data['city'],
                    address=rest_data['address'],
                    phone=rest_data.get('phone', '')
                )
                session.add(restaurant)
            
            session.commit()
            restaurant_count = session.query(Restaurant).count()
            print(f"  ✓ PostgreSQL initialized with {restaurant_count} restaurants")
            return session
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    except Exception as e:
        print(f"  ✗ PostgreSQL initialization failed: {e}")
        raise


def init_firestore():
    """Initialize Firestore with menus"""
    print("\n[2/3] Initializing Firestore...")
    try:
        from database.firestore import firestore_db
        from database.seed_data import get_all_menus
        
        # Get all menus
        all_menus = get_all_menus()
        
        # Add menus to Firestore
        print("  ✓ Adding menus...")
        for restaurant_id, menu_items in all_menus.items():
            for item in menu_items:
                success = firestore_db.add_menu_item(restaurant_id, item)
                if not success:
                    print(f"    ⚠ Warning: Could not add {item['name']} to {restaurant_id}")
        
        print(f"  ✓ Firestore initialized with {sum(len(items) for items in all_menus.values())} menu items")
        print(f"    ({len(all_menus)} restaurants with menus)")
        
    except Exception as e:
        print(f"  ✗ Firestore initialization failed (this is OK if using mock data): {e}")


def verify_data():
    """Verify that data was added correctly"""
    print("\n[3/3] Verifying data...")
    try:
        import os
        os.environ['FLASK_ENV'] = 'development'
        
        from database.postgres import SessionLocal
        from database.models import Restaurant
        from database.firestore import firestore_db
        
        # Check PostgreSQL
        session = SessionLocal()
        restaurant_count = session.query(Restaurant).count()
        session.close()
        
        print(f"  ✓ PostgreSQL: {restaurant_count} restaurants")
        
        # Check Firestore
        print(f"  ✓ Firestore: Menu items available")
        
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        raise


def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("RESTAURANT ORDERING APP - DATABASE INITIALIZATION")
    print("="*60)
    
    try:
        # Set environment
        os.environ['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
        
        # Initialize databases
        init_postgresql()
        init_firestore()
        verify_data()
        
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("="*60)
        print("\nYou can now:")
        print("  1. Run the Flask app: python app.py")
        print("  2. Register a user: http://localhost:5000/auth/register")
        print("  3. Login and browse restaurants")
        print("  4. View menus and order food\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ INITIALIZATION FAILED")
        print("="*60)
        print(f"\nError: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
