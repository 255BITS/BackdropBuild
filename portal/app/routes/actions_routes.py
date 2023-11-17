from flask import Blueprint, render_template, redirect, url_for, request, g
from app.services.actions_service import ActionsService
from app.services.auth_service import assert_logged_in
from shared.couch import db

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
    actions = actions_service().get(id)
    return render_template('actions_show.html', actions=actions)

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
    return render_template('actions_api_link.html', apis=apis, id=id)

@actions_bp.post('/actions/<id>/api_link/<api_id>')
def api_link_add(id, api_id):
    api_id = request.form.get('api_id')
    actions_service().add_api_link(id, api_id, request.form.to_dict())
    return redirect(url_for("actions.show", id=id))

@actions_bp.route('/actions/<id>/api_link/<api_id>/new')
def api_link_new(id, api_id):
    api = db.get(api_id)
    actions = actions_service().get(id)
    return render_template('actions_api_link_new.html', api=api, actions=actions)

@actions_bp.route('/api/options')
def api_link_options():
    return render_template('actions_api_link_options.html')
