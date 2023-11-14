from shared.couch import db

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
        return action

    def get(self, id):
        #TODO 404
        #TODO doc type check
        actions = db.get(id)
        apis = db.get_apis_for_actions(actions["_id"])
        return actions | { "apis": apis }
