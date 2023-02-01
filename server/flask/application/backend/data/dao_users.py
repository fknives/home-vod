from .data_models import User
from .data_models import RegisteringUser
from .data_models import DataError
from .db import get_db
from sqlite3 import IntegrityError
from passlib.hash import sha256_crypt

def _user_from_row(row):
    return User(
        id = row['id'],
        name = row['username'],
        otp_secret = row['otp_secret'],
        was_otp_verified = row['was_otp_verified'] != 0,
        privileged = row['privileged'] != 0,
    )

def get_user_by_id(user_id: int):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM user where id = :user_id", {"user_id": user_id})
    row = db_cursor.fetchone()
    
    if (row is None):
        return None

    return _user_from_row(row)

def get_user_by_name(username: str):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM user where username = :name", {"name": username})
    row = db_cursor.fetchone()
    
    if (row is None):
        return None

    return _user_from_row(row)

def get_user_by_name_and_password(user_name: str, password: str):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM user where username = :user_name", {"user_name": user_name})
    row = db_cursor.fetchone()

    if (row is None):
        sha256_crypt.hash('') # do hashing even if no user is found
        return None

    is_password_wrong = not sha256_crypt.verify(password, row['password'] or '')
    if is_password_wrong:
        return None

    return _user_from_row(row)

def get_users():
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM user")
    rows = db_cursor.fetchall()

    return map(_user_from_row, rows)

_INSER_USER_SQL = "INSERT INTO user(username, password, otp_secret, privileged, was_otp_verified)"\
"VALUES(:name, :pass, :otp, :privileged, :otp_verified)"
def insert_user(user: RegisteringUser):
    db = get_db()
    db_cursor = db.cursor()
    hashed_password = sha256_crypt.hash(user.password)

    params = {
        "name": user.name,
        "pass": hashed_password,
        "otp": user.otp_secret,
        "privileged": 1 if user.privileged else 0,
        "otp_verified": 1 if user.was_otp_verified else 0,
    }
    try:
        db_cursor.execute(_INSER_USER_SQL, params)
    except IntegrityError as e:
        return DataError.USER_NAME_NOT_VALID
    db.commit()
    return db_cursor.lastrowid

def update_user_privilige(user_id: int, privileged: bool):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute('UPDATE user SET privileged = :privileged WHERE id=:id',{'id':user_id, 'privileged': privileged})
    db.commit()

def update_user_otp_verification(user_id: int, was_otp_verified: bool):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute('UPDATE user SET was_otp_verified = :otp_verified WHERE id=:id',{'id':user_id, 'otp_verified': was_otp_verified})
    db.commit()

def update_user_password(user_id: int, new_password: str):
    hashed_password = sha256_crypt.hash(new_password)
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute('UPDATE user SET password = :pass WHERE id=:id',{'id':user_id, 'pass': hashed_password})
    db.commit()

def delete_user_by_id(user_id: int):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute('DELETE FROM user WHERE id=:id',{'id':user_id})
    db.commit()
