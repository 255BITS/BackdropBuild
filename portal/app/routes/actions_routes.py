from flask import Blueprint, render_template, redirect, url_for, request, g
from app.services.actions_service import ActionsService
from app.services.auth_service import assert_logged_in

actions_bp = Blueprint('actions', __name__)

def actions_service():
    return ActionsService(g.current_user)

@actions_bp.before_request
def before_request():
    assert_logged_in()

@actions_bp.route('/dashboard')
def dashboard():
    actions_list = [
        {
            "_id": "abcd",
            "name": "Calculator",
            "apis": 2,
            "gpts": 4,
            "uses": 27,
            "last_updated": "3 hours ago",
            "sparkline_data": "0,48 60,24 120,36 180,40 240,24 300,0"
        },
        {
            "_id": "efgh",
            "name": "PDF tools",
            "apis": 0,
            "gpts": 0,
            "uses": 0,
            "last_updated": "6 days ago",
            "sparkline_data": "0,48 60,48 120,48 180,48 240,48 300,48"
        },
    ]
    actions_list += actions_service().list() #TODO pagination, order
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
    actions = actions_service().get(id)
    return render_template('actions_show.html', actions=actions)

@actions_bp.route('/actions/<id>/edit')
def edit(id):
    return redirect(url_for('actions.show', id=id))

@actions_bp.route('/actions/<id>/link_api')
def actions_link_api(id):
    apis = [
        {
            "value": "api1",
            "description": "Get last message from queue",
            "author": "apiauthor1",
            "name": "AWS SNS",
            "id": "1",
            "method": "GET"
        },
        {
            "value": "api2",
            "description": "POST message to queue",
            "name": "AWS SNS",
            "author": "apiauthor1",
            "id": "2",
            "method": "POST"
        }
    ]
    return render_template('actions_link_api.html', apis=apis, id=id)

@actions_bp.route('/actions/<id>/link_api/<api_id>/new')
def actions_link_api_new(id, api_id):
    api = {
            "default_name": "apiCall",
            "fields": [
                {
                    "api key": "credential",
                    "bucket": "string",
                    "message": "string"
                 }
            ],
    }
    return render_template('actions_link_api_new.html', api=api)

@actions_bp.route('/api/options')
def actions_link_api_options():
    return render_template('actions_link_api_options.html')
