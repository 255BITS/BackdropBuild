from flask import Flask, render_template, redirect, request, jsonify, url_for, flash
import re
from app import create_app

app = create_app()

@app.route('/')
def home():
    return render_template('landing.html', count_apis=123)

@app.route('/actions/<id>/link_api')
def actions_link_api(id):
    apis = [
        {
            "value": "api1",
            "description": "Get last message from queue",
            "author": "apiauthor1",
            "name": "AWS SNS",
            "id": "1",
            "method": "GET"
        },
        {
            "value": "api2",
            "description": "POST message to queue",
            "name": "AWS SNS",
            "author": "apiauthor1",
            "id": "2",
            "method": "POST"
        }
    ]
    return render_template('actions_link_api.html', apis=apis, id=id)

@app.route('/actions/<id>/link_api/<api_id>/new')
def actions_link_api_new(id, api_id):
    api = {
            "default_name": "apiCall",
            "fields": [
                {
                    "api key": "credential",
                    "bucket": "string",
                    "message": "string"
                 }
            ],
    }
    return render_template('actions_link_api_new.html', api=api)

@app.route('/api/options')
def actions_link_api_options():
    return render_template('actions_link_api_options.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10002)
