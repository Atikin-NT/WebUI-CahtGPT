import os
import psycopg2
import pprint

class PostgresClient:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Connected to PostgreSQL database!")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()
            print("Disconnected from PostgreSQL database.")
            self.conn = None

    def execute_query(self, query, params=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            print("Query executed successfully!")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")

    def execute_query_ret(self, query, params=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            print("Query executed successfully!")
            return cursor.fetchone()[0]
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            return None

    def fetch_data(self, query, params=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")

    def __del__(self):
        self.disconnect()


# pprint.pprint(dict(os.environ), width = 1)

# Создание экземпляра класса PostgresClient
db = PostgresClient(
    dbname='chat_db', 
    user="postgres", 
    password="postgres", 
    host='localhost', 
    port='5432')
