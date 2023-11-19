from app.services.swagger_service import generate_openapi_spec_for_actions

def test_generate_openapi_spec_empty():
    result = generate_openapi_spec_for_actions({
        "api_links": [],
        "name": "Empty"
    }, [])
    expected = {'openapi': '3.1.0', 'info': {'title': 'Empty', 'version': '1.0', 'description': ''}, 'servers': [{'url': 'https://gptactionhub.com', 'description': 'The hub for GPT actions'}], 'paths': {}, 'components': {'schemas': {}}}
    assert len(result["servers"]) == 1
    assert result["info"]["title"] == "Empty"
    assert len(result["paths"]) == 0
    assert len(result["components"]["schemas"]) == 0

