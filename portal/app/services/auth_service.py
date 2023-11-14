from passlib.hash import bcrypt
from shared.couch import db
from flask import session

class AuthError(ValueError):
    pass

class InvalidPasswordError(AuthError):
    pass

class UserExistsError(AuthError):
    pass

class UserNotFoundError(AuthError):
    pass

def authenticate_user(email, password):
    user = db.get_user_by_email(email)
    if user is None:
        raise UserNotFoundError("This user does not exist.")
    if not bcrypt.verify(password, user["password_hash"]):
        raise InvalidPasswordError("Invalid Password.")
    return user

def create_user(email, password):
    if db.get_user_by_email(email):
        raise UserExistsError("This user already exists.")
    password_hash = bcrypt.hash(password)
    new_user = db.save({
        "password_hash": password_hash,
        "email": email,
        "verified": False,
        "type": "user"
    })
    return new_user

def load_current_user():
    if 'user_id' in session:
        return db.get(session['user_id'])
    return None

def login_user(user):
    session["user_id"] = user["_id"]

def logout_user():
    del session["user_id"]

def validate_password(password):
    #TODO check for good enough password
    return True
