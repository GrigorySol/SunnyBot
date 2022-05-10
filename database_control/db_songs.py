import sqlite3


def get_all_songs():
    """Return all (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM songs")
        return cursor.fetchall()


def get_song_name(_id):
    """Return the song_name from the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT song_name FROM songs WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_songs_in_work():
    """Return songs (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, song_name, comment FROM songs "
                       "JOIN current_songs ON current_songs.song_id = songs.id ")
        return cursor.fetchall()


def get_songs_by_event_id(event_id):
    """Return songs (id, song_name, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, song_name, comment FROM songs "
                       "JOIN events_songs ON events_songs.song_id = songs.id "
                       "WHERE events_songs.event_id =?", (event_id,))
        return cursor.fetchall()


def song_exists(_id):
    """Check if the song exists in the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT song_name FROM songs WHERE id = ?", (_id,))
        return bool(cursor.fetchone())


def song_name_exists(song_name):
    """Check if the song_name exists in the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM songs WHERE song_name = ?", (song_name,))
        return bool(cursor.fetchone())


def get_sounds_by_song_id(song_id):
    """Return (id, song_id, voice_id, file_id) for each SOUND for the song from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM sounds WHERE song_id = ?", (song_id,))
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

        cursor.execute("SELECT * FROM sounds WHERE voice_id = ?", (voice_id,))
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


def add_sound(song_id, voice_id, file_id):
    """Add SOUND for the song into the database and Return id"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO sounds (song_id, voice_id, file_id) VALUES (?, ?, ?)",
                       (song_id, voice_id, file_id))
        cursor.execute("SELECT id FROM sounds WHERE file_id = ?", (file_id,))
        return cursor.fetchone()[0]


def add_sheets(song_id, voice_id, file_id):
    """Add SHEETS for the song into the database and Return id"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO sheets (song_id, voice_id, file_id) VALUES (?, ?, ?)",
                       (song_id, voice_id, file_id))
        cursor.execute("SELECT id FROM sheets WHERE file_id = ?", (file_id,))
        return cursor.fetchone()[0]


# UPDATE

def edit_song_name(_id, song_name):
    """Edit song_name by song _id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE songs SET song_name = ? WHERE id = ?", (song_name, _id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_song_comment(_id, comment):
    """Edit song comment by song _id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE songs SET comment = ? WHERE id = ?", (comment, _id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_sound_by_id(_id, voice_id):
    """edit sound by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE sounds SET voice_id = ? WHERE id = ?", (voice_id, _id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_sheets_by_id(_id, voice_id):
    """Edit sheets by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE sheets SET voice_id = ? WHERE id = ?", (voice_id, _id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


# DELETE

def delete_song_by_id(_id):
    """DELETE song by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM songs WHERE id = ?", (_id,))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def delete_sounds_by_song_id(song_id):
    """DELETE all sounds by song_id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM sounds WHERE song_id = ?", (song_id,))
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
