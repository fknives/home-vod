from .db import get_db
import time

_DELETE_EXPIRED_SESSION_SQL = "DELETE FROM reset_password_token where expires_at <= :time"
def _delete_expired_tokens(db):
    db_cursor = db.cursor()
    db_cursor.execute(_DELETE_EXPIRED_SESSION_SQL, {"time": time.time()})
    db.commit()

def is_valid_token(token, username):
    db = get_db()
    _delete_expired_tokens(db)
    db_cursor = db.cursor()
    db_cursor.execute("SELECT COUNT(*) FROM reset_password_token where token = :token AND username = :username", {"token": token, "username": username})
    rows = db_cursor.fetchone()
    
    return rows[0] == 1

def insert_token(token, username, expires_at):
    db = get_db()
    db_cursor = db.cursor()
    params = {
        "token": token,
        "username": username,
        "expires_at": expires_at
    }
    db_cursor.execute("INSERT INTO reset_password_token(token, username, expires_at) VALUES(:token, :username, :expires_at)", params)
    db.commit()
    
def delete_tokens(username):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM reset_password_token WHERE username=:username", {"username": username})
    db.commit()
