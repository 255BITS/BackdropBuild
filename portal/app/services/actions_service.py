from passlib.hash import bcrypt
from shared.couch import db

def generate_random_string(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class ActionsService:
    def __init__(self, user):
        self.user = user

    def list(self):
        pass

    def create(self, name):
        #TODO validate name
        action = db.save({
            "user_id": self.user["_id"],
            "type": "actions",
            "name": name
        })
        username = generate_random_string()
        password = generate_random_string()
        password_hash = bcrypt.hash(password)
        action = db.save({
            "action_id": action["_id"],
            "user_id": self.user["_id"],
            "type": "auth",
            "auth_type": "api_key_basic",
            "username": username,
            "password": password, #TODO encrypt
            "password_hash": password_hash
        })
        return action

    def get(self, id):
        #TODO 404
        #TODO doc type check
        actions = db.get(id)
        apis = db.get_apis_for_actions(actions["_id"])
        auths = db.get_auths_for_actions(actions["_id"])
        return actions | { "apis": apis }
