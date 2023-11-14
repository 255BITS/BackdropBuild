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
