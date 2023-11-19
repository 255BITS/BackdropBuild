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


