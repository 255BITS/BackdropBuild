import re

def parse_api_object(request):
    errors = {}

    # Extract the fixed attributes
    title = request.form.get("title", "")
    operation_id = request.form.get("path0_operation_id", "")
    method = request.form.get("path0_method", "")
    url = request.form.get("path0_url", "")
    description = request.form.get("description", "")
    privacy_policy = request.form.get("privacy_policy", "")
    path_id = request.form.get("path0_path_id")

    # Validation checks
    if not title:
        errors['title'] = 'Title cannot be empty.'
    # TODO: Check for title uniqueness in the database or data store
    if not description:
        errors['description'] = 'Short description cannot be empty.'
    if not operation_id:
        errors['operation_id'] = 'Operation ID cannot be empty.'
    if not url:
        errors['url'] = 'URL cannot be empty.'
    elif not re.match(r'^https://', url):
        errors['url'] = 'URL must start with https://'

    # Initialize an empty list to store the parameters
    params = []

    # Iteratively process each pair of 'type' and 'input'
    i = 0
    while True:
        param_type_key = f'path0_param{i}-type'
        param_input_key = f'path0_param{i}-input'

        # Check if both keys exist in the form data
        if param_type_key in request.form and param_input_key in request.form:
            params.append({"type": request.form[param_type_key], "name":request.form[param_input_key]})
            if request.form[param_input_key] == '':
                errors[param_input_key] = "Parameter "+str(i)+" must have a title"
            i += 1
        else:
            break

    api_object = {
        "title": title,
        "paths": [
            {
                "path_id": path_id,
                "operation_id": operation_id,
                "method": method,
                "url": url,
                "params": params
            }
        ],
        "description": description,
        "type": "API",
        "privacy_policy": privacy_policy
    }

    return errors, api_object
