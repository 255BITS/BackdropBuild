from flask import Blueprint, render_template, redirect, url_for, request, g
from app.services.actions_service import ActionsService
from app.services.auth_service import assert_logged_in

actions_bp = Blueprint('actions', __name__)

def actions_service():
    return ActionsService(g.current_user)

@actions_bp.route('/dashboard')
def dashboard():
    assert_logged_in()
    actions_list = [
        {
            "id": "abcd",
            "name": "Calculator",
            "apis": 2,
            "gpts": 4,
            "uses": 27,
            "last_updated": "3 hours ago",
            "sparkline_data": "0,48 60,24 120,36 180,40 240,24 300,0"
        },
        {
            "id": "efgh",
            "name": "PDF tools",
            "apis": 0,
            "gpts": 0,
            "uses": 0,
            "last_updated": "6 days ago",
            "sparkline_data": "0,48 60,48 120,48 180,48 240,48 300,48"
        },
    ]
    return render_template('dashboard.html', actions_list=actions_list)

@actions_bp.route('/actions/new')
def new():
    return render_template('actions_new.html')

@actions_bp.post("/actions")
def create():
    name = request.form.get('name')
    actions = actions_service().create(name)
    return redirect(url_for("actions.edit", id=actions['_id']))

@actions_bp.route('/actions/<id>')
def show(id):
    return render_template('actions_show.html', actions=["Action 1", "Action 2"], auths=[{"type": "Basic", "value":"b#gv7IiKP#bj9lXO", "value_encoded": "**************"}])

@actions_bp.route('/actions/<id>/edit')
def edit(id):
    return render_template('actions_show.html', actions=[])
