import bcrypt


def hash_password(password) -> str:
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash


def check_password(password, user_password) -> bool:
    # bytes = password.encode('utf-8')
    # salt = bcrypt.gensalt()
    # hash = bcrypt.hashpw(bytes, salt)
    user_password_bcrypt = user_password.encode('utf-8')
    result = bcrypt.chechpw(user_password_bcrypt, password)
    return result
