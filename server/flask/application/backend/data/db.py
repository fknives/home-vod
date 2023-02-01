import sqlite3
from os import path
import argparse
from flask import current_app, g
from passlib.hash import sha256_crypt

default_database_name = "sqlitedb"

def get_db():
    current_app.config.get('DATABASE_PATH')
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH')
        if (db_path is None):
            db_path = path.join(current_app.instance_path, current_app.config['DATABASE_NAME'])
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db(db_path = None, schema_path = None):
    if db_path is None:
        db = get_db()
    else:
        db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    if schema_path is None:
        with current_app.open_resource('data/schema.sql') as f:
            script = f.read().decode('UTF-8')
    else:
        with open(schema_path, "r") as f:
            script = f.read()

    db.executescript(script)
    db.commit()
    db.close()

def init_app(app):
	app.teardown_appcontext(close_db)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DB Init ArgumentParser", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-u", "--username", type=str, help="username of adming user", required=True)
    parser.add_argument("-p", "--password", type=str, help="password of adming user", required=True)
    parser.add_argument("-s", "--otp-secret", type=str, help="otp secret of admin user, python pyotp.random_base32()", required=False)
    args = parser.parse_args()
    config = vars(args)
    username = config['username']
    password = config['password']
    otp_secret = config['otp_secret']
    if (otp_secret is None):
        import pyotp
        otp_secret = pyotp.random_base32()

    db_path = path.join('/server/instance/', default_database_name)
    if path.exists(db_path):
        print('Database already exists at {}. Will NOT override, if necessary first delete first then restart initialization!'.format(db_path))
        exit(1)
    schema_path = path.join(path.dirname(__file__), 'schema.sql')
    init_db(db_path = db_path, schema_path = schema_path)
    db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    db_cursor = db.cursor()

    hashed_password = sha256_crypt.hash(password)
    sql = "INSERT INTO user(username, password, otp_secret, privileged, was_otp_verified)"\
    "VALUES(:name, :pass, :otp, :privileged, :otp_verified)"
    params = {
        "name": username,
        "pass": hashed_password,
        "otp": otp_secret,
        "privileged": True,
        "otp_verified": False,
    }
    db_cursor.execute(sql, params)
    db.commit()
    db.close()