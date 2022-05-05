import sqlite3


class BotDB:
    """
    Add/edit/delete singers, set admins right.
    Set voices, songs, events, places, clothes.
    Receive singer attendance.
    """

    def __init__(self, db_file):
        """The database initialisation."""
        self._connect = sqlite3.connect(db_file, check_same_thread=False)
        self._cursor = self._connect.cursor()

    def singer_exists(self, singer_id: int) -> bool:
        """Returns False if the singer is not in the database."""
        existing = self._cursor.execute("SELECT id FROM singers WHERE singer_id = ?", (singer_id,))
        return bool(len(existing.fetchall()))

    def get_singer_id(self, singer_id: int):
        """Receive the singer id from the database."""
        db_singer_id = self._cursor.execute("SELECT id FROM singers WHERE singer_id = ?", (singer_id,))
        return db_singer_id.fetchall()[0][0]

    def is_admin(self, _id: int):
        """Check if the singer is admin of the bot."""
        db_admin = self._cursor.execute("SELECT * FROM admins "
                                        "JOIN singers ON singers.id = admins.singer_id "
                                        "WHERE singers.singer_id = ?", (_id,))
        return bool(len(db_admin.fetchall()))

    def count_singers(self):
        """Count all singers from database"""
        db_singer_id = self._cursor.execute("SELECT COUNT(*) from `singers`")
        return db_singer_id.fetchall()[0][0]

    def get_singer_telegram_name(self, _id: int):
        """Receive the telegram username from the database."""
        db_singername = self._cursor.execute("SELECT telegram_name FROM singers WHERE id = ?", (_id,))
        return db_singername.fetchall()[0][0]

    def get_singer_fullname(self, _id: int):
        """Receive the singer (name lastname) from the database."""
        db_fullname = self._cursor.execute("SELECT first_name || ' ' || last_name AS fullname "
                                           "FROM singers WHERE id = ?", (_id,))
        return db_fullname.fetchall()[0]

    def get_singer_voices(self, _id: int):
        """Receive the singer voices from the database."""
        db_voices = self._cursor.execute("SELECT GROUP_CONCAT(voice, ', ') FROM voices "
                                         "INNER JOIN singer_voice ON singer_voice.voice_id = voices.id "
                                         "WHERE singer_voice.singer_id = ?", (_id,))
        return db_voices.fetchone()[0]

    def get_singer_suits(self, _id: int):
        """Receive the singer suits from the database."""
        db_suits = self._cursor.execute("SELECT GROUP_CONCAT(suit, ', ') FROM suits "
                                        "INNER JOIN singer_suit ON singer_suit.suit_id = suits.id "
                                        "WHERE singer_suit.singer_id = ?", (_id,))
        return db_suits.fetchone()[0]

    def get_all_suits(self):
        """Receive all suits from the database."""
        db_suits = self._cursor.execute("SELECT suit, image FROM suits ")
        return db_suits.fetchall()

    def get_all_singers(self):
        """Return (name lastname, id) of the all singers from database."""
        db_singers = self._cursor.execute("SELECT first_name || ' ' || last_name AS fullname, id "
                                          "FROM singers")
        return db_singers.fetchall()

    def get_all_admins(self):
        """Return singer_id for each admin from database."""
        db_admin = self._cursor.execute("SELECT singers.singer_id FROM singers "
                                        "JOIN admins ON admins.singer_id = singers.id ")
        return db_admin.fetchall()[0]

    def get_voice_list(self):
        """Return all available voices from database."""
        voices = self._cursor.execute("SELECT voice FROM voices")
        return voices.fetchall()

    def search_singer_voice(self, singer_id: int):
        """Return all singer voices from database."""
        db_singer_voice = self._cursor.execute("SELECT GROUP_CONCAT(voices.voice, ', ') FROM singers "
                                               "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                                               "JOIN voices ON voices.id = singer_voice.voice_id "
                                               "WHERE singers.singer_id = ?", (singer_id,))
        return db_singer_voice.fetchall()

    def search_singers_by_voice(self, voice: str):
        """Return (name lastname, id) of the singers of the chosen voice from database"""
        db_singer = self._cursor.execute(
            "SELECT singers.first_name || ' ' || singers.last_name AS fullname, singers.id "
            "FROM singers "
            "JOIN singer_voice ON singer_voice.singer_id = singers.id "
            "JOIN voices ON voices.id = singer_voice.voice_id "
            "WHERE voices.voice = ?", (voice,))
        return db_singer.fetchall()

    """TODO: Replace below code to above"""

    """
    def show_singers(self):
        db_singer_id = self._cursor.execute("SELECT singers.singer_name, singers.first_name, singers.last_name, "
                                            "GROUP_CONCAT(voices.voice, ', ') FROM singers "
                                            "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                                            "JOIN voices ON voices.id = singer_voice.voice_id GROUP BY singers.id")
        return db_singer_id.fetchall()
    """

    def search_singer_by_name(self, msg: str):
        """Return """
        db_singer_id = self._cursor.execute("SELECT singer_name, first_name, last_name "
                                            "FROM singers WHERE first_name LIKE ?", (msg,))
        return db_singer_id.fetchall()

    def add_singer(self, singer_id: int, singer_name: str, first_name=str, last_name=str):
        """Add new singer into the database"""
        self._cursor.execute("INSERT INTO singers "
                             "(singer_id, singer_name, first_name, last_name) VALUES (?, ?, ?, ?)",
                             (singer_id, singer_name, first_name, last_name))
        return self._connect.commit()

    def edit_singer(self, singer_id: int):
        """Edit existing singer in the database"""
        # self._cursor.execute("INSERT INTO `singers` (`singer_id`) VALUES (?)", (singer_id,))
        return self._connect.commit()

    def close(self):
        """Disconnect from the database"""
        self._connect.close()
