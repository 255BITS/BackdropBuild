import os
from shared.db import DB

DEFAULT_DATABASE = "gptactionhub" 
DEFAULT_HOST = "localhost:5984"
DEFAULT_PASSWORD = "gptactionhub" 
DEFAULT_USER = "gptactionhub" 

COUCHDB_DATABASE = os.getenv("COUCHDB_DATABASE", DEFAULT_DATABASE)
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", DEFAULT_PASSWORD)
COUCHDB_HOST = os.getenv("COUCHDB_HOST", DEFAULT_HOST)
COUCHDB_USER = os.getenv("COUCHDB_USER", DEFAULT_USER)

if COUCHDB_USER == DEFAULT_USER and COUCHDB_PASSWORD == DEFAULT_PASSWORD:
    print("Using default couch settings.")

couch_credentials = {
    'url': f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}",
    'db_name': COUCHDB_DATABASE
}
couch_credentials_logs = couch_credentials | {
    'db_name': COUCHDB_DATABASE+"-logs"
}
db = None
logs_db = None

def initialize_couch(couch_credentials):
    global db, logs_db
    db = DB(couch_credentials, partition="app")
    logs_db = DB(couch_credentials_logs, partition="logs")

initialize_couch(couch_credentials)
