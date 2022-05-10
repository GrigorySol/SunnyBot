import sqlite3


def get_all_events():
    """Return all (id, event_id, event_name, datetime, location_id, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events ORDER BY datetime")
        return cursor.fetchall()


def get_event_name(_id):
    """Return event_name from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT event_name FROM events WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_event_datetime(_id):
    """Return datetime from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT datetime FROM events WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_event_location_id(_id):
    """Return location_id from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT location_id FROM events WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def get_event_comment(_id):
    """Return event_name from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT comment FROM events WHERE id = ?", (_id,))
        return cursor.fetchone()[0]


def search_event_by_id(_id):
    """Return id, event_id, event_name, datetime, location_id, comment from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (_id,))
        return cursor.fetchone()


def search_events_by_event_id(event_id):
    """Return (id, location_name, datetime) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT events.id, location_name, events.datetime FROM events "
                       "JOIN locations ON locations.id = events.location_id "
                       "WHERE event_id = ? ORDER BY datetime", (event_id,))
        return cursor.fetchall()


def search_event_by_date(date):
    """Return (id, event_id, event_name, datetime, location_id, comment) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events WHERE datetime LIKE ? ORDER BY datetime", (date,))
        return cursor.fetchall()


def get_all_locations():
    """Return all (id, location_name, url) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM locations")
        return cursor.fetchall()


def search_location_by_id(_id):
    """Return id, location_name, url from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM locations WHERE id = ?", (_id,))
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

def add_event(event_id, event_name, datetime, location_id):
    """Add new singer into the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO events (event_id, event_name, datetime, location_id) VALUES (?, ?, ?, ?)",
                       (event_id, event_name, datetime, location_id))
        cursor.execute("SELECT id FROM events WHERE datetime = ?", (datetime,))
        return cursor.fetchone()[0]


def add_location(location_name, url):
    """Add suit for the singer into database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("INSERT INTO locations (location_name, url) VALUES (?, ?)", (location_name, url))
        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (location_name,))
        return cursor.fetchone()[0]


# UPDATE


# DELETE
