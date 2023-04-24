import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="chat_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])


cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS USERS CASCADE;')
cur.execute('CREATE TABLE USERS ('
                                'uId SERIAL PRIMARY KEY,'
                                'name TEXT NOT NULL,'
                                'dept TEXT NOT NULL,'
                                'tokens_spent INTEGER DEFAULT 0,'
                                'tokens_left INTEGER DEFAULT 0,'
                                'tokens_quota INTEGER DEFAULT 0);'
                                )

cur.execute('DROP TABLE IF EXISTS CONVERSATION;')
cur.execute('CREATE TABLE CONVERSATION ('
                                    'cId SERIAL PRIMARY KEY,'
                                    'title TEXT,'
                                    'author INTEGER NOT NULL,'
                                    'FOREIGN KEY (author) REFERENCES USERS(uId));'
                                    )

cur.execute('DROP TABLE IF EXISTS MESSAGE;')
cur.execute('CREATE TABLE MESSAGE ('
                                'mId varchar(255) NOT NULL,'
                                'role text NOT NULL,'
                                'content text NOT NULL,'
                                'create_t timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,'
                                'conversation INTEGER NOT NULL,'
                                'CONSTRAINT PK_Message PRIMARY KEY (mId, conversation));'
                                    )

cur.execute('INSERT INTO USERS (name, dept) VALUES (%s, %s);', ('Clark', 'Sales'))
cur.execute('INSERT INTO USERS (name, dept) VALUES (%s, %s);', ('Dave', 'Accounting'))
cur.execute('INSERT INTO USERS (name, dept) VALUES (%s, %s);', ('Ava', 'Sales'))

cur.execute('INSERT INTO CONVERSATION (title, author) VALUES (%s, %s);', ("C++", 1))
cur.execute('INSERT INTO CONVERSATION (title, author) VALUES (%s, %s);', ("C", 1))
cur.execute('INSERT INTO CONVERSATION (title, author) VALUES (%s, %s);', ("Rust", 2))

cur.execute('INSERT INTO MESSAGE (mId, role, content, conversation) VALUES (%s, %s, %s, %s);', ('m1', "assist", "You are the best", 1))
cur.execute('INSERT INTO MESSAGE (mId, role, content, conversation) VALUES (%s, %s, %s, %s);', ('m2', "user", "Are you ok?", 1))
cur.execute('INSERT INTO MESSAGE (mId, role, content, conversation) VALUES (%s, %s, %s, %s);', ('m3', "system", "Yep", 1))
cur.execute('INSERT INTO MESSAGE (mId, role, content, conversation) VALUES (%s, %s, %s, %s);', ('m2', "assist", "You are the best", 2))
cur.execute('INSERT INTO MESSAGE (mId, role, content, conversation) VALUES (%s, %s, %s, %s);', ('m1', "assist", "You are the best", 3))


conn.commit()

cur.close()
conn.close()