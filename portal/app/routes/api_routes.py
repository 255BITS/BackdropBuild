from flask import Flask, render_template, redirect, request, jsonify, url_for, flash
import re

from flask import Blueprint
api_bp = Blueprint('apis', __name__)

@api_bp.route('/discover-apis')
def apis_discover():
    return render_template('api_discover.html')

@api_bp.route('/apis')
def apis_my():
    return render_template('api_list.html')

@api_bp.route('/apis/new')
def apis_new():
    return render_template('api_new.html')

@api_bp.route('/apis/create', methods=["POST"])
def apis_create():
    # Check if request content type is form data
    if request.content_type != 'application/x-www-form-urlencoded':
        return jsonify({"error": "Content type must be application/x-www-form-urlencoded"}), 400

    errors = {}

    # Extract the fixed attributes
    name = request.form.get("name", "")
    defaultFunctionName = request.form.get("defaultFunctionName", "")
    method = request.form.get("method", "")
    url = request.form.get("url", "")
    shortDescription = request.form.get("shortDescription", "")

    # Validation checks
    if not name:
        errors['name'] = 'Name cannot be empty.'
    # TODO: Check for name uniqueness in the database or data store
    if not shortDescription:
        errors['shortDescription'] = 'Short description cannot be empty.'
    if not url:
        errors['url'] = 'URL cannot be empty.'
    elif not re.match(r'^https://', url):
        errors['url'] = 'URL must start with https://'

    # Initialize an empty list to store the parameters
    params = []

    # Iteratively process each pair of 'type' and 'input'
    i = 0
    while True:
        param_type_key = f'param{i}-type'
        param_input_key = f'param{i}-input'

        # Check if both keys exist in the form data
        if param_type_key in request.form and param_input_key in request.form:
            params.append([request.form[param_type_key], request.form[param_input_key]])
            i += 1
        else:
            break

    api_object = {
        "name": name,
        "defaultFunctionName": defaultFunctionName,
        "method": method,
        "url": url,
        "shortDescription": shortDescription,
        "type": "API",
        "params": params
    }

    # If there are errors, render the api_new template with errors
    if errors:
        return render_template('api_new.html', errors=errors, name=name, defaultFunctionName=defaultFunctionName, method=method, url=url, shortDescription=shortDescription, params=params)

    # Add your logic here to handle the attributes and 'params' list
    return redirect('/apis/1')

@api_bp.route('/apis/<id>')
def apis_show(id):
    return render_template('api_show.html')

@api_bp.route('/apis/<id>/usage')
def apis_show_usage(id):
    return render_template('api_usage.html')


