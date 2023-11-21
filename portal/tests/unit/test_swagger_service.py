import json
import os
from app.services.swagger_service import generate_openapi_spec_for_actions

def load_fixture(filename):
    path = os.path.dirname(__file__) + "/fixtures"
    file = os.path.join(path, filename)
    with open(file, 'r') as f:
        return json.load(f)

def test_generate_openapi_spec_empty():
    actions = load_fixture("empty_actions.json")
    apis = []
    result = generate_openapi_spec_for_actions(actions, [])
    assert len(result["servers"]) == 1
    assert result["info"]["title"] == "Empty"
    assert len(result["paths"]) == 0
    assert len(result["components"]["schemas"]) == 0

def test_generate_openapi_no_params():
    actions = load_fixture("single_no_params_actions.json")
    apis = [load_fixture("single_no_params_api.json")]
    result = generate_openapi_spec_for_actions(actions, apis)
    assert len(result["servers"]) == 1
    assert len(result["paths"]) == 1
    assert len(result["paths"][""]) == 1
    assert len(result["paths"][""]["post"]) > 0

def test_generate_openapi_one_params():
    actions = load_fixture("single_one_params_actions.json")
    apis = [load_fixture("single_one_params_api.json")]
    result = generate_openapi_spec_for_actions(actions, apis)
    assert len(result["servers"]) == 1
    assert len(result["paths"]) == 1
    assert len(result["paths"][""]) == 1
    assert len(result["paths"][""]["post"]["schema"]) > 0
    assert len(result["paths"][""]["post"]["schema"]["properties"]) > 0
