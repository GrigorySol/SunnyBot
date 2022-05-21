import sqlite3


def create_database():
    """Create database tables."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("CREATE TABLE singers "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "telegram_id INTEGER NOT NULL UNIQUE, "
                       "join_date DATETIME NOT NULL DEFAULT ((DATETIME('now'))), "
                       "telegram_name STRING UNIQUE NOT NULL, "
                       "first_name STRING, "
                       "last_name STRING, "
                       "comment STRING)")

        cursor.execute("CREATE TABLE admins "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "singer_id INTEGER REFERENCES singers (id) "
                       "ON DELETE CASCADE NOT NULL)")

        cursor.execute("CREATE TABLE black_list "
                       "(telegram_id INTEGER UNIQUE NOT NULL, "
                       "telegram_name STRING UNIQUE NOT NULL)")

        cursor.execute("CREATE TABLE voices "
                       "(id INTEGER PRIMARY KEY, "
                       "voice STRING NOT NULL UNIQUE)")

        cursor.execute("CREATE TABLE suits "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "suit_name STRING UNIQUE NOT NULL, "
                       "image STRING)")

        cursor.execute("CREATE TABLE songs "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "song_name STRING NOT NULL UNIQUE, "
                       "comment STRING)")

        cursor.execute("CREATE TABLE sheets "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "song_id INTEGER REFERENCES songs (id) ON DELETE CASCADE NOT NULL, "
                       "voice_id INTEGER REFERENCES voices (id) ON DELETE SET NULL, "
                       "file_id STRING UNIQUE NOT NULL)")

        cursor.execute("CREATE TABLE sounds "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "song_id INTEGER REFERENCES songs (id) ON DELETE CASCADE NOT NULL, "
                       "voice_id INTEGER REFERENCES voices (id) ON DELETE SET NULL, "
                       "file_id STRING UNIQUE NOT NULL)")

        cursor.execute("CREATE TABLE locations "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "location_name STRING NOT NULL UNIQUE, "
                       "url STRING UNIQUE NOT NULL)")

        cursor.execute("CREATE TABLE events "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "event_type INTEGER NOT NULL, "
                       "event_name STRING, "
                       "date DATE NOT NULL, "
                       "time TIME NOT NULL, "
                       "location_id INTEGER REFERENCES locations (id) ON DELETE CASCADE, "
                       "comment STRING)")

        cursor.execute("CREATE TABLE attendance "
                       "(event_id INTEGER REFERENCES events (id) ON DELETE CASCADE NOT NULL, "
                       "singer_id INTEGER NOT NULL REFERENCES singers (id) ON DELETE CASCADE, "
                       "attend INTEGER NOT NULL DEFAULT (2))")

        cursor.execute("CREATE TABLE events_suits "
                       "(event_id INTEGER REFERENCES events (id) ON DELETE CASCADE NOT NULL, "
                       "suit_id INTEGER REFERENCES suits (id) ON DELETE CASCADE NOT NULL)")

        cursor.execute("CREATE TABLE events_songs "
                       "(event_id INTEGER REFERENCES events (id) ON DELETE CASCADE NOT NULL, "
                       "song_id INTEGER REFERENCES songs (id) ON DELETE CASCADE NOT NULL)")

        cursor.execute("CREATE TABLE singers_suits "
                       "(singer_id INTEGER REFERENCES singers (id) ON DELETE CASCADE NOT NULL, "
                       "suit_id INTEGER REFERENCES suits (id) ON DELETE CASCADE NOT NULL)")

        cursor.execute("CREATE TABLE singers_voices "
                       "(singer_id INTEGER REFERENCES singers (id) ON DELETE CASCADE NOT NULL, "
                       "voice_id INTEGER REFERENCES voices (id) ON DELETE CASCADE NOT NULL)")
