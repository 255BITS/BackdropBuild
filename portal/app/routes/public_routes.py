from flask import Blueprint, render_template
from shared.couch import db
from app.services.actions_service import ActionsService
from app.services.swagger_service import generate_openapi_spec_for_actions

public_bp = Blueprint('public', __name__)

@public_bp.get('/')
def home():
    return render_template('landing.html', count_apis=db.count_apis())

@public_bp.get('/openapi/<actions_id>.json')
def get_openapi_spec(actions_id):
    actions, apis, _ = ActionsService(None).get_details(actions_id)
    #TODO 404?
    return generate_openapi_spec_for_actions(actions, apis, "https://6230-83-136-182-61.ngrok.io")
