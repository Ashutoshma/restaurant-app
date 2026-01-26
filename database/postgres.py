"""PostgreSQL database connection and initialization"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, User, Restaurant, Order, OrderItem, Payment

class PostgresDB:
    def __init__(self, database_url=None):
        """Initialize PostgreSQL connection"""
        if database_url is None:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
        
        self.engine = create_engine(database_url, echo=os.environ.get('SQLALCHEMY_ECHO', False))
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables (for testing)"""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def seed_data(self):
        """Seed initial restaurant data"""
        session = self.get_session()
        
        try:
            # Check if data already exists
            existing = session.query(Restaurant).first()
            if existing:
                return
            
            # Create sample restaurants
            restaurants = [
                Restaurant(
                    name="Pizza Palace",
                    description="Authentic Italian pizza",
                    city="New York",
                    address="123 Main St"
                ),
                Restaurant(
                    name="Burger Haven",
                    description="Gourmet burgers and fries",
                    city="New York",
                    address="456 Oak Ave"
                ),
                Restaurant(
                    name="Sushi Paradise",
                    description="Fresh sushi and Japanese cuisine",
                    city="Los Angeles",
                    address="789 Elm St"
                )
            ]
            
            session.add_all(restaurants)
            session.commit()
            print("✓ Sample restaurants created")
        
        except Exception as e:
            print(f"✗ Error seeding data: {e}")
            session.rollback()
        
        finally:
            session.close()

# Global database instance
db = PostgresDB()

# Export SessionLocal for convenient import
SessionLocal = db.SessionLocal

def init_db(database_url=None):
    """Initialize database (create tables)"""
    if database_url:
        global db
        db = PostgresDB(database_url)
    db.create_tables()

if __name__ == '__main__':
    # For manual initialization
    db.create_tables()
    db.seed_data()
    print("Database initialized successfully!")
