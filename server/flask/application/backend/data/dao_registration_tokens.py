from .db import get_db
from .data_models import DataError
from sqlite3 import IntegrityError

def is_valid_token(token):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT COUNT(*) FROM registration_token where token = :token", {"token": token})
    rows = db_cursor.fetchone()
    
    return rows[0] == 1

def insert_token(token):
    db = get_db()
    db_cursor = db.cursor()
    try:
        db_cursor.execute("INSERT INTO registration_token(token) VALUES(:token)", {"token": token})
    except IntegrityError as e:
        return DataError.REGISTRATION_CODE_ALREADY_EXISTS
    db.commit()
    
def delete_token(token):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM registration_token WHERE token=:token", {"token": token})
    db.commit()

def get_tokens():
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM registration_token")
    rows = db_cursor.fetchall()
    
    return list(map(lambda row: row['token'],rows))