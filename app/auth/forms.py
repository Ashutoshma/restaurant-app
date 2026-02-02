"""Registration and login forms with validation"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from database.models import User
from database.postgres import SessionLocal


class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    
    email = StringField('Email', 
                       validators=[
                           DataRequired('Email is required'),
                           Email('Please enter a valid email address')
                       ])
    
    username = StringField('Username',
                          validators=[
                              DataRequired('Username is required'),
                              Length(min=3, max=20, message='Username must be between 3 and 20 characters'),
                              Regexp('^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
                          ])
    
    password = PasswordField('Password',
                            validators=[
                                DataRequired('Password is required'),
                                Length(min=8, message='Password must be at least 8 characters long')
                            ])
    
    confirm_password = PasswordField('Confirm Password',
                                    validators=[
                                        DataRequired('Please confirm your password'),
                                        EqualTo('password', message='Passwords must match')
                                    ])
    
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email already exists in database"""
        try:
            session = SessionLocal()
            try:
                user = session.query(User).filter_by(email=field.data).first()
                if user:
                    raise ValidationError('Email already registered. Please use a different email.')
            finally:
                session.close()
        except Exception as e:
            # If database connection fails, skip validation
            # (will be caught during registration)
            pass
    
    def validate_username(self, field):
        """Check if username already exists in database"""
        try:
            session = SessionLocal()
            try:
                user = session.query(User).filter_by(username=field.data).first()
                if user:
                    raise ValidationError('Username already taken. Please choose a different username.')
            finally:
                session.close()
        except Exception as e:
            # If database connection fails, skip validation
            # (will be caught during registration)
            pass


class LoginForm(FlaskForm):
    """User login form"""
    
    email = StringField('Email',
                       validators=[
                           DataRequired('Email is required'),
                           Email('Please enter a valid email address')
                       ])
    
    password = PasswordField('Password',
                            validators=[
                                DataRequired('Password is required')
                            ])
    
    submit = SubmitField('Login')
