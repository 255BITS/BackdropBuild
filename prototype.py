from flask import Flask, render_template, flash, request, redirect, url_for
from auth_service import validate_password, create_user, UserExistsError
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", 'development')

@app.route('/')
def home():
    return render_template('landing.html', count_apis=123)

@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.post('/signup')
def post_signup():
    form = request.form
    email = form.get('email')
    password = form.get('password')
    password_confirmation = form.get('password_confirmation')
    if password != password_confirmation:
        flash('Invalid password', 'error')
        return redirect(url_for('signup'))

    if not validate_password(password):
        flash('Invalid password', 'error')
        return redirect(url_for('signup'))

    try:
        user = create_user(email, password)
    except UserExistsError as e:
        flash(str(e), 'error')
        return redirect(url_for('course.index'))

    flash('Your account has been created. Welcome!', 'error')
    return redirect(url_for('dashboard'))


@app.get('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/discover-apis')
def apis_discover():
    return render_template('api_discover.html')

@app.route('/apis')
def apis_my():
    return render_template('api_list.html')

@app.route('/apis/new')
def apis_new():
    return render_template('api_new.html')

@app.route('/apis/<id>')
def apis_show(id):
    return render_template('api_show.html')

@app.route('/apis/<id>/usage')
def apis_show_usage(id):
    return render_template('api_usage.html')

@app.route('/actions/new')
def actions_create():
    return render_template('actions_create.html')

@app.route('/actions/<id>')
def actions_show(id):
    return render_template('actions_show.html', actions=["Action 1", "Action 2"], auths=[{"type": "Basic", "value":"b#gv7IiKP#bj9lXO", "value_encoded": "**************"}])

@app.route('/actions/<id>/edit')
def actions_edit(id):
    return render_template('actions_show.html', actions=[])

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
