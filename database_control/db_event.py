import sqlite3


def get_event_by_id(event_id):
    """Return id, event_type, event_name, date, time, location_id, comment from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()


def get_event_name(event_id):
    """Return event_name from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT event_name FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()[0]


def get_event_date(event_id):
    """Return date from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT date FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()[0]


def search_event_by_id(event_id):
    """Return id, event_type, event_name, date, time, location_id, comment from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()


def search_events_by_event_type(event_type):
    """Return (id, location_name, date, time) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT events.id, location_name, events.date, events.time FROM events "
                       "JOIN locations ON locations.id = events.location_id "
                       "WHERE event_type = ? ORDER BY date", (event_type,))
        return cursor.fetchall()


def search_event_by_date(date):
    """Return (id, event_type, event_name, time) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, event_type, event_name, time "
                       "FROM events WHERE date LIKE ? ORDER BY time", (date,))
        return cursor.fetchall()


def event_datetime_exists(date, time) -> bool:
    """Return True if date and time exists in the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM events WHERE date = ? AND time = ?", (date, time))
        return bool(cursor.fetchone())


def get_all_locations():
    """Return all (id, location_name, url) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM locations ORDER BY location_name")
        return cursor.fetchall()


def search_location_by_id(location_id):
    """Return id, location_name, url from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
        return cursor.fetchone()


def location_url_exists(url):
    """Return True if a location exists."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM locations WHERE url = ?", (url,))
        return bool(cursor.fetchone())


def location_name_exists(location_name):
    """Return True if a location exists."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (location_name,))
        return bool(cursor.fetchone())


# INSERT

def add_event(event_type, event_name, date, time, location_id):
    """Add new event into the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO events (event_type, event_name, date, time, location_id) VALUES (?, ?, ?, ?, ?)",
                       (event_type, event_name, date, time, location_id))
        cursor.execute("SELECT id FROM events WHERE date = ? AND time = ?", (date, time,))
        return cursor.fetchone()[0]


def add_location(location_name, url):
    """Add new location into the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO locations (location_name, url) VALUES (?, ?)", (location_name, url))
        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (location_name,))
        return cursor.fetchone()[0]


def add_song_to_concert(concert_id: int, song_id: int):
    """Add song to the events_songs."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events_songs WHERE event_id = ? and song_id = ?", (concert_id, song_id))
        if cursor.fetchall():
            return False

        cursor.execute("INSERT INTO events_songs VALUES (?, ?)", (concert_id, song_id))
        return True


# UPDATE

def edit_event_name(event_id, event_name):
    """Edit event_name by event _id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET event_name = ? WHERE id = ?", (event_name, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_event_datetime(event_id: int, date, time):
    """Edit date and time by event id and Return bool to confirm changes"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET date = ?, time = ? WHERE id = ?", (date, time, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


# DELETE

def delete_event_by_id(event_id: int):
    """DELETE event by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))


def delete_location_by_id(location_id: int):
    """DELETE location by id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM location WHERE id = ?", (location_id,))


def delete_song_from_concert(concert_id: int, song_id: int):
    """DELETE songs from events_songs."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM events_songs WHERE concert_id = ? and song_id = ?", (concert_id, song_id))
