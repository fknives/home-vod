import sqlite3
import sys

def migration_0_to_1(db_path: str):
    db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    db_cursor = db.cursor()
    db_cursor.execute("ALTER TABLE session ADD media_token TEXT NOT NULL;")
    db.commit()
    db.close()

if __name__ == "__main__":
    print(sys.argv[1])
    #migration_0_to_1(sys.argv[1])