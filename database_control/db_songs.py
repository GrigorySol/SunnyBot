import sqlite3


def get_all_songs():
    """Return all (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM songs ORDER BY song_name")
        return cursor.fetchall()


def get_song_name(_id):
    """Return the song_name from the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT song_name FROM songs WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_songs_in_work(event_type: int, start_date, end_date):
    """Return songs (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT DISTINCT id, song_name, comment FROM songs "
                       "JOIN event_song ON event_song.song_id = songs.id "
                       "WHERE event_song.event_id IN "
                       "(SELECT id FROM events WHERE events.event_type = ? AND events.date BETWEEN ? AND ?) "
                       "ORDER BY song_name", (event_type, start_date, end_date))
        return cursor.fetchall()


def get_songs_by_event_id(event_id):
    """Return songs (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, song_name, comment FROM songs "
                       "JOIN event_song ON event_song.song_id = songs.id "
                       "WHERE event_song.event_id = ? ORDER BY song_name", (event_id,))
        return cursor.fetchall()


def song_exists(song_id):
    """Check if the song exists in the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT song_name FROM songs WHERE id = ?", (song_id,))
        return bool(cursor.fetchone())


def song_name_exists(song_name):
    """Check if the song_name exists in the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM songs WHERE song_name = ?", (song_name,))
        return bool(cursor.fetchone())


def get_sound_by_song_id(song_id):
    """Return (id, song_id, voice_id, file_id) for each SOUND for the song from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM sound WHERE song_id = ?", (song_id,))
        return cursor.fetchall()


def get_sheets_by_song_id(song_id):
    """Return (id, song_id, voice_id, file_id) for each SHEETS for the song from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM sheets WHERE song_id = ?", (song_id,))
        return cursor.fetchall()


def get_sound_by_voice_id(voice_id):
    """Return (id, song_id, voice_id, file_id) for each SOUND for the song from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM sound WHERE voice_id = ?", (voice_id,))
        return cursor.fetchall()


def get_sheets_by_voice_id(voice_id):
    """Return (id, song_id, voice_id, file_id) for each SHEETS for the song from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM sheets WHERE voice_id = ?", (voice_id,))
        return cursor.fetchall()


# INSERT

def add_song(song_name):
    """Add new song into the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO songs (song_name) VALUES (?)", (song_name,))
        cursor.execute("SELECT id FROM songs WHERE song_name = ?", (song_name,))
        return cursor.fetchone()[0]


def add_sound(song_id: int, voice_id: int, file_id):
    """Add SOUND for the song into the database and Return id"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO sound (song_id, voice_id, file_id) VALUES (?, ?, ?)",
                       (song_id, voice_id, file_id))
        cursor.execute("SELECT id FROM sound WHERE file_id = ?", (file_id,))
        return cursor.fetchone()[0]


def add_sheets(song_id: int, voice_id: int, file_id):
    """Add SHEETS for the song into the database and Return id"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO sheets (song_id, voice_id, file_id) VALUES (?, ?, ?)",
                       (song_id, voice_id, file_id))
        cursor.execute("SELECT id FROM sheets WHERE file_id = ?", (file_id,))
        return cursor.fetchone()[0]


# UPDATE

def edit_song_name(song_id, song_name):
    """Edit song_name by song _id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE songs SET song_name = ? WHERE id = ?", (song_name, song_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_song_comment(song_id, comment):
    """Edit song comment by song _id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE songs SET comment = ? WHERE id = ?", (comment, song_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_sound_by_id(song_id, voice_id):
    """edit sound by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE sound SET voice_id = ? WHERE id = ?", (voice_id, song_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_sheets_by_id(song_id, voice_id):
    """Edit sheets by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE sheets SET voice_id = ? WHERE id = ?", (voice_id, song_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


# DELETE

def delete_song(song_id):
    """DELETE song by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def delete_sound_by_song_id(song_id):
    """DELETE all sound by song_id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM sound WHERE song_id = ?", (song_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def delete_sheets_by_song_id(song_id):
    """DELETE all sheets by song_id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM sheets WHERE song_id = ?", (song_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False
