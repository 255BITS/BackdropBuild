from flask import Blueprint, render_template
from shared.couch import db

public_bp = Blueprint('public', __name__)

@public_bp.get('/')
def home():
    return render_template('landing.html', count_apis=db.count_apis())
