import sqlite3


def get_attendance_by_event_id(event_id):
    """Return all (singer id, fullname, telegram_name, attend) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name, attendance.attend "
                       "FROM attendance "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE event_id = ? ORDER BY attend", (event_id,))
        return cursor.fetchall()


def get_not_participating_by_event_id(event_id):
    """Return all (singer id, fullname, telegram_name) who do not participate in an event from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name "
                       "FROM singers EXCEPT "
                       "SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name "
                       "FROM attendance "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE event_id = ? ORDER BY fullname", (event_id,))
        return cursor.fetchall()


def get_attendance_by_interval(singer_id, start_date, end_date):
    """Return (attend) using singer_id and date interval from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT GROUP_CONCAT(attendance.attend, '') FROM attendance "
                       "JOIN events ON events.id = attendance.event_id "
                       "WHERE attendance.singer_id = ? AND events.date BETWEEN ? AND ?",
                       (singer_id, start_date, end_date))
        return cursor.fetchone()[0]


def check_singer_attendance_exists(event_id, singer_id):
    """Return True if attendance record exists in the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM attendance WHERE event_id = ? AND singer_id = ?", (event_id, singer_id))
        return bool(cursor.fetchone())


def get_all_telegram_singer_id_by_event_id(event_id):
    """Return all telegram singer_id's from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.telegram_id FROM singers "
                       "JOIN attendance ON attendance.singer_id = singers.id "
                       "WHERE attendance.event_id = ?", (event_id,))
        return cursor.fetchall()


# INSERT

def add_all_singers_attendance(event_id: int):
    """Add singers with voices and an event to the attendance table in the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO attendance (event_id, singer_id) "
                       "SELECT DISTINCT ?, singer_id FROM singer_voice "
                       "EXCEPT SELECT event_id, singer_id FROM attendance", (event_id,))


def add_singer_attendance(event_id, singer_id):
    """Add singers  with voices and an event to the attendance table in the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO attendance (event_id, singer_id) VALUES (?, ?)", (event_id, singer_id))


# UPDATE

def edit_singer_attendance(event_id, telegram_id, attend):
    """Edit singer attendance for an event in the database/"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("UPDATE attendance SET attend = ? "
                       "WHERE attendance.event_id = ? AND attendance.singer_id = "
                       "(SELECT id FROM singers WHERE telegram_id = ?)", (attend, event_id, telegram_id))


# DELETE

def remove_singer_attendance(event_id, singer_id):
    """Remove singer attendance check from an event."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM attendance WHERE event_id = ? AND singer_id = ?", (event_id, singer_id))

