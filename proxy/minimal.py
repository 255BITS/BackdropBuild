from flask import Flask, request

app = Flask(__name__)

@app.before_request
def debug_request_info():
   app.logger.info(f'Headers: {dict(request.headers)}')
   app.logger.info(f'Method: {request.method}')
   app.logger.info(f'URL: {request.url}')
   app.logger.info(f'Body: {request.get_data()}')


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE'])
def catch_all(path):
    return f"Button pressed: {path}. What did it do??"

if __name__ == '__main__':
    app.run(debug=True, port=10005, host="0.0.0.0")
