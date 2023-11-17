from passlib.hash import bcrypt
from shared import utils
from shared.couch import db
import arrow
import secrets
import string

def decode_auth(auth):
    if auth["auth_type"] == "api_key_basic":
        value = f"{auth['username']}:{auth['password']}"
        return auth | {
            "value_encoded": ''.join(['*' for _ in value]),
            "value": value
        }

def generate_random_string(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class ActionsService:
    def __init__(self, user):
        self.user = user

    def add_computed_values(self, actions):
        computed = {
            "last_updated" : arrow.get(actions["updated_at"]).humanize()
        }
        return computed | actions

    def list(self):
        actions_list = db.get_actions_for_user(self.user["_id"])
        actions_list = [self.add_computed_values(actions) for actions in actions_list]
        return actions_list

    def create(self, name):
        #TODO validate name
        actions = db.save({
            "name": name,
            "type": "actions",
            "user_id": self.user["_id"],
        })
        username = generate_random_string()
        password = generate_random_string()
        password_hash = bcrypt.hash(password)
        auth = db.save({
            "actions_id": actions["_id"],
            "auth_type": "api_key_basic",
            "type": "auth",
            "user_id": self.user["_id"],
            "username": username,
            "password": password, #TODO encrypt
            "password_hash": password_hash,
        })
        return actions

    def add_api_link(self, id, api_id, params):
        actions = self.get(id)
        if "api_links" not in actions:
            actions["api_links"] = []
        actions["api_links"] += [
            {
                "api_id": api_id,
                "params": params
            }
        ]
        return db.save(actions)


    def get(self, id):
        #TODO 404
        #TODO doc type check
        actions = db.get(id)
        auths = db.get_auths_for_actions(actions["_id"])
        auths = [decode_auth(auth) for auth in auths]
        return actions | { "auths": auths }

    def update(self, id, update_dict):
        actions = db.get(id)
        db.save(actions | update)

    def get_apis(self):
        apis = db.query_view('apis', 'public')
        apis += db.query_view('apis', 'by_user', key=self.user['_id'])
        return apis
