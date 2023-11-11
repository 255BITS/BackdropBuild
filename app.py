from quart import Quart, request, jsonify
from swagger import Swagger, create_schema

app = Quart(__name__)
openapi = Swagger(title='Alert API', version='1.0.0', description='API for alert messages', base_url='https://d12d-64-44-84-226.ngrok-free.app')

openapi.add_schema('AlertMessage', create_schema('The alert message', 'System overload'))
openapi.add_schema('ResponseMessage', create_schema('The response message', 'Success: System overload'))

alert_response_schema = {
    'type': 'object',
    'properties': {
        'message': {
            'type': 'string',
            'description': 'Message of the Day',
            'example': 'Welcome to the Alert API!'
        }
    }
}
openapi.add_schema('AlertResponse', alert_response_schema)

openapi.add_path('/alert', {
    'post': {
        'summary': 'Post an alert message',
        'operationId': 'postAlert',
        'tags': ['Alert'],
        'requestBody': {
            'required': True,
            'content': {
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
                            '$ref': '#/components/schemas/ResponseMessage'
                        }
                    }
                }
            }
        }
    },
    'get': {
        'summary': 'Get the last alert',
        'operationId': 'getAlert',
        'tags': ['Alert'],
        'responses': {
            '200': {
                'description': 'Get the last alert that was posted.',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/AlertResponse'
                        }
                    }
                }
            }
        }
    }
})


last_alert = "This is the first call."

@app.before_request
async def debug_request_info():
   app.logger.info(f'Headers: {dict(request.headers)}')
   app.logger.info(f'Method: {request.method}')
   app.logger.info(f'URL: {request.url}')
   app.logger.info(f'Body: {await request.get_data()}')

@app.route('/alert', methods=['POST'])
async def alert():
    global last_alert
    data = await request.get_json()
    message = data.get('message', '')
    last_alert = message
    return jsonify(status='Success', received_message=message)


@app.route('/alert', methods=['GET'])
async def get_alert():
    return jsonify(message=last_alert)

@app.route('/', methods=['GET'])
async def get_apidocs():
    return openapi.generate_spec()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10001)

