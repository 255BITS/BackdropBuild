import re

def parse_api_object(request):
    errors = {}

    # Extract the fixed attributes
    name = request.form.get("name", "")
    default_function_name = request.form.get("default_function_name", "")
    method = request.form.get("method", "")
    url = request.form.get("url", "")
    description = request.form.get("description", "")
    privacy_policy = request.form.get("privacy_policy", "")

    # Validation checks
    if not name:
        errors['name'] = 'Name cannot be empty.'
    # TODO: Check for name uniqueness in the database or data store
    if not description:
        errors['description'] = 'Short description cannot be empty.'
    if not default_function_name:
        errors['default_function_name'] = 'Default function name cannot be empty.'
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
            if request.form[param_input_key] == '':
                errors[param_input_key] = "Parameter "+str(i)+" must have a name"
            i += 1
        else:
            break

    api_object = {
        "name": name,
        "default_function_name": default_function_name,
        "method": method,
        "url": url,
        "description": description,
        "type": "API",
        "params": params,
        "privacy_policy": privacy_policy
    }

    return errors, api_object
