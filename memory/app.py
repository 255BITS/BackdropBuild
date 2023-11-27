from flask import Flask, request, jsonify
import memorydb

app = Flask(__name__)

@app.route('/<datatype>/write', methods=['POST'])
@app.route('/<datatype>/read', methods=['GET'])
@app.route('/<datatype>/history', methods=['GET'])
def handle_request(datatype):
    if datatype not in ['conversation', 'gpts', 'user']:
        return jsonify({"error": "Invalid data type"}), 400

    if request.method == 'POST':
        return write_data(datatype)
    elif request.method == 'GET':
        if 'history' in request.path:
            return history_data(datatype)
        else:
            return read_data(datatype)

def write_data(datatype):
    id = get_id_from_headers(datatype)
    doc = request.json.get('message')
    memorydb.write(id, doc)
    return "", 204

def read_data(datatype):
    id = get_id_from_headers(datatype)
    data = memorydb.get(id)
    if data:
        return data
    return jsonify({"message": "No data found"}), 404

def history_data(datatype):
    id = get_id_from_headers(datatype)
    data = memorydb.list(id)
    return jsonify(data), 200

def get_id_from_headers(datatype):
    action_hub_id = request.headers.get('ActionHub-Id')
    second_key = ''
    if datatype == 'conversation':
        second_key = request.headers.get('Openai-Conversation-Id')
    elif datatype == 'user':
        second_key = request.headers.get('Openai-Ephemeral-User-Id')
    else:  # For gpts or other types
        second_key = request.headers.get('Openai-Gpt-Id')

    return f"{action_hub_id}_{second_key}"

app.run(debug=True, host='0.0.0.0', port=10005)
