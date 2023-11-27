from flask import Blueprint, render_template, Response
from shared.couch import db
from app.services.actions_service import ActionsService
from app.services.swagger_service import generate_openapi_spec_for_actions
import datetime

public_bp = Blueprint('public', __name__)

@public_bp.get('/')
def home():
    return render_template('landing.html', count_apis=db.count_apis())

@public_bp.get('/openapi/<action_id>.json')
def get_openapi_spec(action_id):
    actions, apis, _ = ActionsService(None).get_details(action_id)
    #TODO 404?
    return generate_openapi_spec_for_actions(actions, apis)

@public_bp.get('/privacy_policy/<action_id>')
def get_privacy_policy(action_id):
    actions, apis, _ = ActionsService(None).get_details(action_id)
    privacy_policy = "In addition to the following GPTActionHub.com may monitor request input/output, collect analytics, and share them with the Actions authors.\n"
    privacy_policy += "------\n"
    for api in apis:
        privacy_policy += "Privacy policy for the API:"+api["title"]+"\n"
        privacy_policy += api["privacy_policy"]
        privacy_policy += "\n------\n"
    privacy_policy += f"This privacy policy is valid {datetime.datetime.now().isoformat()}. GPTActionHub.com and API authors reserve the right to modify any part of the policy in the future.\n"
    return Response(privacy_policy, mimetype="text/plain")
