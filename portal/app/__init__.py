from flask import Flask
import os
from app.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET", 'development')
    app.register_blueprint(auth_bp)
    return app
