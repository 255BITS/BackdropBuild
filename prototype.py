from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/action-set/new')
def action_set_create():
    return render_template('action_set_create.html')

@app.route('/action-set/<id>')
def action_set_show(id):
    return render_template('action_set_show.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10002)
