"""Authentication routes - registration, login, logout"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database.postgres import SessionLocal
from database.models import User
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.utils import hash_password, verify_password

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration endpoint.
    GET: Display registration form
    POST: Process registration form submission
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user with hashed password
        session = SessionLocal()
        try:
            user = User(
                email=form.email.data,
                username=form.username.data,
                password_hash=hash_password(form.password.data)
            )
            session.add(user)
            session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
        finally:
            session.close()
    
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint.
    GET: Display login form
    POST: Process login form submission
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(email=form.email.data).first()
            
            if user and verify_password(form.password.data, user.password_hash):
                # Use Flask-Login to create session
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to next page or home
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.home'))
            else:
                flash('Invalid email or password. Please try again.', 'error')
        finally:
            session.close()
    
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """
    User logout endpoint.
    Clears user session and redirects to login page.
    """
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
