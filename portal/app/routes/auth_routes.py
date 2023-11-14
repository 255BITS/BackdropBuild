from flask import Blueprint, Flask, render_template, redirect, request, url_for, flash, make_response
from app.services.auth_service import validate_password, create_user, login_user, logout_user, UserExistsError
auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/logout')
def login():
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

    try:
        user = create_user(email, password)
    except UserExistsError as e:
        flash(str(e), 'error')
        return redirect(url_for('auth.signup'))

    flash('Your account has been created. Welcome!', 'info')
    login_user(user)
    return redirect(url_for('dashboard'))
