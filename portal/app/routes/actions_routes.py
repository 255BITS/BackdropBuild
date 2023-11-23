from flask import Blueprint, render_template, redirect, url_for, request, g, make_response, flash
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
    templates = [
        {'name': 'DEX Trade', 'description': 'Trade on your hot wallet', 'icon': 'fas fa-chart-line'},
        {'name': 'Send Emails', 'description': 'Send an email', 'icon': 'fas fa-envelope'},
        {'name': 'Control Robot', 'description': 'Beep boop bop', 'icon': 'fas fa-cog'}
        # ... Add as many templates as you need
    ]

    return render_template('actions_new.html', templates=templates)

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
    actions, apis, auths = actions_service().get_details(id)
    return render_template('actions_edit.html', actions=actions, apis=apis)

@actions_bp.route('/actions/<id>/edit_redirect')
def edit_redirect(id):
    response = make_response("", 200)
    response.headers['HX-Redirect'] = url_for("actions.edit", id=id)
    return response

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

@actions_bp.post('/actions/<id>/api_link')
def post_api_link(id):
    apis = actions_service().get_apis()
    actions = db.get(id)
    form_data = request.form
    api_id = form_data["api"]
    api = db.get(api_id)
    print("FOUND api", api)
    #TODO 404
    for api_link in actions["api_links"]:
        if api_id == api_link["api_id"]:
            flash("That API has already been added.", "info")
            return redirect(url_for("actions.show", id=id))
    api_links = { "api_id": api_id, "paths": [] }
    for path in api["paths"]:
        api_link_path = dict(path)
        api_link_path["params"] = []
        print("--params", path)
        for param in path["params"]:
            default_source = "gpt"
            if param["type"] == "credentials":
                default_source = "credentials"
            default_value = ""
            api_link_param = { "name": param["name"], "source": default_source, "value": default_value }
            api_link_path["params"].append(api_link_param)

        api_links["paths"].append(api_link_path)

    actions["api_links"].append(api_links) 
    db.save(actions)
    return redirect(url_for("actions.show", id=id))

@actions_bp.delete('/actions/<id>/api_link/<api_link_id>')
def api_link_delete(id, api_link_id):
    actions = db.get(id)
    del actions["api_links"][int(api_link_id)]
    db.save(actions)
    return ""

@actions_bp.post('/actions/<id>/api_link/<api_id>')
def api_link_add(id, api_id):
    form_data = request.form
    action_name = form_data["action_name"] #TODO operation_id
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
