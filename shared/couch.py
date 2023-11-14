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
db = None

def initialize_couch(couch_credentials):
    global db
    db = DB(couch_credentials)

initialize_couch(couch_credentials)
