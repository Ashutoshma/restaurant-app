"""Pytest configuration and fixtures"""
import sys
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_factory import create_app
from database.postgres import PostgresDB
from database.models import User, Restaurant
from app.auth.utils import hash_password
from flask_login import login_user


# Global database instance for all tests
_test_db = None


def get_test_db():
    """Get or create the global test database"""
    global _test_db
    if _test_db is None:
        _test_db = PostgresDB('sqlite:///:memory:')
        _test_db.create_tables()
    return _test_db


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application for the entire session"""
    app = create_app('testing')
    
    # Initialize test database for the session
    db = get_test_db()
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client that persists cookies across requests"""
    return app.test_client(use_cookies=True)


@pytest.fixture
def runner(app):
    """Create a test CLI runner for each test"""
    return app.test_cli_runner()


@pytest.fixture
def init_db():
    """Get the initialized test database"""
    return get_test_db()


@pytest.fixture
def auth_user(client, app, init_db):
    """Create and log in a test user"""
    session = init_db.get_session()
    
    try:
        # Check if user already exists
        existing = session.query(User).filter_by(email='test@example.com').first()
        if existing:
            user_id = existing.id
        else:
            # Create test user
            user = User(
                email='test@example.com',
                username='testuser',
                password_hash=hash_password('testpass123'),
                first_name='Test',
                last_name='User'
            )
            session.add(user)
            session.commit()
            user_id = user.id
        
        session.close()
        
        # Log in using Flask-Login directly
        session = init_db.get_session()
        user = session.query(User).filter_by(id=user_id).first()
        
        # Push app context and log in
        with app.test_request_context():
            login_user(user)
        
        session.close()
        
        # Also do a POST login to set the session cookie
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=False)
        
        # Return user object
        session = init_db.get_session()
        user = session.query(User).filter_by(id=user_id).first()
        session.close()
        
        return user
    
    except Exception as e:
        session.rollback()
        session.close()
        raise


@pytest.fixture
def sample_restaurants(init_db):
    """Create sample restaurant data"""
    session = init_db.get_session()
    
    try:
        # Check if restaurants already exist
        existing = session.query(Restaurant).first()
        if existing:
            restaurants = session.query(Restaurant).all()
            session.close()
            return restaurants
        
        restaurants_data = [
            Restaurant(
                name='Pizza Palace',
                description='Authentic Italian pizza',
                city='New York',
                address='123 Main St',
                phone='555-0001'
            ),
            Restaurant(
                name='Burger Haven',
                description='Gourmet burgers and fries',
                city='New York',
                address='456 Oak Ave',
                phone='555-0002'
            ),
            Restaurant(
                name='Sushi Paradise',
                description='Fresh sushi and Japanese cuisine',
                city='Los Angeles',
                address='789 Elm St',
                phone='555-0003'
            )
        ]
        
        for restaurant in restaurants_data:
            session.add(restaurant)
        session.commit()
        
        restaurants = session.query(Restaurant).all()
        session.close()
        return restaurants
    
    except Exception as e:
        session.rollback()
        session.close()
        raise
