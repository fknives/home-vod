from .db import get_db
from .data_models import Session
import time

_DELETE_EXPIRED_SESSION_SQL = "DELETE FROM session where refresh_expires_at <= :time"
def _delete_expired_tokens(db):
    db_cursor = db.cursor()
    db_cursor.execute(_DELETE_EXPIRED_SESSION_SQL, {"time": time.time()})
    db.commit()

_GET_USER_FOR_ACCESS_TOKEN_SQL = "SELECT user_id FROM session where access_token = :token and access_expires_at >= :time"
def get_user_for_token(access_token: str):
    db = get_db()
    _delete_expired_tokens(db)
    db_cursor = db.cursor()
    db_cursor.execute(_GET_USER_FOR_ACCESS_TOKEN_SQL, {"token": access_token, "time": time.time()})
    rows = db_cursor.fetchall()
    
    if (len(rows) == 1):
        return rows[0][0]
    return None

_GET_USER_FOR_MEDIA_TOKEN_SQL = "SELECT user_id FROM session where media_token = :token and access_expires_at >= :time"
def get_user_for_media_token(media_token: str):
    db = get_db()
    _delete_expired_tokens(db)
    db_cursor = db.cursor()
    db_cursor.execute(_GET_USER_FOR_MEDIA_TOKEN_SQL, {"token": media_token, "time": time.time()})
    rows = db_cursor.fetchall()
    
    if (len(rows) == 1):
        return rows[0][0]
    return None

_INSER_SESSION_SQL = "INSERT INTO session(user_id, access_token, media_token, refresh_token, access_expires_at, refresh_expires_at)"\
"VALUES(:user_id, :access_token, :media_token, :refresh_token, :access_expires_at, :refresh_expires_at)"

def _session_insert(db_cursor, session: Session):
    params = {
        "user_id": session.user_id,
        "access_token": session.access_token,
        "media_token": session.media_token,
        "refresh_token": session.refresh_token,
        "access_expires_at": session.access_expires_at,
        "refresh_expires_at": session.refresh_expires_at,
    }
    db_cursor.execute(_INSER_SESSION_SQL, params)

def insert_user_session(session: Session):
    db = get_db()
    db_cursor = db.cursor()
    _session_insert(db_cursor, session)
    db.commit()

def delete_user_session(access_token: str):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM session WHERE access_token = :token", {"token": access_token})
    db.commit()

def delete_all_user_session_by_user_id(user_id: int):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM session WHERE user_id = :id", {"id": user_id})
    db.commit()

def create_new_single_session(session: Session):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM session where user_id = :id", {"id": session.user_id})
    _session_insert(db_cursor, session)
    db.commit()

def get_user_for_refresh_token(refresh_token: str):
    db = get_db()
    _delete_expired_tokens(db)
    db_cursor = db.cursor()
    db_cursor.execute("SELECT user_id FROM session where refresh_token = :token", {"token": refresh_token})
    rows = db_cursor.fetchall()
    
    if (len(rows) == 1):
        return rows[0][0]
    return None

def swap_refresh_session(refresh_token: str, session: Session):
    db = get_db()
    _delete_expired_tokens(db)
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM session WHERE refresh_token = :token", {"token": refresh_token})
    _session_insert(db_cursor, session)
    db.commit()