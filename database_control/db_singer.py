import sqlite3

"""
Add/edit/delete singers, set admins right.
Set voices, songs, events, places, clothes.
Receive singer attendance.
"""


# SELECT

def singer_exists(singer_id: int) -> bool:
    """Return False if the singer is not in the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM singers WHERE singer_id = ?", (singer_id,))
        return bool(cursor.fetchone())


def get_singer_id(singer_id: int):
    """Return the singer id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM singers WHERE singer_id = ?", (singer_id,))
        return cursor.fetchone()[0]


def is_admin(singer_id: int):
    """Check if the singer is admin of the bot."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM admins JOIN singers ON singers.id = admins.singer_id "
                       "WHERE singers.singer_id = ?", (singer_id,))
    return bool(cursor.fetchone())


def count_singers():
    """Count all singers from database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) from `singers`")
        return cursor.fetchone()[0]


def get_singer_telegram_name(_id: int):
    """Return the (telegram username) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT telegram_name FROM singers WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_singer_fullname(_id: int):
    """Return the singer (firstname lastname) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT first_name || ' ' || last_name AS fullname "
                       "FROM singers WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_singer_voices(_id: int):
    """Return the singer (id, voices) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, voice FROM voices "
                       "INNER JOIN singer_voice ON singer_voice.voice_id = voices.id "
                       "WHERE singer_voice.singer_id = ? ORDER BY singer_voice.voice_id", (_id,))
        return cursor.fetchall()


def get_singer_suits(_id: int):
    """Return the singer (id, suits, photo) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, suit, image FROM suits "
                       "INNER JOIN singer_suit ON singer_suit.suit_id = suits.id "
                       "WHERE singer_suit.singer_id = ?", (_id,))
        return cursor.fetchall()


def get_all_suits():
    """Return all (id, suits, photos) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM suits ")
        return cursor.fetchall()


def get_all_voices():
    """Return all (id, voice) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM voices ")
        return cursor.fetchall()


def get_all_singers():
    """Return (firstname lastname, id) of the all singers from database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT first_name || ' ' || last_name AS fullname, id "
                       "FROM singers ORDER BY first_name")
        return cursor.fetchall()


def get_all_admins():
    """Return (singer_id) for each admin from database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT singers.singer_id FROM singers "
                       "JOIN admins ON admins.singer_id = singers.id ")
        return cursor.fetchall()


def get_voice_list():
    """Return all available voices from database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT voice FROM voices")
        return cursor.fetchall()


def search_singer_voice(singer_id: int):
    """Return all singer voices from database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT GROUP_CONCAT(voices.voice, ', ') FROM singers "
                       "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                       "JOIN voices ON voices.id = singer_voice.voice_id "
                       "WHERE singers.singer_id = ? ORDER BY singer_voice.voice_id", (singer_id,))
        return cursor.fetchall()


def search_singers_by_voice(voice: str):
    """Return (firstname lastname, id) of the singers of the chosen voice from database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT singers.first_name || ' ' || singers.last_name AS fullname, singers.id "
                       "FROM singers "
                       "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                       "JOIN voices ON voices.id = singer_voice.voice_id "
                       "WHERE voices.voice = ?", (voice,))
        return cursor.fetchall()


def search_singer_by_name(msg: str):
    """Return singers (telegram username, firstname, lastname) from database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT telegram_name, first_name, last_name "
                       "FROM singers WHERE first_name LIKE ?", (msg,))
        return cursor.fetchall()


# INSERT

def add_singer(singer_id: int, telegram_name: str, first_name=None, last_name=None):
    """Add new singer into the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singers (singer_id, telegram_name, first_name, last_name) VALUES (?, ?, ?, ?)",
                       (singer_id, telegram_name, first_name, last_name))


def add_suit(_id: int, suit_id: int):
    """Add suit for the singer into database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singer_suit VALUES (?, ?)", (_id, suit_id))


def add_voice(_id: int, voice_id: int):
    """Add voice for the singer into database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singer_voice VALUES (?, ?)", (_id, voice_id))


# UPDATE


# DELETE

def delete_suit(_id: int, suit_id: int):
    """Remove suit of the singer from database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM singer_suit WHERE singer_id = ? and suit_id = ?", (_id, suit_id))


def delete_voice(_id: int, voice_id: int):
    """Remove voice of the singer from database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM singer_voice WHERE singer_id = ? and voice_id = ?", (_id, voice_id))
