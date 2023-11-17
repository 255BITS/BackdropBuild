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
    actions_list = actions_service().list() #TODO pagination, order
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
    apis = actions_service().get_link_apis()
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
