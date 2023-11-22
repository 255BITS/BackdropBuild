from urllib.parse import urlparse

def generate_openapi_spec_for_actions(actions, apis, base_url="https://gptactionhub.com"):
    title = actions["name"]
    version = "1.0" #TODO
    description = "" #TODO is this used?
    swagger = Swagger(title, version, description, base_url)
    for api, api_link in zip(apis, actions["api_links"]):
        swagger.add_api(api, api_link, actions)
    return swagger.generate_spec()

class Swagger:
    def __init__(self, title, version, description, base_url):
        self.openapi_version = '3.1.0'
        self.title = title
        self.version = version
        self.description = description
        self.base_url = base_url
        self.paths = {}
        self.components = {'schemas': {}}

    def add_api(self, api, api_link, actions):
        params = {}
        for api_path, api_link_path in zip(api["paths"], api_link["paths"]):
            print("--", api_path, api_link_path)

            params[api_path["method"].lower()] = []
            for api_param, api_link_param in zip(api_path["params"], api_link_path["params"]):
                #TODO match by path_id
                #TODO support more than one operation_id
                param_name = api_link_param["name"]
                param_type = api_param["type"]

                if api_param['type'] == "credential":
                    pass
                if "source" in api_link_param and api_link_param["source"] == "constant":
                    pass
                params[api_path["method"].lower()].append({
                    'schema': {
                        'type': param_type,
                    },
                    "name": param_name,
                    "in": "query",
                    'description': 'TODO',
                    'required': True
                })
            path = f"/{actions['_id']}/{api_link_path['operation_id']}"

            self.add_path(path, api_path["method"].lower(), {
                "description": api["description"], #TODO
                "operationId": api_link_path["operation_id"],
                "parameters": params[api_path["method"].lower()],
                 'responses': {
                    '200': {
                        'description': 'Message received successfully',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'string'
                                }
                            }
                        }
                    }
                }
            })
        #TODO add i/o types
        #TODO review spec

    def add_path(self, path, method, path_data):
        if path not in self.paths:
            self.paths[path] = {}
        if method in self.paths[path]:
            raise f"Already defined path {path} {method}"
        self.paths[path][method] = path_data

    def add_schema(self, name, schema):
        self.components['schemas'][name] = schema

    def generate_spec(self):
        return {
            'openapi': self.openapi_version,
            'info': {
                'title': self.title,
                'version': self.version,
                'description': self.description
            },
            'servers': [{
                'url': self.base_url,
                'description': 'The hub for GPT actions'
            }],
            'paths': self.paths,
            'components': self.components
        }


