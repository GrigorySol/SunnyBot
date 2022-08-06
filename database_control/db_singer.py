import sqlite3
from config import BOT_DB

"""
Add/edit/delete singers, set admins right.
Set voices, songs, events, places, clothes.
Receive singer attendance.
"""


# SELECT

def singer_exists(telegram_id) -> bool:
    """Return True if the telegram_id is in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM singers WHERE telegram_id = ?", (telegram_id,))
        return bool(cursor.fetchone())


def singer_exists_by_id(singer_id) -> bool:
    """Return True if id is in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT telegram_id FROM singers WHERE id = ?", (singer_id,))
        return bool(cursor.fetchone())


def get_singer_id(telegram_id):
    """Return id of a singer from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM singers WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()[0]


def get_singer_info(telegram_id):
    """Return id, join_date, telegram_name, first_name, last_name, comment of a singer from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, join_date, telegram_name, first_name, last_name, comment "
                       "FROM singers WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()


def is_admin(telegram_id) -> bool:
    """Check if the singer is admin of the bot."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT * FROM admins JOIN singers ON singers.id = admins.singer_id "
                       "WHERE singers.telegram_id = ?", (telegram_id,))
    return bool(cursor.fetchone())


def count_singers():
    """Count all singers from the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT COUNT (*) from `singers`")
        return cursor.fetchone()[0]


def get_all_singers():
    """Return (firstname lastname, id) of the all singers from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT first_name || ' ' || last_name AS fullname, id "
                       "FROM singers "
                       "ORDER BY first_name")
        return cursor.fetchall()


def get_all_admins():
    """Return (telegram_id) for each admin from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.telegram_id FROM singers "
                       "JOIN admins ON admins.singer_id = singers.id")
        return cursor.fetchall()


def get_admins_fullname_singer_id():
    """Return (fullname, singer_id) for each admin from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.id FROM singers "
                       "JOIN admins ON admins.singer_id = singers.id")
        return cursor.fetchall()


def get_all_non_admins():
    """Return (fullname, singer_id) of singers that doesn't have admin rights."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT first_name || ' ' || last_name AS fullname, id "
                       "FROM singers EXCEPT "
                       "SELECT singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.id FROM singers "
                       "JOIN admins ON admins.singer_id = singers.id "
                       "ORDER BY fullname")
        return cursor.fetchall()


def get_singers_id_by_event(event_id):
    """Return (telegram_id, attend) from singers for event_id from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.telegram_id, attendance.attend FROM singers "
                       "JOIN attendance ON attendance.singer_id = singers.id "
                       "WHERE attendance.event_id = ? AND attendance.attend IS NOT '0'", (event_id,))
        return cursor.fetchall()


def get_singer_telegram_name(singer_id):
    """Return (telegram username) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT telegram_name FROM singers WHERE id = ?", (singer_id,))
        return cursor.fetchone()[0]


def get_singer_fullname(singer_id):
    """Return (firstname lastname) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT first_name || ' ' || last_name AS fullname "
                       "FROM singers WHERE id = ?", (singer_id,))
        return cursor.fetchone()[0]


def get_singer_join_date(singer_id):
    """Return singer's join_date from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT join_date FROM singers WHERE id = ?", (singer_id,))
        return cursor.fetchone()[0]


def get_singer_voices(singer_id):
    """Return (voice_id, voice) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT id, voice FROM voices "
                       "JOIN singer_voice ON singer_voice.voice_id = voices.id "
                       "WHERE singer_voice.singer_id = ? ORDER BY singer_voice.voice_id", (singer_id,))
        return cursor.fetchall()


def get_singer_voice_id(singer_id):
    """Return voice_id from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT voice_id FROM singer_voice "
                       "WHERE singer_id = ? ORDER BY voice_id", (singer_id,))
        return cursor.fetchall()


def get_singer_suits(singer_id):
    """Return the singer (id, suit_name) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT id, suit_name FROM suits "
                       "JOIN singer_suit ON singer_suit.suit_id = suits.id "
                       "WHERE singer_suit.singer_id = ?", (singer_id,))
        return cursor.fetchall()


def get_available_suits(singer_id):
    """Return all (id, suit_name) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, suit_name FROM suits EXCEPT "
                       "SELECT id, suit_name FROM suits "
                       "JOIN singer_suit ON singer_suit.suit_id = suits.id "
                       "WHERE singer_suit.singer_id = ?", (singer_id,))
        return cursor.fetchall()


def get_singer_comment(singer_id):
    """Return comment about a singer from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT comment FROM singers WHERE id = ?", (singer_id,))
        return cursor.fetchone()[0]


def get_all_suits():
    """Return all (id, suit_name, photo) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM suits")
        return cursor.fetchall()


