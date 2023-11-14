from passlib.hash import bcrypt
from shared.couch import db

class UserExistsError(ValueError):
    pass

def create_user(email, password):
    if db.get_user_by_email(email):
        raise UserExistsError("This user already exists.")
    password_hash = bcrypt.hash(password)
    new_user = db.save({
        "password_hash": password_hash,
        "email": email,
        #TODO username?
        "verified": False,
        "type": "user"
    })
    return new_user

def validate_password(password):
    #TODO check for good enough password
    return True
