import sys
from pathlib import Path
shared_path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(shared_path)

from flask import Flask
import os
from app.routes.auth_routes import auth_bp
from app.routes.api_routes import api_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET", 'development')
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    return app
