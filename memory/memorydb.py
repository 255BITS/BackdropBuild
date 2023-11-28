import sys
import os
import time
from pathlib import Path
shared_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(shared_path)

from shared import db

class MemoryDB(db.DB):
    def create_views(self):
      map_store ='''
        function(doc) {
            if (doc.id && doc.timestamp) {
                emit([doc.id, doc.timestamp], doc);
            }
        }
      '''
      self.create_view_ddoc("memory", "store", map_store)


COUCHDB_USER = os.getenv("COUCHDB_USER", "gptactionhub-memory")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", "gptactionhub-memory")
COUCHDB_HOST = os.getenv("COUCHDB_HOST", "localhost:5984")
COUCHDB_DATABASE = os.getenv("COUCHDB_DATABASE", "gptactionhub-memory")
couch_credentials = {
    'url': f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}",
    'db_name': COUCHDB_DATABASE
}
db = None

def get_db():
    global db
    if db is None:
        db = MemoryDB(couch_credentials)
    return db

def read(id):
    results = get_db().query_view('memory', 'store', startkey=[id, {}], endkey=[id], descending=True, limit=1)
    return results[0]['value'] if len(results)>0 else None

def write(id, value):
    doc = {'id': id, 'value': value, 'timestamp': time.time()}
    get_db().save(doc)
    return doc

def list(id, limit=10, skip=0):
    results = get_db().query_view('memory', 'store', startkey=[id, {}], endkey=[id], descending=True, limit=limit, skip=skip)
    return [row["value"] for row in results]

