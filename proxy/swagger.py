class Swagger:
    def __init__(self, title, version, description, base_url):
        self.openapi_version = '3.0.0'
        self.title = title
        self.version = version
        self.description = description
        self.base_url = base_url
        self.paths = {}
        self.components = {'schemas': {}}

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
                'description': 'API server'
            }],
            'paths': self.paths,
            'components': self.components
        }

# Helper function to create schema
def create_schema(description, example):
    return {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'description': description,
                'example': example
            }
        }
    }
