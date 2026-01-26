"""Main Flask application factory"""
import os
from flask import Flask
from config import config

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
