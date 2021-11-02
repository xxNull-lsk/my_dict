import datetime
import sqlite3

from src.setting import setting


class WordBook:
    def __init__(self):
        self.conn = sqlite3.connect(setting.word_book)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS words
               (id INTEGER PRIMARY KEY  AUTOINCREMENT   NOT NULL,
               word            TEXT    UNIQUE NOT NULL,
               translate       TEXT    NOT NULL,
               dt_create          TEXT    NOT NULL,
               review_count    INTEGER);''')

        c.execute('''CREATE TABLE IF NOT EXISTS groups
               (id INTEGER PRIMARY KEY  AUTOINCREMENT   NOT NULL,
               name            TEXT    UNIQUE NOT NULL,
               dt_create          TEXT    NOT NULL);''')

        c.execute('''CREATE TABLE IF NOT EXISTS groups_info
               (word_id       INTEGER   NOT NULL,
                group_id      INTEGER   NOT NULL);''')
        self.conn.commit()

        self.create_group("未分类")

    def add_word(self, word: str, translate: str):
        c = self.conn.cursor()
        try:
            c.execute(
                '''INSERT INTO words (word, translate, dt_create, review_count) VALUES (?, ?, ?, ?);''',
                (word, translate, datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"), 0)
            )
            self.conn.commit()
            return c.lastrowid
        except Exception as ex:
            print(ex)
            return -1

    def create_group(self, name: str):
        c = self.conn.cursor()
        try:
            c.execute(
                '''INSERT INTO groups (name, dt_create) VALUES (?, ?);''',
                (name, datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
            )
            self.conn.commit()
            return c.lastrowid
        except Exception as ex:
            print(ex)
            return -1

    def add_word_to_group(self, word_id: int, group_id: int):
        c = self.conn.cursor()
        try:
            c.execute(
                '''INSERT INTO groups_info (word_id, group_id) VALUES (?, ?);''',
                (word_id, group_id)
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def get_groups(self, row=-1, count=-1) -> list:
        c = self.conn.cursor()
        try:
            if row < 0:
                result = c.execute(
                    '''SELECT id, name, dt_create FROM groups;'''
                )
            else:
                result = c.execute(
                    '''SELECT id, name, dt_create FROM groups LIMIT ? OFFSET ?;''',
                    (count, row)
                )
            return result.fetchall()
        except Exception as ex:
            print(ex)
            return []

    def get_words(self, group_id: int, row=-1, count=-1) -> list:
        c = self.conn.cursor()
        try:
            if row < 0:
                result = c.execute(
                    '''SELECT id, word, translate, dt_create, review_count FROM words WHERE id in
                        (SELECT word_id FROM groups_info WHERE group_id=?);''',
                    (group_id, )
                )
            else:
                result = c.execute(
                    '''SELECT id, word, translate, dt_create, review_count FROM words WHERE id in
                        (SELECT word_id FROM groups_info WHERE group_id=?)
                      LIMIT ? OFFSET ?;''',
                    (group_id, count, row)
                )
            return result.fetchall()
        except Exception as ex:
            print(ex)
            return []

    def change_word_translate(self, word_id: int, translate: str):
        c = self.conn.cursor()
        try:
            c.execute(
                '''UPDATE words SET translate=? WHERE id=?;''',
                (translate, word_id)
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def review_word(self, word_id: int, review_count: int):
        c = self.conn.cursor()
        try:
            c.execute(
                '''UPDATE words SET review_count=? WHERE id=?;''',
                (review_count, word_id)
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def delete_word(self, word_id: int):
        c = self.conn.cursor()
        try:
            c.execute(
                '''DELETE FROM groups_info WHERE word_id=?;''',
                (word_id, )
            )
            c.execute(
                '''DELETE FROM words WHERE id=?;''',
                (word_id, )
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def delete_word_from_group(self, word_id: int, group_id: int):
        c = self.conn.cursor()
        try:
            c.execute(
                '''DELETE FROM groups_info WHERE word_id=? AND group_id=?;''',
                (word_id, group_id)
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def delete_group(self, group_id: int):
        c = self.conn.cursor()
        try:
            c.execute(
                '''DELETE FROM groups_info WHERE group_id=?;''',
                (group_id, )
            )
            c.execute(
                '''DELETE FROM groups WHERE id=?;''',
                (group_id, )
            )
            self.conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False


work_book = WordBook()

