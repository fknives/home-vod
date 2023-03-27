DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS registration_token;
DROP TABLE IF EXISTS reset_password_token;
DROP TABLE IF EXISTS session;
DROP TABLE IF EXISTS file_metadata_of_user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  otp_secret TEXT NOT NULL,
  privileged INTEGER NOT NULL,
  was_otp_verified INTEGER NOT NULL
);

CREATE TABLE registration_token (
  token TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE reset_password_token (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token TEXT NOT NULL,
  username TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);

CREATE TABLE session (
  user_id INTEGER NOT NULL,
  access_token TEXT NOT NULL,
  media_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  access_expires_at INTEGER NOT NULL,
  refresh_expires_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE file_metadata_of_user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  file_key TEXT NOT NULL,
  metadata TEXT NOT NULL
);

CREATE TABLE file_metadata (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_key TEXT NOT NULL,
  metadata TEXT NOT NULL
);