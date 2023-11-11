from quart import Quart, request, jsonify
from swagger import Swagger, create_schema

app = Quart(__name__)
openapi = Swagger(title='Alert API', version='1.0.0', description='API for alert messages', base_url='https://d12d-64-44-84-226.ngrok-free.app')

openapi.add_schema('AlertMessage', create_schema('The alert message', 'System overload'))
openapi.add_schema('ResponseMessage', create_schema('The response message', 'Success: System overload'))

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
    }
})

@app.route('/alert', methods=['POST'])
async def alert():
    data = await request.get_json()
    message = data.get('message', '')
    print("I received", message)
    return jsonify(status='Success', received_message=message)

@app.route('/', methods=['GET'])
async def get_apidocs():
    return openapi.generate_spec()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10001)

