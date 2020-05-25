import sqlite3
import hashlib
import datetime
import configparser
from crypto import quick_encrypt, quick_decrypt
import configparser

config = configparser.ConfigParser()
config.read('conf.ini')

DB_FILE = config['APP']['DB_FILE']
TITLE_TIMESTAMP_FORMAT = config['APP']['TITLE_TIMESTAMP_FORMAT']
SYS_LEVEL_ENCRYPTION = config['CRYPTO']['SYS_LEVEL_ENCRYPTION']
DEFAULT_PASSKEY = config['CRYPTO']['DEFAULT_PASSKEY']
DEFAULT_LIST_LIMIT = int(config['APP']['DEFAULT_LIST_LIMIT'])


# print(DB_FILE + str(type(DB_FILE)))
# print(TITLE_TIMESTAMP_FORMAT + str(type(TITLE_TIMESTAMP_FORMAT)))
# print(SYS_LEVEL_ENCRYPTION + str(type(SYS_LEVEL_ENCRYPTION)))
# print(DEFAULT_PASSKEY + str(type(DEFAULT_PASSKEY)))
# print(str(DEFAULT_LIST_LIMIT) + str(type(DEFAULT_LIST_LIMIT)))

class Snotes:
    sql_conn = sqlite3.connect(DB_FILE)

    def __init__(self, note, title=datetime.datetime.now().strftime(TITLE_TIMESTAMP_FORMAT)):
        self.note = note
        self.title = title
        # self.created_on = None

    def save_note(self, encrypted=False, passkey=DEFAULT_PASSKEY):
        if encrypted:
            self.__encrypt_note(passkey)
            sql = "INSERT INTO snotes_db (title, note, hash, encrypted) VALUES ('" + self.title + "','" + self.note + "', '" + hashlib.md5(
                self.note.encode()).hexdigest() + "', 1)"
        else:
            sql = "INSERT INTO snotes_db (title, note, hash, encrypted) VALUES ('" + self.title + "','" + self.note + "', '" + hashlib.md5(
                self.note.encode()).hexdigest() + "', 0)"
        Snotes.sql_conn.execute(sql)
        Snotes.sql_conn.commit()

    @staticmethod
    def list_notes(limit=DEFAULT_LIST_LIMIT):
        cur = Snotes.sql_conn.execute("SELECT note_id, title, created_on, encrypted FROM snotes_db LIMIT " + str(limit))
        rows = cur.fetchall()
        return rows

    @staticmethod
    def search_notes(title, limit=DEFAULT_LIST_LIMIT):
        cur = Snotes.sql_conn.execute(
            "SELECT note_id, title, created_on FROM snotes_db WHERE title LIKE '%'" + title + "'%' LIMIT " + str(limit))
        rows = cur.fetchall()
        return rows

    @staticmethod
    def read_note(note_id, passkey=DEFAULT_PASSKEY):
        cur = Snotes.sql_conn.execute(
            "SELECT note_id, title, note, encrypted, created_on FROM snotes_db WHERE note_id = " + str(note_id))
        row = cur.fetchone()
        if row is None:
            return None
        if row[3] == 1:
            r = Snotes(row[2], row[1])
            r.__decrypt_note(passkey)
        else:
            r = Snotes(row[2], row[1])
        return r

    def __encrypt_note(self, passkey):
        self.note = quick_encrypt(self.note, passkey)

    def __decrypt_note(self, passkey=DEFAULT_PASSKEY):

        self.note = quick_decrypt(self.note, passkey)
        # self.title = rows[0][1]

# n1 = Snotes("seventh text")
#
# n1.save_note(encrypted=True, passkey='sag')
# print(n1.list_notes())
#
# print(Snotes.read_note(7, passkey='sag').note)