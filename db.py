import sqlite3


class BotDB:
    """
    Add/edit/delete singers, set admins right.
    Set voices, songs, events, places, clothes.
    Receive singer attendance.
    """

    def __init__(self, db_file):
        """The database initialisation"""
        self._connect = sqlite3.connect(db_file, check_same_thread=False)
        self._cursor = self._connect.cursor()

    def singer_exists(self, singer_id: int) -> bool:
        """Returns False if the singer is not in the database"""
        existing = self._cursor.execute("SELECT `id` FROM `singers` WHERE `singer_id` = ?", (singer_id,))
        return bool(len(existing.fetchall()))

    def get_singer_id(self, singer_id: int):
        """Receive the singer id from the database"""
        db_singer_id = self._cursor.execute("SELECT `id` FROM `singers` WHERE `singer_id` = ?", (singer_id,))
        return db_singer_id.fetchall()[0]

    def count_singers(self):
        """Count all singers from database"""
        db_singer_id = self._cursor.execute("SELECT COUNT(*) from `singers`")
        return db_singer_id.fetchall()[0][0]

    def show_singers(self):
        """Show all singers from database"""
        db_singer_id = self._cursor.execute("SELECT singers.singer_name, singers.first_name, singers.last_name, "
                                            "GROUP_CONCAT(voices.voice, ', ') FROM singers "
                                            "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                                            "JOIN voices ON voices.id = singer_voice.voice_id GROUP BY singers.id")
        return db_singer_id.fetchall()

    def search_singer_voice(self, singer_id: int):
        """ """
        db_singer_id = self._cursor.execute("SELECT GROUP_CONCAT(voices.voice, ', ') FROM singers "
                                            "JOIN singer_voice ON singer_voice.singer_id = singers.id "
                                            "JOIN voices ON voices.id = singer_voice.voice_id "
                                            "WHERE singers.singer_id = ?", (singer_id,))
        return db_singer_id.fetchall()

    def search_singers_by_voice(self, voice: str):
        """ """
        db_singer_id = self._cursor.execute(
            "SELECT singers.singer_name, singers.first_name, singers.last_name FROM singers "
            "JOIN singer_voice ON singer_voice.singer_id = singers.id "
            "JOIN voices ON voices.id = singer_voice.voice_id "
            "WHERE voices.voice = ?", (voice,))
        return db_singer_id.fetchall()

    def search_singer_by_name(self, msg: str):
        """ """
        db_singer_id = self._cursor.execute("SELECT `singer_name`, `first_name`, `last_name`  FROM `singers` WHERE "
                                            "`first_name` LIKE ?", (msg,))
        return db_singer_id.fetchall()

    def add_singer(self, singer_id: int, singer_name: str, first_name=str, last_name=str):
        """Add new singer into the database"""
        self._cursor.execute("INSERT INTO `singers` "
                             "(`singer_id`, `singer_name`, `first_name`, `last_name`) VALUES (?, ?, ?, ?)",
                             (singer_id, singer_name, first_name, last_name))
        return self._connect.commit()

    def edit_singer(self, singer_id: int):
        """Edit existing singer in the database"""
        # self._cursor.execute("INSERT INTO `singers` (`singer_id`) VALUES (?)", (singer_id,))
        return self._connect.commit()

    def add_admin(self, db_singer_id: int):
        """Add new singer into the database"""
        self._cursor.execute("INSERT INTO `admins` (`db_singer_id`) VALUES (?)", (db_singer_id,))
        return self._connect.commit()

    def is_admin(self, db_singer_id: int):
        """Check if the singer is admin of the bot"""
        admin = self._cursor.execute("SELECT `id` FROM `admins` WHERE `db_singer_id` = ?", (db_singer_id,))
        return bool(len(admin.fetchall()))

    def close(self):
        """Disconnect from the database"""
        self._connect.close()
