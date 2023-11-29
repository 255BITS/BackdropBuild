import uuid
from flask import Flask, render_template, redirect, request, jsonify, url_for, flash, g, make_response
from shared.couch import db, logs_db
from app.services.api_service import parse_api_object, ApiService
from app.services.auth_service import assert_owner, assert_logged_in

from flask import Blueprint
api_bp = Blueprint('apis', __name__)

def api_service(api):
    return ApiService(api)

@api_bp.route('/discover-apis')
def apis_discover():
    apis = db.query_view('apis', 'public')
    ids = [a['_id'] for a in apis]

    api_links_count = db.count_api_links(ids)
    usage_count = logs_db.count_logs_by_api(ids)
    return render_template('api_discover.html', apis=apis, api_links_count=api_links_count, usage_count=usage_count)

@api_bp.route('/apis')
def apis_my():
    assert_logged_in()
    apis = db.query_view('apis', 'by_user', key=g.current_user.id)
    ids = [a['_id'] for a in apis]
    api_links_count = db.count_api_links(ids)
    usage_count = logs_db.count_logs_by_api(ids)
    apis_last_used = logs_db.get_apis_last_used(ids)
    return render_template('api_list.html', apis=apis, usage_count=usage_count, api_links_count=api_links_count, apis_last_used=apis_last_used)

@api_bp.route('/apis/new')
def apis_new():
    assert_logged_in()
    default_api={"paths":[{"params":[{"type": "credential", "name": "API_KEY"},{"type": "string", "name": "query"}]}]}
    return render_template('api_new.html', errors={}, api=default_api, uuid=uuid)

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
        return render_template('api_new.html', errors=errors, api=api)
    for k, v in api_object.items():
        api[k]=v

    saved = db.save(api)
    return redirect('/apis/'+api["_id"])

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
    page = int(request.args.get("page", 1))
    limit = 10
    api = db.get(id)
    assert_owner(api)
    logs, total_count = api_service(api).get_logs(limit, limit*(page-1))
    return render_template('api_usage.html', api=api, logs=logs, page=page, limit=limit, total_count=total_count)

@api_bp.delete('/apis/<id>')
def delete(id):
    doc = db.get(id)
    if doc is not None:
        assert_owner(doc)
        db.delete(id)
        response = make_response("", 200)
        response.headers['HX-Redirect'] = url_for("apis.apis_my")
        return response
    flash("You can't delete that.", "error")
    return redirect(url_for("apis.apis_show", id=id))


