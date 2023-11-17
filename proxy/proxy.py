from quart import Quart, request, jsonify
import httpx
import time
import asyncio
import logging
import signal
import os

app = Quart(__name__)
logging_tasks = set()
api_call_tasks = set()
url_api_lookup_table = {}
url_action_lookup_table = {}

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
MAPPING_API_URL = COUCHDB_PROTOCOL+COUCHDB_USER+":"+COUCHDB_PASSWORD+"@"+COUCHDB_HOST+"/"+COUCHDB_DATABASE+"/_design/apis/_views/urls"
#TODO create view, check abstraction
MAPPING_ACTION_URL = COUCHDB_PROTOCOL+COUCHDB_USER+":"+COUCHDB_PASSWORD+"@"+COUCHDB_HOST+"/"+COUCHDB_DATABASE+"/_design/apis/_views/schema"

# Setup asynchronous logging
logger = logging.getLogger("quart.app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def async_log(request_data, response_data, response_time):
    log_message = f"Request Data: {request_data}, Response Data: {response_data}, Response Time: {response_time} seconds"
    await asyncio.to_thread(logger.info, log_message)

async def fetch_api_url_mapping():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(MAPPING_API_URL)
            if response.status_code == 200:
                return response.json()
            else:
                return url_api_lookup_table  # Return current mapping on failure
        except httpx.RequestError:
            return url_api_lookup_table  # Return current mapping on failure

async def fetch_action_mapping():
    async with httpx.AsyncClient() as client:
        try:
            print("Updating action lookup table")
            response = await client.get(MAPPING_ACTION_URL)
            if response.status_code == 200:
                return response.json()
            else:
                return url_action_lookup_table  # Return current mapping on failure
        except httpx.RequestError:
            return url_action_lookup_table  # Return current mapping on failure


# TODO can we just subscribe to the views?
async def update_api_lookup_table(breakloop):
    while True:
        print("Updating api lookup table")
        api_urls = await fetch_api_url_mapping()
        if api_urls:
            url_api_lookup_table.update(api_urls)
        if breakloop:
            break
        await asyncio.sleep(60)  # Wait for 1 minute before next update

async def update_action_lookup_table(breakloop):
    while True:
        action_info = await fetch_action_mapping()
        if action_info:
            url_action_lookup_table.update(action_info)
        if breakloop:
            break
        await asyncio.sleep(60)  # Wait for 1 minute before next update

@app.route('/<id>', methods=['GET', 'POST', 'PUT', 'DELETE', "PATCH"])
async def passthrough(id):
    start_time = time.time()
    method = request.method
    data = await request.get_data()
    headers = dict(request.headers)

    target_url = url_lookup_table.get(id)
    if target_url is None:
        return jsonify({"error": "API not found"}, 404)

    async with httpx.AsyncClient() as client:
        api_call = client.request(method, f"{target_url}/{id}", content=data, headers=headers)
        api_call_task = asyncio.create_task(api_call)
        api_call_tasks.add(api_call_task)
        api_call_task.add_done_callback(api_call_tasks.discard)

        try:
            response = await api_call_task
            response_data = response.text
        except httpx.RequestError as e:
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

@app.before_serving
async def before_serving():
    #asyncio.get_event_loop().add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))
    #asyncio.get_event_loop().add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown()))
    await update_api_lookup_table(True)  # Perform initial update of URL lookup table
    await update_action_lookup_table(True)  # Perform initial update of URL lookup table
    # TODO
    asyncio.create_task(update_api_lookup_table(False))  # Start the task to update URL lookup table periodically
    asyncio.create_task(update_action_lookup_table(False))  # Start the task to update URL lookup table periodically

if __name__ == '__main__':
    app.run(debug=True, port=10004)

