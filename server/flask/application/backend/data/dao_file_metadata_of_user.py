from .db import get_db
from .data_models import DataError
from sqlite3 import IntegrityError

_INSER_METADATA_SQL = "INSERT INTO file_metadata_of_user(user_id,file_key,metadata) "\
"VALUES(:user_id, :file_key, :metadata)"
_DELETE_METADATA_SQL = "DELETE FROM file_metadata_of_user WHERE user_id=:user_id AND file_key=:file_key"
def insert_metadata(user_id: str, metadata: dict):
    db = get_db()
    db_cursor = db.cursor()

    delete_params = map(lambda key: {'user_id':user_id, 'file_key':key}, metadata.keys())
    delete_params = list(delete_params)
    db_cursor.executemany(_DELETE_METADATA_SQL, delete_params)
    
    insert_params = map(lambda item: {'user_id':user_id, 'file_key':item[0], 'metadata':item[1]}, metadata.items())
    insert_params = list(insert_params)


    db_cursor.executemany(_INSER_METADATA_SQL, insert_params)
    db.commit()

def get_metadata(user_id: str):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT file_key, metadata FROM file_metadata_of_user WHERE user_id=:user_id",{"user_id":user_id})
    rows = db_cursor.fetchall()

    converted_tuple_array = map(lambda row: (row['file_key'], row['metadata']), rows)
    return dict(converted_tuple_array)