"""Main Flask application"""
import sys
import traceback

error_message = None

try:
    from app_factory import create_app
    app = create_app()
except Exception as e:
    error_message = str(e)
    print(f"ERROR creating Flask app: {error_message}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    # Create a minimal error app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Error initializing app: {error_message}", 500

if __name__ == '__main__':
    app.run(debug=True)
