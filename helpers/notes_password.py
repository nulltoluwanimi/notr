# import bcrypt

import hashlib
import binascii
import os

# def hash_password(password) -> str:
#     bytes = password.encode('utf-8')
#     salt = bcrypt.gensalt()
#     hash = bcrypt.hashpw(bytes, salt)
#     return hash


# def check_password(password, user_password) -> bool:
# bytes = password.encode('utf-8')
# salt = bcrypt.gensalt()
# hash = bcrypt.hashpw(bytes, salt)
# user_password_bcrypt = user_password.encode('utf-8')
# result = bcrypt.chechpw(user_password_bcrypt, password)
# return result


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                        salt, 100000)
    password_hash = binascii.hexlify(password_hash)
    return (salt+password_hash).decode('ascii')


def check_password(stored_password, user_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    password_hash = hashlib.pbkdf2_hmac('sha512', user_password.encode('utf-8'),
                                        salt.encode('ascii'),
                                        100000)
    password_hash = binascii.hexlify(password_hash).decode('ascii')
    return password_hash == stored_password
