from flask import Blueprint, Flask, render_template, redirect, request, url_for, flash, make_response, g
from app.services.auth_service import validate_password, authenticate_user, create_user, load_current_user, login_user, logout_user, AuthError
auth_bp = Blueprint('auth', __name__)

@auth_bp.get('/login')
def login():
    return render_template('login.html')

@auth_bp.post('/login')
def post_login():
    form = request.form
    email = form.get('email')
    password = form.get('password')
    user = authenticate_user(email, password)
    login_user(user)
    return redirect("dashboard")

@auth_bp.post('/logout')
def logout():
    logout_user()
    response = make_response("", 200)
    response.headers['HX-Redirect'] = '/'
    return response

@auth_bp.get('/signup')
def signup():
    return render_template('signup.html')

@auth_bp.post('/signup')
def post_signup():
    form = request.form
    email = form.get('email')
    password = form.get('password')
    password_confirmation = form.get('password-confirm')
    if password != password_confirmation:
        flash('Invalid password', 'error')
        return redirect(url_for('auth.signup'))

    if not validate_password(password):
        flash('Invalid password', 'error')
        return redirect(url_for('auth.signup'))

    user = create_user(email, password)

    flash('Your account has been created. Welcome!', 'success')
    login_user(user)
    return redirect(url_for('actions.dashboard'))

@auth_bp.before_app_request
def load_current():
    g.current_user = load_current_user()

@auth_bp.app_context_processor
def inject_globals():
    return dict(current_user=g.get('current_user', None))
