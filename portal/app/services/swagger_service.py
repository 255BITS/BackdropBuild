def generate_openapi_spec_for_actions(actions, apis):
    title = actions["name"]
    version = "1.0" #TODO
    description = "" #TODO is this used?
    base_url = "https://gptactionhub.com" 
    swagger = Swagger(title, version, description, base_url)
    for api, api_link in zip(apis, actions["api_links"]):
        swagger.add_api(api, api_link)
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

    def add_api(self, api, api_link):
        print("--API")
        print(api)
        for api_param, api_link_param in api["params"], api_link["params"]:
            param_type = api_param[0]
            param_name = api_link_param["name"]

            if param_type == "credential":
                pass
            if api_link_param["type"] == "constant":
                pass

            params.append()

        self.add_action(url, api["method"], {
            "summary": api["description"],
            "operationId": api_link["name"],
            "requestBody": {
                "required": True,
                "content": {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/AlertMessage'
                        }
                    }
                }

            },
            'responses': {
                '200': {
                    'description': 'Message received successfully',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ResponseMessage' #TODO
                            }
                        }
                    }
                }
            }
        })
        print("--api_link")
        print(api_link)
        #TODO add path for api_link
        #TODO add i/o types
        #TODO review spec
        pass

    def add_path(self, path, methods):
        self.paths[path] = methods

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


