import sqlite3
from sqlite3 import Error
import threading

lock = threading.Lock()  # Initialize a lock


class ExcelSqlHelper:

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self):
        """create a database connection to the SQLite database"""
        try:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            print(f"Connected to SQLite database {self.db_file}")
        except Error as e:
            print(e)
        else:
            return conn

    def get_sgl_codes(self):
        """Retrieve distinct sgl_unique_model_code values from Parts table"""
        select_sql = "SELECT DISTINCT sgl_unique_model_code FROM Parts"
        try:
            with lock:
                c = self.conn.cursor()
                c.execute(select_sql)
                data = c.fetchall()
                return [row[0] for row in data]
        except Error as e:
            print(e)

    def execute_sql(self, sql: str):
        """Retrieve distinct sgl_unique_model_code values from Parts table"""
        try:
            with lock:
                c = self.conn.cursor()
                c.execute(sql)
                data = c.fetchall()
                return data
        except Error as e:
            print(e)

    def create_table(self):
        """create table with specified columns"""
        create_table_sql = """CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY,
        sgl_code TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        model TEXT NOT NULL,
        unique_product_code TEXT NOT NULL,
        year TEXT NOT NULL,
        section TEXT NOT NULL
        );"""
        try:
            with lock:
                c = self.conn.cursor()
                c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_record(self, record):
        """insert a new record into the parts table"""
        sql = "INSERT INTO parts(sgl_code, manufacturer, model, unique_product_code, year, section) VALUES(?,?,?,?,?,?)"
        try:
            with lock:
                cur = self.conn.cursor()
                cur.execute(
                    sql,
                    (
                        record["sgl_code"],
                        record["manufacturer"],
                        record["model"],
                        record["unique_product_code"],
                        record["year"],
                        record["section"],
                    ),
                )
                self.conn.commit()
                return cur.lastrowid
        except Error as e:
            print(e)

    def insert_many_records(self, records):
        """insert multiple records into the parts table"""
        sql = "INSERT INTO parts(sgl_code, manufacturer, model, unique_product_code, year, section) VALUES(?,?,?,?,?,?)"
        try:
            with lock:
                cur = self.conn.cursor()
                cur.executemany(
                    sql,
                    [
                        (
                            record["sgl_code"],
                            record["manufacturer"],
                            record["model"],
                            record["unique_product_code"],
                            record["year"],
                            record["section"],
                        )
                        for record in records
                    ],
                )
                self.conn.commit()
        except Error as e:
            print(e)

    def insert_many_records_tuple(self, records):
        """insert multiple records into the parts table"""
        sql = "INSERT INTO parts(sgl_unique_model_code, section, part_number, description, item_number, section_diagram) VALUES(?,?,?,?,?,?)"
        try:
            with lock:
                cur = self.conn.cursor()
                cur.executemany(sql, records)
                self.conn.commit()
        except Error as e:
            print(e)

    def insert_many_records_tuple_with_id(self, records):
        """insert multiple records into the parts table"""
        sql = "INSERT INTO parts(id,sgl_unique_model_code, section, part_number, description, item_number, section_diagram) VALUES(?,?,?,?,?,?,?)"
        try:
            with lock:
                cur = self.conn.cursor()
                cur.executemany(sql, records)
                self.conn.commit()
        except Error as e:
            print(e)

    def get_all(self):
        """Retrieve all records from the parts table"""
        sql = "SELECT sgl_unique_model_code, section, part_number, description, item_number, section_diagram FROM parts;"
        try:
            with lock:
                c = self.conn.cursor()
                c.execute(sql)
                data = c.fetchall()
                return data
        except Error as e:
            print(e)

    def close_connection(self):
        """close the database connection"""
        with lock:
            if self.conn:
                self.conn.close()
                print(f"Connection to SQLite database {self.db_file} closed")
