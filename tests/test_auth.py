"""Authentication tests - registration, login, password utilities"""
import pytest
import sys
import os
import importlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import create_app from app module, avoiding naming conflict with app/ directory
app_module = importlib.import_module('app', package=None)
# Get create_app by loading the root app.py directly
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("root_app", os.path.join(root_path, "app.py"))
root_app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_app_module)
create_app = root_app_module.create_app

from database.postgres import SessionLocal, init_db
from database.models import User
from app.auth.utils import hash_password, verify_password


@pytest.fixture
def app():
    """Create app with test configuration"""
    app = create_app('testing')
    
    # Create tables before tests
    with app.app_context():
        init_db()
    
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def test_user():
    """Create test user data"""
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPassword123',
        'confirm_password': 'TestPassword123'
    }


class TestPasswordUtilities:
    """Test password hashing and verification"""
    
    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a valid bcrypt hash"""
        password = 'TestPassword123'
        hashed = hash_password(password)
        
        # Hash should be a string
        assert isinstance(hashed, str)
        # Hash should not be the original password
        assert hashed != password
        # Hash should be long (bcrypt hashes are ~60 characters)
        assert len(hashed) >= 50
    
    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password"""
        password = 'TestPassword123'
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password"""
        password = 'TestPassword123'
        wrong_password = 'WrongPassword123'
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_invalid_hash(self):
        """Test that verify_password handles invalid hash gracefully"""
        password = 'TestPassword123'
        invalid_hash = 'not_a_valid_hash'
        
        # Should not raise exception, just return False
        assert verify_password(password, invalid_hash) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords create different hashes"""
        password1 = 'TestPassword123'
        password2 = 'DifferentPassword456'
        
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        
        assert hash1 != hash2


class TestRegistration:
    """Test user registration"""
    
    def test_registration_page_loads(self, client):
        """Test that registration page loads successfully"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data
        assert b'Email' in response.data
        assert b'Username' in response.data
        assert b'Password' in response.data
    
    def test_register_valid_user(self, client, test_user):
        """Test successful user registration"""
        response = client.post('/auth/register', data=test_user, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
        
        # Verify user was created in database
        session = SessionLocal()
        user = session.query(User).filter_by(email=test_user['email']).first()
        session.close()
        
        assert user is not None
        assert user.username == test_user['username']
        assert user.email == test_user['email']
    
    def test_register_missing_email(self, client):
        """Test registration without email fails"""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'Email is required' in response.data
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails"""
        data = {
            'email': 'not_an_email',
            'username': 'testuser',
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'valid email' in response.data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails"""
        # Create first user
        client.post('/auth/register', data=test_user)
        
        # Try to register with same email
        response = client.post('/auth/register', data=test_user)
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username fails"""
        # Create first user
        client.post('/auth/register', data=test_user)
        
        # Try to register with same username but different email
        different_email_user = test_user.copy()
        different_email_user['email'] = 'different@example.com'
        response = client.post('/auth/register', data=different_email_user)
        assert response.status_code == 200
        assert b'Username already taken' in response.data
    
    def test_register_short_username(self, client):
        """Test registration with username too short fails"""
        data = {
            'email': 'test@example.com',
            'username': 'ab',  # Too short
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'between 3 and 20 characters' in response.data
    
    def test_register_invalid_username_characters(self, client):
        """Test registration with invalid username characters fails"""
        data = {
            'email': 'test@example.com',
            'username': 'test-user',  # Hyphens not allowed
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'letters, numbers, and underscores' in response.data
    
    def test_register_short_password(self, client):
        """Test registration with password too short fails"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Short1',  # Less than 8 characters
            'confirm_password': 'Short1'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'at least 8 characters' in response.data
    
    def test_register_passwords_dont_match(self, client):
        """Test registration with non-matching passwords fails"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPassword123',
            'confirm_password': 'DifferentPassword123'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 200
        assert b'Passwords must match' in response.data


class TestLogin:
    """Test user login"""
    
    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'Email' in response.data
        assert b'Password' in response.data
    
    def test_login_valid_credentials(self, client, test_user):
        """Test successful login with valid credentials"""
        # First register a user
        client.post('/auth/register', data=test_user)
        
        # Then login
        response = client.post('/auth/login', data={
            'email': test_user['email'],
            'password': test_user['password']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back, testuser' in response.data
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email fails"""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'TestPassword123'
        })
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with correct email but wrong password fails"""
        # Register a user
        client.post('/auth/register', data=test_user)
        
        # Try to login with wrong password
        response = client.post('/auth/login', data={
            'email': test_user['email'],
            'password': 'WrongPassword123'
        })
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_missing_email(self, client):
        """Test login without email fails"""
        response = client.post('/auth/login', data={
            'password': 'TestPassword123'
        })
        assert response.status_code == 200
        assert b'Email is required' in response.data
    
    def test_login_missing_password(self, client):
        """Test login without password fails"""
        response = client.post('/auth/login', data={
            'email': 'test@example.com'
        })
        assert response.status_code == 200
        assert b'Password is required' in response.data


class TestLogout:
    """Test user logout"""
    
    def test_logout_clears_session(self, client, test_user):
        """Test that logout clears user session"""
        # Register and login
        client.post('/auth/register', data=test_user)
        client.post('/auth/login', data={
            'email': test_user['email'],
            'password': test_user['password']
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out successfully' in response.data
    
    def test_logout_redirects_to_login(self, client, test_user):
        """Test that logout redirects to login page"""
        # Register and login
        client.post('/auth/register', data=test_user)
        client.post('/auth/login', data={
            'email': test_user['email'],
            'password': test_user['password']
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        # Should see login page after redirect
        assert b'Login' in response.data


class TestProtectedRoutes:
    """Test that protected routes require login"""
    
    def test_home_requires_login(self, client):
        """Test that home page requires login"""
        response = client.get('/')
        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.location
    
    def test_home_accessible_when_logged_in(self, client, test_user):
        """Test that home page is accessible when logged in"""
        # Register and login
        client.post('/auth/register', data=test_user)
        client.post('/auth/login', data={
            'email': test_user['email'],
            'password': test_user['password']
        })
        
        # Now access home page
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to Restaurant Ordering' in response.data
