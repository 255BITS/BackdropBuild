import os
import requests
from requests.auth import HTTPBasicAuth

# Your CouchDB admin credentials
admin_user = os.getenv("ADMIN_USER", None)
admin_pass = os.getenv("ADMIN_PASSWORD", None)

# CouchDB server details
couchdb_url = 'http://localhost:5984/'

# User details
username = 'gptactionhub'
password = 'gptactionhub'

# Step 1: Create a new user
user_doc = {
    "type": "user",
    "name": username,
    "roles": [],
    "password": password
}
users_url = couchdb_url + '_users/org.couchdb.user:' + username
user_creation_response = requests.put(users_url, json=user_doc, auth=HTTPBasicAuth(admin_user, admin_pass))

# Step 2: Create a new database
db_url = couchdb_url + username
db_creation_response = requests.put(db_url, auth=HTTPBasicAuth(admin_user, admin_pass))

# Step 3: Set permissions for the user on the new database
permissions = {
    'admins': {
        'names': [username],
        'roles': []
    },
    'members': {
        'names': [username],
        'roles': []
    }
}
security_url = db_url + '/_security'
permission_response = requests.put(security_url, json=permissions, auth=HTTPBasicAuth(admin_user, admin_pass))

# Output the responses
print(user_creation_response.json(), db_creation_response.json(), permission_response.json())
