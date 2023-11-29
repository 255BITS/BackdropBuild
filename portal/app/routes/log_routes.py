from flask import Blueprint, render_template
from shared.couch import logs_db

log_bp = Blueprint('logs', __name__)

@log_bp.get('/logs/<id>')
def show(id):
    log = logs_db.get(id)
    return render_template('log_show.html', log=log)
