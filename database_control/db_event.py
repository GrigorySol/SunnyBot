import sqlite3
from config import BOT_DB


def get_event_by_id(event_id):
    """Return id, event_type, event_name, date, time, location_id, comment from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()


def get_event_name(event_id):
    """Return event_name from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT event_name FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()[0]


def get_event_date(event_id):
    """Return date from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT date FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()[0]


def get_suit_by_event_id(event_id):
    """Return suit_id, suit_name, photo from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT id, suit_name, photo FROM suits "
                       "JOIN event_suit ON event_suit.suit_id = suits.id "
                       "WHERE event_suit.event_id = ?", (event_id,))
        return cursor.fetchone()


def search_event_by_id(event_id):
    """Return id, event_type, event_name, date, time, location_id, comment from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone()


def search_future_events_by_event_type(event_type, current_date):
    """Return (id, location_name, date, time) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT events.id, location_name, events.date, events.time FROM events "
                       "JOIN locations ON locations.id = events.location_id "
                       "WHERE event_type = ? AND events.date >= ?"
                       "ORDER BY date", (event_type, current_date))
        return cursor.fetchall()


def search_event_by_date(date):
    """Return (id, event_type, event_name, time) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id, event_type, event_name, time "
                       "FROM events WHERE date LIKE ? ORDER BY time", (date,))
        return cursor.fetchall()


def search_events_by_date_interval(start_date, end_date, telegram_id):
    """Return (id, event_type, event_name, date, time) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT DISTINCT events.id, event_type, event_name, date, time FROM events "
                       "JOIN attendance ON attendance.event_id = events.id "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE singers.telegram_id = ? AND date BETWEEN ? AND ? "
                       "ORDER BY date", (telegram_id, start_date, end_date,))
        return cursor.fetchall()


def search_event_by_date_and_telegram_id(date, telegram_id):
    """Return (id, event_type, event_name, time) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT events.id, events.event_type, events.event_name, events.time FROM events "
                       "JOIN attendance ON attendance.event_id = events.id "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE date LIKE ? and singers.telegram_id = ? "
                       "ORDER BY time", (date, telegram_id))
        return cursor.fetchall()


def event_datetime_exists(date, time) -> bool:
    """Return True if date and time exists in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM events WHERE date = ? AND time = ?", (date, time))
        return bool(cursor.fetchone())


def get_all_locations():
    """Return all (id, location_name, url) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM locations ORDER BY location_name")
        return cursor.fetchall()


def search_location_by_id(location_id):
    """Return location_name, url from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT location_name, url FROM locations WHERE id = ?", (location_id,))
        return cursor.fetchone()


def search_location_by_event_id(event_id):
    """Return location_name, url from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT location_name, url FROM locations WHERE id = "
                       "(SELECT location_id FROM events WHERE id = ?)", (event_id,))
        return cursor.fetchone()


def location_url_exists(url):
    """Return True if a location exists."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM locations WHERE url = ?", (url,))
        return bool(cursor.fetchone())


def location_name_exists(location_name):
    """Return True if a location exists."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (location_name,))
        return bool(cursor.fetchone())


# INSERT

def add_event(event_type, event_name, date, time, location_id):
    """Add new event into the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO events (event_type, event_name, date, time, location_id) VALUES (?, ?, ?, ?, ?)",
                       (event_type, event_name, date, time, location_id))
        cursor.execute("SELECT id FROM events WHERE date = ? AND time = ?", (date, time,))
        return cursor.fetchone()[0]


def add_location(location_name, url):
    """Add new location into the database"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO locations (location_name, url) VALUES (?, ?)", (location_name, url))
        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (location_name,))
        return cursor.fetchone()[0]


def add_song_to_concert(concert_id, song_id):
    """Add event_is, song_id to the event_song."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM event_song WHERE event_id = ? and song_id = ?", (concert_id, song_id))
        if cursor.fetchall():
            return False

        cursor.execute("INSERT INTO event_song VALUES (?, ?)", (concert_id, song_id))
        return True


def add_suit_to_concert(concert_id, suit_id):
    """Add event_is, suit_id to the event_suit."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM event_suit WHERE event_id = ? and suit_id = ?", (concert_id, suit_id))
        if cursor.fetchall():
            return False

        cursor.execute("INSERT INTO event_suit VALUES (?, ?)", (concert_id, suit_id))
        return True


# UPDATE

def edit_event_name(event_id, event_name):
    """Edit event_name by event _id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET event_name = ? WHERE id = ?", (event_name, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_event_location(event_id, location_id):
    """Edit location_id by event _id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET location_id = ? WHERE id = ?", (location_id, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_event_comment(event_id, comment):
    """Edit comment by event_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET comment = ? WHERE id = ?", (comment, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_event_datetime(event_id, date, time):
    """Edit date and time by event id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE events SET date = ?, time = ? WHERE id = ?", (date, time, event_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_location_name(location_id, location_name):
    """Edit location_name by location_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE locations SET location_name = ? WHERE id = ?", (location_name, location_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


def edit_location_url(location_id, url):
    """Edit location_name by location_id and Return bool to confirm changes"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE locations SET url = ? WHERE id = ?", (url, location_id))
            return True

        except sqlite3.Error as err:
            print(err)
            return False


# DELETE

def delete_event(event_id):
    """DELETE event by id from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))


def delete_location_by_id(location_id):
    """DELETE location by id from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))


def remove_song_from_concert(concert_id, song_id):
    """DELETE song from event_song."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM event_song WHERE event_id = ? and song_id = ?", (concert_id, song_id))


def remove_suit_from_concert(concert_id, suit_id):
    """DELETE suit from event_suit."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM event_suit WHERE event_id = ? and suit_id = ?", (concert_id, suit_id))