def get_suits_and_amount():
    """Return all (id, suit_name, photo, amount) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT suits.id, suits.suit_name, suits.photo, "
                       "(SELECT COUNT(singer_suit.singer_id) FROM singer_suit "
                       "WHERE singer_suit.suit_id = suits.id) "
                       "FROM suits")
        return cursor.fetchall()


def search_suits_by_id(suit_id):
    """Return (suit_name, photo) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT suit_name, photo FROM suits WHERE id = ?", (suit_id,))
        return cursor.fetchone()


def suit_name_exists(suit_name):
    """Check if the suit_name exists in the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM suits WHERE suit_name = ?", (suit_name,))
        return bool(cursor.fetchone())


def get_all_voices():
    """Return all (id, voice) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM voices ")
        return cursor.fetchall()


def search_singers_by_voice(voice: str):
    """Return (firstname lastname, id) of the singers of the chosen voice from the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.first_name || ' ' || singers.last_name AS fullname, singers.id "
                       "FROM singers "
                       "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                       "JOIN voices ON voices.id = singer_voice.voice_id "
                       "WHERE voices.voice = ?", (voice,))
        return cursor.fetchall()


def search_singer_by_name(msg: str):
    """Return singers (telegram username, firstname, lastname) from the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT telegram_name, first_name, last_name "
                       "FROM singers WHERE first_name LIKE ?", (msg,))
        return cursor.fetchall()


def get_all_blocked_users():
    """Return blocked users (telegram_id, telegram_name) from the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM black_list")
        return cursor.fetchall()


def is_blocked(telegram_id) -> bool:
    """Check if the user is blocked."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM black_list WHERE telegram_id = ?", (telegram_id,))
    return bool(cursor.fetchone())


# INSERT

def block_user(telegram_id, telegram_name: str):
    """Add user id and telegram name in black list in the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO black_list VALUES (?, ?)", (telegram_id, telegram_name))


def add_singer(telegram_id, telegram_name: str, first_name: str = None, last_name: str = None):
    """Add new singer into the database"""
    print(f"{telegram_id} {telegram_name} {first_name} {last_name}")
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singers (telegram_id, telegram_name, first_name, last_name) VALUES (?, ?, ?, ?)",
                       (telegram_id, telegram_name, first_name, last_name))


def add_admin(telegram_id):
    """Add singer to admins in the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO admins (singer_id) SELECT singers.id FROM singers "
                       "WHERE singers.telegram_id = ?", (telegram_id,))


def add_admin_by_singer_id(singer_id):
    """Add singer to admins in the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO admins (singer_id) VALUES (?)", (singer_id,))


def add_suit(suit_name: str, photo: str):
    """Add new suit into the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO suits (suit_name, photo) VALUES (?, ?)", (suit_name, photo))


def add_singer_suit(singer_id, suit_id):
    """Add suit for the singer into database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singer_suit VALUES (?, ?)", (singer_id, suit_id))


def add_singer_voice(singer_id, voice_id):
    """Add voice for the singer into database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO singer_voice VALUES (?, ?)", (singer_id, voice_id))


# UPDATE

def edit_singer_comment(singer_id, comment):
    """Edit comment by singer_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE singers SET comment = ? WHERE id = ?", (comment, singer_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_singer_name(singer_id, first_name, last_name):
    """Edit first and last name by singer_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE singers SET first_name = ?, last_name = ? "
                           "WHERE id = ?", (first_name, last_name, singer_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_suit_name(suit_id, suit_name):
    """Edit suit_name by suit_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE suits SET suit_name = ? WHERE id = ?", (suit_name, suit_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_suit_photo(suit_id, photo):
    """Edit photo by suit_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE suits SET photo = ? WHERE id = ?", (photo, suit_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


# DELETE

def remove_user_from_blacklist(telegram_id):
    """Remove a user from the black list"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM black_list WHERE telegram_id = ?", (telegram_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def delete_singer(singer_id):
    """DELETE singer by id from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM singers WHERE id = ?", (singer_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def remove_admin(singer_id):
    """REMOVE singer by singer_id from admins"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("DELETE FROM admins WHERE singer_id = ?", (singer_id,))


def delete_suit(suit_id):
    """DELETE suit from the database"""

    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM suits WHERE id = ?", (suit_id,))


def remove_suit(singer_id, suit_id):
    """Remove singer's suit"""

    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM singer_suit WHERE singer_id = ? and suit_id = ?", (singer_id, suit_id))


def remove_singer_from_voice(singer_id, voice_id):
    """Remove singer from voice"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM singer_voice WHERE singer_id = ? and voice_id = ?", (singer_id, voice_id))
