import re
from shared.couch import db

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
        errors['path0_operation_id'] = 'Operation ID cannot be empty.'
    if not url:
        errors['path0_url'] = 'URL cannot be empty.'
    elif not re.match(r'^https://', url) and not re.match(r'^http://', url):
        errors['path0_url'] = 'URL must start with https:// or http://'

    # Initialize an empty list to store the parameters
    params = []

    # Iteratively process each pair of 'type' and 'input'
    i = 0
    while True:
        param_type_key = f'path0_param{i}_type'
        param_input_key = f'path0_param{i}_input'

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

class ApiService:
    def __init__(self, api):
        self.api = api

    def get_logs(self, limit, skip):
        api_id = self.api["_id"]
        logs = db.query_view('logs', 'by_api', limit=limit, skip=skip, key=api_id, reduce=False)
        total_count = sum(db.query_view('logs', 'by_api', key=api_id, limit=limit, skip=skip, reduce=True)+[0])
        return logs, total_count
