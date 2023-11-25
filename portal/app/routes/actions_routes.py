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
    ids = [a['_id'] for a in actions_list]
    usage_count = db.count_logs_by_actions(ids)
    gpts_count = db.count_gpt_ids_by_actions(ids)
    sparklines = actions_service().get_sparklines(ids)
    return render_template('actions_index.html', actions_list=actions_list, usage_count=usage_count, gpts_count=gpts_count, sparklines=sparklines)

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
    return redirect(url_for("actions.show", id=actions['_id']))

@actions_bp.get('/actions/<id>')
def show(id):
    actions, apis, auths = actions_service().get_details(id)
    return render_template('actions_show.html', actions=actions, apis=apis, auths=auths)

@actions_bp.delete('/actions/<id>')
def delete(id):
    #TODO assert owner
    #TODO assert valid uuid
    if db.get(id) is not None:
        db.delete(id)
        response = make_response("", 200)
        response.headers['HX-Redirect'] = url_for("actions.index")
        return response
    flash("You can't delete that.", "error")
    return redirect(url_for("actions.show", id=id))

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
    form_data = request.form
    name = form_data.get('name')

    actions = db.get(id)
    actions['name'] = name
    api_links = [dict(a) for a in actions["api_links"]]

    param_pattern = re.compile(r'api_links\[(\d+)\]\[paths\]\[(\d+)\]\[params\]\[(\d+)\]\[(\w+)\]')
    path_pattern = re.compile(r'api_links\[(\d+)\]\[paths\]\[(\d+)\]\[(\w+)\]')

    for key, value in form_data.items():
        param_match = param_pattern.match(key)
        path_match = path_pattern.match(key)

        if param_match:
            api_index, path_index, param_index, field = tuple(map(int, param_match.groups()[:-1])) + (param_match.groups()[-1],)
            # Ensure the structure is large enough for params
            while len(api_links) <= api_index:
                api_links.append({"paths": []})
            while len(api_links[api_index]["paths"]) <= path_index:
                api_links[api_index]["paths"].append({"params": []})
            while len(api_links[api_index]["paths"][path_index]["params"]) <= param_index:
                api_links[api_index]["paths"][path_index]["params"].append({})

            # Assign the param value
            api_links[api_index]["paths"][path_index]["params"][param_index][field] = value

        elif path_match:
            # Extract the api_index and path_index as integers, and field as string
            api_index, path_index = map(int, path_match.groups()[:-1])
            field = path_match.groups()[-1]

            # Ensure the structure is large enough for paths
            while len(api_links) <= api_index:
                api_links.append({"paths": []})
            while len(api_links[api_index]["paths"]) <= path_index:
                api_links[api_index]["paths"].append({})

            # Assign the path value
            api_links[api_index]["paths"][path_index][field] = value

    actions["api_links"] = api_links
    db.save(actions)

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
    #TODO 404
    for api_link in actions["api_links"]:
        if api_id == api_link["api_id"]:
            flash("That API has already been added.", "info")
            return redirect(url_for("actions.show", id=id))
    api_links = { "api_id": api_id, "paths": [] }
    for path in api["paths"]:
        api_link_path = { "path_id": path["path_id"], "operation_id": path["operation_id"], "params": [] }
        for param in path["params"]:
            default_source = "gpt"
            if param["type"] == "credential":
                default_source = "credential"
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

@actions_bp.route('/actions/<id>/usage')
def actions_usage(id):
    actions = db.get(id)
    logs = db.get_logs(id)
    return render_template('actions_usage.html', id=id, actions=actions, logs=logs)

