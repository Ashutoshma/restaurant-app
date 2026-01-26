# Phase 2: Authentication & Security - Detailed Plan

## Overview
Implement user authentication with secure password hashing, session management, and CSRF protection.

**Duration:** 2-3 days  
**Target Commits:** 5-6  
**Target Tests:** 8-10  
**Status:** Ready to start

---

## Phase 2 Goals

### 1. User Registration
- [ ] Create registration form with validation
- [ ] Validate email format and uniqueness
- [ ] Hash passwords with bcrypt
- [ ] Store user in PostgreSQL
- [ ] Test form validation

### 2. User Login
- [ ] Create login form
- [ ] Authenticate user credentials
- [ ] Compare bcrypt hashes
- [ ] Create session with Flask-Login
- [ ] Test login process

### 3. Session Management
- [ ] Implement Flask-Login integration
- [ ] Add session timeout (1 hour)
- [ ] Implement user_loader callback
- [ ] Add logout functionality
- [ ] Test session management

### 4. Security Features
- [ ] CSRF protection on all forms
- [ ] Secure cookies (HTTPOnly, Secure flags)
- [ ] Password validation rules
- [ ] Test security features

### 5. HTML Templates
- [ ] Base template with navigation
- [ ] Login page
- [ ] Registration page
- [ ] Homepage (requires login)

---

## File Structure for Phase 2

```
app/
├── __init__.py           (Already exists)
├── auth/
│   ├── __init__.py       (New)
│   ├── forms.py          (New) - Registration and login forms
│   ├── models.py         (New) - User model methods (login_required)
│   └── utils.py          (New) - Hash/verify password helpers
│
├── routes/
│   ├── __init__.py       (New)
│   └── auth.py           (New) - Login/registration/logout routes
│
├── templates/
│   ├── base.html         (New) - Base template with nav
│   ├── register.html     (New) - Registration form
│   ├── login.html        (New) - Login form
│   └── home.html         (New) - Home page (login required)
│
└── static/
    └── css/
        └── style.css     (New) - Basic styling

tests/
├── test_database.py      (Already exists)
└── test_auth.py          (New) - Authentication tests
```

---

## Step-by-Step Implementation

### Step 2.1: Create Auth Forms

**File: `app/auth/forms.py`**

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import re

class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_password(self, field):
        """Validate password strength"""
        password = field.data
        # Must have uppercase, lowercase, and number
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit')


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```

**What to do:**
1. Create `app/auth/` directory with `__init__.py` file
2. Create the forms.py file with code above
3. Explain form validation in a comment

---

### Step 2.2: Create Password Utilities

**File: `app/auth/utils.py`**

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good security
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

**What to do:**
1. Create utils.py file
2. Implement hash_password function
3. Implement verify_password function
4. Add comments explaining bcrypt

---

### Step 2.3: Create Auth Routes

**File: `app/routes/auth.py`**

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database.postgres import db
from database.models import User
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.utils import hash_password, verify_password

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        session = db.get_session()
        existing_user = session.query(User).filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=hash_password(form.password.data)
        )
        
        session.add(user)
        session.commit()
        session.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        session = db.get_session()
        user = session.query(User).filter_by(email=form.email.data).first()
        
        if user and verify_password(form.password.data, user.password_hash):
            login_user(user)
            session.close()
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
        
        session.close()
    
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))
```

**What to do:**
1. Create `app/routes/` directory with `__init__.py`
2. Create auth.py file with routes above
3. Implement register route with form validation
4. Implement login route with password verification
5. Implement logout route

---

### Step 2.4: Create HTML Templates

**File: `app/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Restaurant Ordering App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Restaurant Orders</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <span class="navbar-text me-3">Hello, {{ current_user.username }}!</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**What to do:**
1. Create `app/templates/` directory
2. Create base.html with Bootstrap navbar
3. Add flash message display
4. Add navigation logic for authenticated users

---

### Step 2.5: Create Tests

**File: `tests/test_auth.py`**

```python
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.postgres import PostgresDB
from database.models import User
from app.auth.utils import hash_password, verify_password

class TestPasswordHashing:
    """Test bcrypt password functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Hash should not be plaintext
        assert hashed != password
        # Hash should be string
        assert isinstance(hashed, str)
    
    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword123", hashed) is False


class TestAuthRoutes:
    """Test authentication routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app('testing')
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        # Setup database
        from database.postgres import PostgresDB
        db = PostgresDB('sqlite:///:memory:')
        db.create_tables()
        
        with app.test_client() as client:
            yield client
    
    def test_register_page(self, client):
        """Test registration page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
    
    def test_login_user(self, client):
        """Test user login"""
        # First register user
        client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123'
        })
        
        # Then login
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login successful' in response.data
```

**What to do:**
1. Create tests/test_auth.py file
2. Test password hashing functions
3. Test registration page
4. Test login page
5. Test registration process
6. Test login process

---

## Commit Strategy for Phase 2

After each step, commit:

```bash
# Step 2.1
git add app/auth/forms.py
git commit -m "feat: Add registration and login forms with validation"

# Step 2.2
git add app/auth/utils.py
git commit -m "feat: Add bcrypt password hashing utilities"

# Step 2.3
git add app/routes/auth.py
git commit -m "feat: Add authentication routes (register, login, logout)"

# Step 2.4
git add app/templates/
git commit -m "feat: Add HTML templates for auth pages"

# Step 2.5
git add tests/test_auth.py
git commit -m "test: Add authentication unit tests"

# Update Flask app
git add app.py
git commit -m "config: Integrate authentication into Flask app"
```

---

## Testing After Each Step

```bash
# Run all tests
python -m pytest tests/ -v

# Run only auth tests
python -m pytest tests/test_auth.py -v

# Check test coverage
python -m pytest tests/ --cov=app
```

---

## What You'll Learn in Phase 2

- Form validation with Flask-WTF
- CSRF protection (automatic with WTF)
- Password hashing best practices
- Session management
- User authentication flow
- HTML template inheritance
- User-required decorators

---

## Common Issues & Solutions

**Issue:** "No module named 'flask_login'"
**Solution:** `pip install Flask-Login==0.6.0`

**Issue:** "Form validation failing"
**Solution:** Make sure WTF_CSRF_ENABLED = True in config (already set)

**Issue:** "CSRF token missing"
**Solution:** Add {{ form.csrf_token }} in HTML form

---

## Ready When...

- [ ] All 7 database tests still passing
- [ ] Auth routes created and tested
- [ ] Registration form validates input
- [ ] Login hashes and verifies passwords
- [ ] CSRF protection enabled
- [ ] Session timeout configured
- [ ] Logout clears session
- [ ] 5-6 new commits made
- [ ] 8-10 auth tests passing

Then move to **Phase 3: Core Features (CRUD Operations)**
