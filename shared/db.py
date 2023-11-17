import couchdb
import traceback
from typing import List, Union
from shared import utils

class DB:
    def __init__(self, couch_credentials):
        self.server = couchdb.Server(url=couch_credentials['url'])
        self.db_name = couch_credentials['db_name']

        # Create the database if it doesn't exist
        if self.db_name not in self.server:
            self.server.create(self.db_name)
        self.db = self.server[self.db_name]
        self.create_views()

    def create_views(self):
        self.create_actions_views()
        self.create_api_views()
        self.create_auth_views()
        self.create_user_views()

    def insert(self, data):
        try:
            doc_id, doc_rev = self.db.save(data)
            return doc_id, doc_rev
        except couchdb.http.ResourceConflict:
            # Handle conflict if necessary
            return None

    def create_view_ddoc(self, design_doc_name, view_name, map_func, reduce_func=None):
        """
        Utility function to create a view design document and check for its existence.
        Optionally, a reduce function can be added.
        """
        design_doc_id = f"_design/{design_doc_name}"

        # Initialize the design document if it doesn't exist
        if design_doc_id not in self.db:
            self.db[design_doc_id] = {
                "_id": design_doc_id,
                "views": {}
            }

        current_design_doc = self.db[design_doc_id]
        update_needed = False  # Flag to determine if an update is needed

        # Check if the view already exists within the design document
        if view_name not in current_design_doc["views"]:
            current_design_doc["views"][view_name] = {
                "map": map_func
            }
            if reduce_func:
                current_design_doc["views"][view_name]["reduce"] = reduce_func
            update_needed = True  # New view, so an update is needed
        else:
            # Check if the map function has changed
            existing_map_func = current_design_doc["views"][view_name].get("map", "")
            existing_reduce_func = current_design_doc["views"][view_name].get("reduce", "")

            if existing_map_func != map_func:
                current_design_doc["views"][view_name]["map"] = map_func
                update_needed = True  # Map function changed, so an update is needed

            if existing_reduce_func != reduce_func:
                if reduce_func:
                    current_design_doc["views"][view_name]["reduce"] = reduce_func
                else:
                    # Remove the reduce key if reduce_func is None
                    current_design_doc["views"][view_name].pop("reduce", None)
                update_needed = True  # Reduce function changed, so an update is needed

        # Update the design document in the database if needed
        if update_needed:
            self.db[design_doc_id] = current_design_doc

    def create_actions_views(self):
        """
        Create views related to actions.
        """
        by_user = """function(doc) {
                                if (doc.type === 'actions') {
                                    emit(doc.user_id, doc);
                                }
                            }"""

        self.create_view_ddoc("actions", "by_user", by_user)

    def create_auth_views(self):
        """
        Create views related to api keys.
        """
        by_actions = """function(doc) {
                                if (doc.type === 'auth') {
                                    emit(doc.actions_id, doc);
                                }
                            }"""

        self.create_view_ddoc("auths", "by_actions", by_actions)

    def create_api_views(self):
        """
        Create views related to apis.
        """
        map_count = """function(doc) { 
                                if (doc.type === 'API') { 
                                    emit(null, null); 
                                } 
                            }"""
        public = """function(doc) { 
                                if (doc.type === 'API' && doc.visibility === 'public') { 
                                    emit(null, doc); 
                                } 
                            }"""
        by_user = """function(doc) { 
                                if (doc.type === 'API') { 
                                    emit(doc.user_id, doc); 
                                } 
                            }"""
        urls = """function(doc) { 
                                if (doc.type === 'API') { 
                                    emit(null, doc.url); 
                                } 
                            }"""

        self.create_view_ddoc("apis", "count", map_count, reduce_func="_count")
        self.create_view_ddoc("apis", "public", public)
        self.create_view_ddoc("apis", "by_user", by_user)
        self.create_view_ddoc("apis", "urls", urls)

    def create_user_views(self):
        map_users_by_email = """function(doc) {
                                if (doc.type === 'user' && doc.email) {
                                    emit(doc.email, doc);
                                } 
                            }"""
        self.create_view_ddoc("users", "by_email", map_users_by_email)

    def query_view(self, design_doc, view_name, **kwargs) -> List:
        """
        Query a CouchDB view and return the results as a list.
        """
        view_result = self.db.view(f'{design_doc}/{view_name}', **kwargs)
        return [row.value for row in view_result] if view_result else []

    def count_apis(self):
        result = self.db.view('apis/count', reduce=True)
        count = result.rows[0]['value'] if result.rows else 0
        return count

    def delete(self, doc_id):
        del self.db[doc_id]

    def save(self, data):
        try:
            current_datetime = utils.get_current_datetime_iso8601()
            defaults = {
                "created_at": current_datetime,
                "updated_at": current_datetime
            }
            if "updated_at" in data:
                data["updated_at"] = current_datetime
            doc_id, doc_rev = self.db.save(defaults | data)
            return self.db[doc_id]
        except couchdb.http.ResourceConflict:
            traceback.print_exc()
            # Handle conflict if necessary
            return None

    def get(self, _id):
        return self.db.get(_id)

    def get_user_by_email(self, email):
        """
        Get a user by email
        """
        users = self.query_view('users', 'by_email', key=email)
        return users[0] if users else None

    def get_actions_for_user(self, user_id):
        return self.query_view('actions', 'by_user', key=user_id)

    def get_auths_for_actions(self, actions_id):
        return self.query_view('auths', 'by_actions', key=actions_id)
