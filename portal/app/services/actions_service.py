from passlib.hash import bcrypt
import datetime
from shared import utils
from shared.couch import db
import secrets
import string
from app.services.credentials_service import CredentialsService

def decode_auth(auth):
    creds = CredentialsService()
    if auth["auth_type"] == "api_key_basic":
        password = creds.try_decrypt(auth['password'])
        value = f"{auth['username']}:{password}"
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

    def list(self, limit, skip):
        actions_list = db.query_view('actions', 'by_user', key=self.user["_id"], limit=limit, skip=skip, reduce=False)
        total_count = db.query_view('actions', 'by_user', key=self.user["_id"], reduce=True)[0]
        return actions_list, total_count

    def create(self, name):
        #TODO validate name
        actions = db.save({
            "api_links": [],
            "name": name,
            "type": "actions",
            "user_id": self.user["_id"],
            })
        username = generate_random_string()
        password = generate_random_string()
        password_hash = bcrypt.hash(password)
        auth = db.save({
            "action_id": actions["_id"],
            "auth_type": "api_key_basic",
            "type": "auth",
            "user_id": self.user["_id"],
            "username": username,
            "password": CredentialsService().encrypt(password), #TODO encrypt
            "password_hash": password_hash,
        })
        return actions

    def get_details(self, id):
        #TODO 404
        #TODO doc type check
        actions = db.get(id)
        auths = db.get_auths_for_actions(actions["_id"])
        apis = db.get([link['api_id'] for link in actions["api_links"]])
        auths = [decode_auth(auth) for auth in auths]
        return actions, apis, auths

    def update(self, id, update_dict):
        actions = db.get(id)
        db.save(actions | update_dict)

    def get_apis(self, limit, skip):
        apis = db.query_view('apis', 'public_or_by_user', keys=[["public", 0],[self.user["_id"], 1]], limit=limit, skip=skip, reduce=False)
        total_count = sum(db.query_view('apis', 'public_or_by_user', key=["public", 0], reduce=True)+db.query_view('apis', 'public_or_by_user', key=[self.user["_id"], 1], reduce=True)+[0])
        return apis, total_count

    def get_logs(self, actions, limit, skip):
        action_id = actions["_id"]
        logs = db.query_view('logs', 'by_actions', limit=limit, skip=skip, key=action_id, reduce=False)
        total_count = sum(db.query_view('logs', 'by_actions', key=action_id, limit=limit, skip=skip, reduce=True)+[0])
        return logs, total_count

    def get_sparklines(self, ids):
        """
        Get sparkline data for the given action IDs.

        Args:
        - ids (list): List of action IDs.

        Returns:
        - dict: A dictionary with action IDs as keys and sparkline data points as values.
        """

        # Calculate the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(weeks=2)

        # SVG dimensions
        svg_width = 300
        svg_height = 50

        # Total number of days for x-axis distribution
        total_days = (end_date - start_date).days + 1

        # Initialize sparkline data dictionary
        sparkline_data = {}

        for action_id in ids:
            # Fetch log counts for this action_id
            log_counts = db.count_logs_by_actions_day(action_id, start_date, end_date)

            # Extract and normalize counts
            counts = [log_counts.get((action_id, start_date.year, start_date.month, start_date.day + i), 0) for i in range(total_days)]
            max_count = max(counts + [1]) if counts else 1
            normalized_counts = [count / max_count for count in counts]

            # Create points for polyline
            points = []
            for i, count in enumerate(normalized_counts):
                x = (i / total_days) * svg_width
                y = svg_height - (count * svg_height)
                points.append(f"{x},{y}")

            sparkline_data[action_id] = " ".join(points)

        return sparkline_data
