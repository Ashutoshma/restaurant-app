"""Main Flask application factory"""
import os
from flask import Flask, Blueprint, render_template
from flask_login import LoginManager, login_required
from config import config
from database.postgres import SessionLocal, init_db
from database.models import User

def create_app(config_name=None):
    """
    Application factory pattern.
    Creates and configures Flask app with database and authentication.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Explicitly set template and static folders
    template_folder = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    static_folder = os.path.join(os.path.dirname(__file__), 'app', 'static')
    
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        session = SessionLocal()
        try:
            user = session.query(User).get(int(user_id))
            return user
        finally:
            session.close()
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Create main routes blueprint
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    @login_required
    def home():
        return render_template('home.html')
    
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
