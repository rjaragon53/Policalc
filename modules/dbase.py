import sqlite3
from datetime import datetime as dt
from modules import get_data as gd
import os


class access_db:

    def create_tables(self):

        get = gd.get_data()
        f_name, f_path = get.file_data()
        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()

        for name in f_name:
            query = """CREATE TABLE {} (id INTEGER PRIMARY KEY AUTOINCREMENT, date datetime, file blob)""".format(name)
            db_con.execute(query)

        conn.close()

    def insert_all_file(self):

        get = gd.get_data()
        f_name, f_path = get.file_data()
        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()

        for i in range(len(f_path)):

            with open(f_path[i], 'rb') as file:
                blob_file = file.read()

            db_con.execute("INSERT INTO {} VALUES (:id, :date, :file)".format(f_name[i]), {'id': None, 'date': dt.now(), 'file': blob_file})
            conn.commit()

        conn.close()

    def delete_local_files(self):
        get = gd.get_data()
        f_name, f_path = get.file_data()
        for fpath in f_path:
            os.remove(fpath)

        os.remove('raw/raw_rss.txt')
        os.remove('clean/clean_rss.txt')

    def get_all_file(self):

        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()
        get = gd.get_data()
        f_name, f_path = get.file_data()

        for i in range(len(f_path)):
            db_con.execute("SELECT * FROM {} ORDER BY id DESC LIMIT 1;".format(f_name[i]))
            db_data = db_con.fetchone()

            with open(f_path[i], 'wb') as file:
                file.write(db_data[2])

        conn.close()

    def get_file(self, name, f_path):

        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()

        db_con.execute("SELECT * FROM {} ORDER BY id DESC LIMIT 1;".format(name))
        db_data = db_con.fetchone()

        with open(f_path, 'wb') as file:
            file.write(db_data[2])

        conn.close()

    def latest_date(self, table):
        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()

        db_con.execute("SELECT * FROM {} ORDER BY id DESC LIMIT 1;".format(table))
        db_data = db_con.fetchone()

        conn.close()

        return db_data[1]
