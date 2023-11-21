from flask import Flask, render_template, redirect, request, jsonify, url_for, flash, g
from shared.couch import db
from app.services.api_service import parse_api_object
from app.services.auth_service import assert_owner, assert_logged_in

from flask import Blueprint
api_bp = Blueprint('apis', __name__)

@api_bp.route('/discover-apis')
def apis_discover():
    apis = db.query_view('apis', 'public')
    return render_template('api_discover.html', apis=apis)

@api_bp.route('/apis')
def apis_my():
    assert_logged_in()
    apis = db.query_view('apis', 'by_user', key=g.current_user.id)
    return render_template('api_list.html', apis=apis)

@api_bp.route('/apis/new')
def apis_new():
    assert_logged_in()
    default_api={"paths":[{"params":[["credential", "API_KEY"],["string", "query"]]}]}
    return render_template('api_new.html', errors={}, api=default_api)

@api_bp.route('/apis/create', methods=["POST"])
def apis_create():
    assert_logged_in()
    # Check if request content type is form data
    if request.content_type != 'application/x-www-form-urlencoded':
        return jsonify({"error": "Content type must be application/x-www-form-urlencoded"}), 400

    errors, api_object = parse_api_object(request)
    api_object["user_id"] = g.current_user.id
    # If there are errors, render the api_new template with errors
    if errors:
        for k, v in errors.items():
            flash(v, 'error')
        return render_template('api_new.html', errors=errors, api=api_object)
    new_api_object = db.save(api_object)

    # Add your logic here to handle the attributes and 'params' list
    return redirect('/apis/'+new_api_object["_id"])

@api_bp.route('/apis/<id>', methods=["GET"])
def apis_show(id):
    assert_logged_in()
    api = db.get(id)
    return render_template('api_show.html', api=api, current_user=g.current_user)

@api_bp.route('/apis/<id>/edit', methods=["GET"])
def apis_edit(id):
    api = db.get(id)
    assert_owner(api)
    return render_template('api_new.html', errors={}, api=api)

@api_bp.route('/apis/<id>/update', methods=["POST"])
def apis_update(id):
    api = db.get(id)
    assert_owner(api)
    errors, api_object = parse_api_object(request)
    if errors:
        for k, v in errors.items():
            flash(v, 'error')
        return render_template('api_new.html', errors=errors, api=api_object)
    for k, v in api_object.items():
        api[k]=v

    saved = db.save(api)
    return render_template('api_show.html', errors={}, api=api_object)

@api_bp.route('/apis/<id>/publish', methods=["POST"])
def apis_publish(id):
    api = db.get(id)
    assert_owner(api)
    api["visibility"]="public"
    db.save(api)
    return render_template('api_show.html', api=api)

@api_bp.route('/apis/<id>/unpublish', methods=["POST"])
def apis_unpublish(id):
    api = db.get(id)
    assert_owner(api)
    api = db.get(id)
    api["visibility"]="private"
    db.save(api)
    return render_template('api_show.html', api=api)

@api_bp.route('/apis/<id>/usage')
def apis_show_usage(id):
    api = db.get(id)
    assert_owner(api)
    return render_template('api_usage.html', api=api)
