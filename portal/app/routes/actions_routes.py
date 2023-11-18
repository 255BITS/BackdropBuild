from flask import Blueprint, render_template, redirect, url_for, request, g
from app.services.actions_service import ActionsService
from app.services.auth_service import assert_logged_in
from shared.couch import db
import re

actions_bp = Blueprint('actions', __name__)

def actions_service():
    return ActionsService(g.current_user)

@actions_bp.before_request
def before_request():
    assert_logged_in()

@actions_bp.route('/actions')
def index():
    actions_list = actions_service().list() #TODO pagination, order
    return render_template('actions_index.html', actions_list=actions_list)

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
    actions, apis, auths = actions_service().get_details(id)
    return render_template('actions_show.html', actions=actions, apis=apis, auths=auths)

@actions_bp.route('/actions/<id>/edit')
def edit(id):
    return redirect(url_for('actions.show', id=id))

@actions_bp.post('/actions/<id>/update')
def update(id):
    name = request.form.get('name')
    actions_service().update(id, {"name": name})
    return redirect(url_for('actions.show', id=id))

@actions_bp.get('/actions/<id>/api_link')
def api_link(id):
    apis = actions_service().get_apis()
    actions = db.get(id)
    return render_template('actions_api_link.html', apis=apis, actions=actions)

@actions_bp.post('/actions/<id>/api_link/<api_id>')
def api_link_add(id, api_id):
    form_data = request.form
    action_name = form_data["action_name"]
    params = []
    indexed_params = {}

    # Organize the data by index
    pattern = re.compile(r'params\[(\d+)\]\[(\w+)\]')
    for key in form_data:
        if key.startswith('params'):
            index, param_key = pattern.match(key).groups()
            if index not in indexed_params:
                indexed_params[index] = {}
            indexed_params[index][param_key] = form_data[key]

    # Convert each indexed group into a dictionary
    for index in indexed_params:
        params.append(indexed_params[index])

    actions_service().add_api_link(id, api_id, action_name, params)
    return redirect(url_for("actions.show", id=id))

@actions_bp.route('/actions/<id>/api_link/<api_id>/new')
def api_link_new(id, api_id):
    api = db.get(api_id)
    actions = db.get(id)
    return render_template('actions_api_link_new.html', api=api, actions=actions)

@actions_bp.route('/api/options')
def api_link_options():
    i = request.args.get("index")
    type = request.args.get(f'params[{i}][type]')
    return render_template('actions_api_link_options.html', type=type, i=i)
