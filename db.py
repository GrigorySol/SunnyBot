import sqlite3


class BotDB:
    """
    Add/edit/delete users, set admins right.
    Set voices, songs, events, places, clothes.
    Receive user attendance.
    """

    def __init__(self, db_file):
        """The database initialisation"""
        self._connect = sqlite3.connect(db_file, check_same_thread=False)
        self._cursor = self._connect.cursor()

    def user_exists(self, user_id: int) -> bool:
        """Returns False if the user is not in the database"""
        existing = self._cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(existing.fetchall()))

    def get_user_id(self, user_id: int):
        """Receive the user id from the database"""
        db_user_id = self._cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return db_user_id.fetchall()[0]

    def count_users(self):
        """Count all users from database"""
        db_user_id = self._cursor.execute("SELECT COUNT(*) from `users`")
        return db_user_id.fetchall()[0][0]

    def show_users(self):
        """Show all users from database"""
        db_user_id = self._cursor.execute("SELECT users.user_name, users.first_name, users.last_name, "
                                          "GROUP_CONCAT(voices.voice, ', ') FROM users "
                                          "JOIN user_voice ON user_voice.user_id = users.id "
                                          "JOIN voices ON voices.id = user_voice.voice_id GROUP BY users.id")
        return db_user_id.fetchall()

    def search_user_voice(self, user_id: int):
        """ """
        db_user_id = self._cursor.execute("SELECT GROUP_CONCAT(voices.voice, ', ') FROM users "
                                          "JOIN user_voice ON user_voice.user_id = users.id "
                                          "JOIN voices ON voices.id = user_voice.voice_id "
                                          "WHERE users.user_id = ?", (user_id,))
        return db_user_id.fetchall()

    def search_users_by_voice(self, voice: str):
        """ """
        db_user_id = self._cursor.execute("SELECT users.user_name, users.first_name, users.last_name FROM users "
                                          "JOIN user_voice ON user_voice.user_id = users.id "
                                          "JOIN voices ON voices.id = user_voice.voice_id "
                                          "WHERE voices.voice = ?", (voice,))
        return db_user_id.fetchall()

    def search_user_by_name(self, msg: str):
        """ """
        db_user_id = self._cursor.execute("SELECT `user_name`, `first_name`, `last_name`  FROM `users` WHERE "
                                          "`first_name` LIKE ?", (msg,))
        return db_user_id.fetchall()

    def add_user(self, user_id: int, user_name: str, first_name=str, last_name=str):
        """Add new user into the database"""
        self._cursor.execute("INSERT INTO `users` "
                             "(`user_id`, `user_name`, `first_name`, `last_name`) VALUES (?, ?, ?, ?)",
                             (user_id, user_name, first_name, last_name))
        return self._connect.commit()

    def edit_user(self, user_id: int):
        """Edit existing user in the database"""
        # self._cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self._connect.commit()

    def add_admin(self, db_user_id: int):
        """Add new user into the database"""
        self._cursor.execute("INSERT INTO `admins` (`db_user_id`) VALUES (?)", (db_user_id,))
        return self._connect.commit()

    def is_admin(self, db_user_id: int):
        """Check if the user is admin of the bot"""
        admin = self._cursor.execute("SELECT `id` FROM `admins` WHERE `db_user_id` = ?", (db_user_id,))
        return bool(len(admin.fetchall()))

    def close(self):
        """Disconnect from the database"""
        self._connect.close()
