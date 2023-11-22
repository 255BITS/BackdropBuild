from quart import Quart, request, jsonify
from pprint import pprint
import httpx
from httpx import Timeout
import time
import asyncio
import logging
import traceback
import signal
import os

app = Quart(__name__)
logging_tasks = set()
api_call_tasks = set()
url_api_lookup_table = {}
action_lookup_table = {}


# TODO use variables from db.py
# URL for fetching the mapping
DEFAULT_DATABASE = "gptactionhub"
DEFAULT_HOST = "localhost:5984"
DEFAULT_PASSWORD = "gptactionhub"
DEFAULT_PROTOCOL = "http://"
DEFAULT_USER = "gptactionhub"
COUCHDB_DATABASE = os.getenv("COUCHDB_DATABASE", DEFAULT_DATABASE)
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", DEFAULT_PASSWORD)
COUCHDB_HOST = os.getenv("COUCHDB_HOST", DEFAULT_HOST)
COUCHDB_USER = os.getenv("COUCHDB_USER", DEFAULT_USER)
COUCHDB_PROTOCOL = os.getenv("COUCHDB_PROTOCOL", DEFAULT_PROTOCOL)
COUCHDB_URL = COUCHDB_PROTOCOL+COUCHDB_USER+":"+COUCHDB_PASSWORD+"@"+COUCHDB_HOST+"/"+COUCHDB_DATABASE
MAPPING_API_URL = COUCHDB_URL+"/_design/apis/_view/urls"
MAPPING_ACTION_URL = COUCHDB_URL+"/_design/actions/_view/api_links"

# Setup asynchronous logging
logger = logging.getLogger("quart.app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
write_lock = asyncio.Lock()

async def async_log(request_data, response_data, response_time):
    log_message = f"Request Data: {request_data}, Response Data: {response_data}, Response Time: {response_time} seconds"
    await asyncio.to_thread(logger.info, log_message)

async def fetch_api_url_mapping():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(MAPPING_API_URL)
            if response.status_code == 200:
                return response.json()['rows']
            else:
                return url_api_lookup_table  # Return current mapping on failure
        except httpx.RequestError:
            return url_api_lookup_table  # Return current mapping on failure

async def fetch_action_mapping():
    async with httpx.AsyncClient() as client:
        try:
            print("Updating action lookup table")
            print(MAPPING_ACTION_URL)
            response = await client.get(MAPPING_ACTION_URL)
            if response.status_code == 200:
                return response.json()['rows']
            else:
                return action_lookup_table  # Return current mapping on failure
        except httpx.RequestError:
            return action_lookup_table  # Return current mapping on failure

async def listen_to_changes(last_seq):
    """ Asynchronous version to listen for changes in the database """

    timeout_duration = 60  # Adjust this according to your needs
    timeout = Timeout(timeout_duration)
    async with httpx.AsyncClient() as client:
        while True:
            url = f"{COUCHDB_URL}//_changes?since={last_seq}&feed=longpoll&include_docs=true"
            try:
                response = await client.get(url)
                response.raise_for_status()
                changes = response.json()
                last_seq = changes['last_seq']

                async with write_lock:
                    for change in changes['results']:
                        doc = change.get('doc', {})
                        if doc.get('type') == 'API':
                            print(f"Document {doc['_id']} of type {doc['type']} is relevant.")
                            url_api_lookup_table[doc['_id']] = {'paths': doc['paths']}
                        elif doc.get('type') == 'actions':
                            print(f"Document {doc['_id']} of type {doc['type']} is relevant.")
                            action_lookup_table[doc['_id']] = {'api_links': doc['api_links'], 'auths': {}} #TODO doc['auths']
            except httpx.ReadTimeout:
                continue
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred:", e)
            except Exception as e:
                print(f"An error occurred:", e)
                traceback.print_exc()

async def update_api_lookup_table():
    print("Updating api lookup table")
    api_urls = await fetch_api_url_mapping()
    print("APIs found", len(api_urls))
    async with write_lock:
        for a in api_urls:
            url_api_lookup_table[a['id']]=a['value']

async def update_action_lookup_table():
    print("Updating api lookup table")
    action_info = await fetch_action_mapping()
    print("Actions found", len(action_info))
    async with write_lock:
        for a in action_info:
            action_lookup_table[a['id']]=a['value']
        pprint(action_lookup_table)

@app.route('/', methods=['GET'])
def ready():
    return "ready"

@app.before_request
async def debug_request_info():
   app.logger.info(f'Headers: {dict(request.headers)}')
   app.logger.info(f'Method: {request.method}')
   app.logger.info(f'URL: {request.url}')
   app.logger.info(f'Body: {await request.get_data()}')


@app.route('/<action_id>/<operation_id>', methods=['GET', 'POST', 'PUT', 'DELETE', "PATCH"])
async def passthrough(action_id, operation_id):
    start_time = time.time()
    method = request.method
    params = request.args
    data = await request.get_data()
    headers = dict(request.headers)
    del headers["Host"]

    if action_id not in action_lookup_table:
        return jsonify({"error": "Action not found"}, 404)
    actions_api_links = action_lookup_table[action_id]
    api = None
    active_path_id = None
    print("Found actions_api_links", actions_api_links)
    for a in actions_api_links:
        for path in a["paths"]:
            if path['operation_id']==operation_id:
                api = a
                active_path_id = path["path_id"]

    if api is None:
        return jsonify({"error": "API not found"}, 404)
    if api['api_id'] not in url_api_lookup_table:
        return jsonify({"error": "API link found in action but not in API"}, 404)

    target = url_api_lookup_table[api['api_id']]
    target_path = None
    for path in target["paths"]:
        if path["path_id"] == active_path_id:
            target_path = path

    print("TARGET", target)
    #TODO: openai token auth on action

    async with httpx.AsyncClient() as client:
        api_url = target_path['url']
        api_call = client.request(method=method, url=api_url, content=data, headers=headers, params=params)
        api_call_task = asyncio.create_task(api_call)
        api_call_tasks.add(api_call_task)
        api_call_task.add_done_callback(api_call_tasks.discard)

        try:
            response = await api_call_task
            response_data = response.text
        except httpx.RequestError as e:
            # dont await the log
            await async_log(data, "Upstream request failed", 0)
            return jsonify({"error": "Upstream request failed"}), 502

    response_time = time.time() - start_time

    log_task = asyncio.create_task(async_log(data, response_data, response_time))
    logging_tasks.add(log_task)
    log_task.add_done_callback(logging_tasks.discard)

    return jsonify(response_data), response.status_code

#TODO
async def shutdown():
    print("Shutting down active calls", 'api calls', len(api_call_tasks), 'logs', len(logging_tasks))
    all_tasks = logging_tasks.union(api_call_tasks)
    while len(all_tasks)>0:
        await asyncio.wait(all_tasks)

async def get_current_last_seq():
    """ Get the current last sequence number from the database """
    url = f"{COUCHDB_URL}/_changes?limit=1&descending=true"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return data['last_seq']

listen_task = None

@app.before_serving
async def before_serving():
    #asyncio.get_event_loop().add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))
    #asyncio.get_event_loop().add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown()))
    await update_api_lookup_table()  # Perform initial update of URL lookup table
    await update_action_lookup_table()  # Perform initial update of URL lookup table
    current_last_seq = await get_current_last_seq()
    listen_task = asyncio.create_task(listen_to_changes(current_last_seq))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10004)
