from flask import Blueprint, render_template, redirect, url_for, request, g, make_response, flash
from app.services.actions_service import ActionsService
from app.services.auth_service import assert_logged_in, assert_owner
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
    page = int(request.args.get("page", 1))
    limit = 10
    actions_list, total_count = actions_service().list(limit, (page-1)*limit) #TODO order
    ids = [a['_id'] for a in actions_list]
    usage_count = db.count_logs_by_actions(ids)
    gpts_count = db.count_gpt_ids_by_actions(ids)
    sparklines = actions_service().get_sparklines(ids)
    return render_template('actions_index.html', actions_list=actions_list, usage_count=usage_count, gpts_count=gpts_count, sparklines=sparklines, page=page, total_count=total_count, limit=limit)

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
    doc = db.get(id)
    if doc is not None:
        assert_owner(doc)
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
    assert_owner(actions)
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
    try:
        actions_service().update(actions)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('actions.edit', id=id))

    return redirect(url_for('actions.show', id=id))

@actions_bp.get('/actions/<id>/api_link')
def api_link(id):
    page = int(request.args.get("page", 1))
    limit = 10
    apis, total_count = actions_service().get_apis(limit, (page-1)*limit)
    actions = db.get(id)
    return render_template('actions_api_link.html', apis=apis, actions=actions, page=page, limit=limit, total_count=total_count)

@actions_bp.post('/actions/<id>/api_link')
def post_api_link(id):
    actions = db.get(id)
    form_data = request.form
    api_id = form_data["api"]
    api = db.get(api_id)
    #TODO 404
    api_link = actions_service().create_api_link(actions["api_links"], api, api_id)
    actions["api_links"].append(api_link) 
    db.save(actions)
    return redirect(url_for("actions.edit", id=id))

@actions_bp.delete('/actions/<id>/api_link/<api_link_id>')
def api_link_delete(id, api_link_id):
    actions = db.get(id)
    assert_owner(actions)
    api_link_index = None
    for i, api_link in enumerate(actions["api_links"]):
        if "id" not in api_link and api_link_id == "0" or api_link["id"] == api_link_id:
            api_link_index = i

    if api_link_index is None:
        flash("API link not found.", "warning")
    else:
        del actions["api_links"][int(api_link_index)]
        db.save(actions)
    response = make_response("", 200)
    response.headers['HX-Redirect'] = url_for("actions.edit", id=id)
    return response

@actions_bp.route('/actions/<id>/usage')
def actions_usage(id):
    page = int(request.args.get("page", 1))
    actions = db.get(id)
    limit = 10
    logs, total_count = actions_service().get_logs(actions, limit, limit*(page-1))
    return render_template('actions_usage.html', id=id, actions=actions, logs=logs, page=page, limit=limit, total_count=total_count)

