from .db import get_db
from .data_models import DataError
from sqlite3 import IntegrityError

_INSER_METADATA_SQL = "INSERT INTO file_metadata(file_key,metadata) "\
"VALUES(:file_key, :metadata)"
_DELETE_METADATA_SQL = "DELETE FROM file_metadata WHERE file_key=:file_key"
def insert_metadata(metadata: dict):
    db = get_db()
    db_cursor = db.cursor()

    delete_params = map(lambda key: {'file_key':key}, metadata.keys())
    delete_params = list(delete_params)
    db_cursor.executemany(_DELETE_METADATA_SQL, delete_params)
    
    insert_params = map(lambda item: {'file_key':item[0], 'metadata':item[1]}, metadata.items())
    insert_params = list(insert_params)


    db_cursor.executemany(_INSER_METADATA_SQL, insert_params)
    db.commit()

def get_metadata(file_key: str):
    db = get_db()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT metadata FROM file_metadata WHERE file_key=:file_key",{"file_key":file_key})
    rows = db_cursor.fetchone()

    if (rows is None):
        return dict()
    
    converted_tuple_array = map(lambda metadata: (file_key, metadata), rows)
    return dict(converted_tuple_array)