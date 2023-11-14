from flask import Flask, render_template, redirect, request, jsonify, url_for, flash
from shared.couch import db
from app.services.api_service import parse_api_object

from flask import Blueprint
api_bp = Blueprint('apis', __name__)

@api_bp.route('/discover-apis')
def apis_discover():
    apis = db.query_view('apis', 'public')
    return render_template('api_discover.html', apis=apis)

@api_bp.route('/apis')
def apis_my():
    return render_template('api_list.html')

@api_bp.route('/apis/new')
def apis_new():
    return render_template('api_new.html', errors={}, api={})

@api_bp.route('/apis/create', methods=["POST"])
def apis_create():
    # Check if request content type is form data
    if request.content_type != 'application/x-www-form-urlencoded':
        return jsonify({"error": "Content type must be application/x-www-form-urlencoded"}), 400

    errors, api_object = parse_api_object(request)
    # If there are errors, render the api_new template with errors
    if errors:
        return render_template('api_new.html', errors=errors, api={"name":name, "defaultFunctionName":defaultFunctionName, "method":method, "url":url, "shortDescription":shortDescription, "params":params})
    new_api_object = db.save(api_object)

    # Add your logic here to handle the attributes and 'params' list
    return redirect('/apis/'+new_api_object["_id"])

@api_bp.route('/apis/<id>', methods=["GET"])
def apis_show(id):
    # TODO security
    api = db.get(id)
    return render_template('api_show.html', api=api)

@api_bp.route('/apis/<id>/edit', methods=["GET"])
def apis_edit(id):
    # TODO security
    api = db.get(id)
    return render_template('api_new.html', errors=[], api=api)

@api_bp.route('/apis/<id>/update', methods=["POST"])
def apis_update(id):
    # TODO security
    errors, api_object = parse_api_object(request)
    api_object["id"]=id
    db.save(api_object)
    return render_template('api_show.html', errors=[], api=api_object)

@api_bp.route('/apis/<id>/publish', methods=["POST"])
def apis_publish(id):
    # TODO security
    api = db.get(id)
    api["visibility"]="Public"
    db.save(api)
    return render_template('api_show.html', api=api)

@api_bp.route('/apis/<id>/unpublish', methods=["POST"])
def apis_unpublish(id):
    # TODO security
    api = db.get(id)
    api["visibility"]="Private"
    db.save(api)
    return render_template('api_show.html', api=api)


@api_bp.route('/apis/<id>/usage')
def apis_show_usage(id):
    # TODO security
    return render_template('api_usage.html')


