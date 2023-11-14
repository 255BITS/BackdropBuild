import bcrypt

class UserExistsError(ValueError):
    pass

def create_user(email, password):
    if couch.get_user_by_email(email):
        raise UserExistsError("This user already exists.")
    password_hash = bcrypt.hash(password)
    #new_user = couch.save({
    #    "password_hash": password_hash,
    #    "email": email,
    #    #TODO username?
    #    "verified": False,
    #    "type": "user"
    #})
    #return new_user
    return None

def validate_password(password):
    #TODO check for good enough password
    return True
