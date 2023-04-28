from database import db

def get_messages(cId):
    return db.fetch_data('SELECT m.role, m.content FROM USERS u '
                        'inner join CONVERSATION c on u.uId = c.author '
                        'inner join MESSAGE m on m.conversation = c.cId '
                        'WHERE c.cId = %s '
                        'ORDER BY m.mId;', 
                        (cId, ))

def conversations(uId, limit, offset):
    return db.fetch_data('SELECT cId, title from CONVERSATION c '
                        'WHERE c.author = %s '
                        'limit %s offset %s;', 
                        (uId, limit, offset))

def add_message(role, content, conversation):
    db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', (role, content, conversation))

def add_conversation(author):
    return db.execute_query_ret('INSERT INTO CONVERSATION (author) VALUES (%s) RETURNING cId;', (author, ))

def upd_title(cId, title):
    db.execute_query('UPDATE CONVERSATION SET title = %s WHERE cId = %s;', (title, cId))

def get_quota(user):
    return db.fetch_data('SELECT tokens_quota from user_quota WHERE uId = %s;', (user, ))[0][0]

def tokens_left(user):
    return db.fetch_data('SELECT tokens_left FROM USERS u where u.uId = %s;', (user, ))[0][0]

def upd_tokens_left(user, tokens_left):
    db.execute_query('UPDATE USERS SET tokens_left = %s WHERE uId = %s;', (tokens_left, user))


def get_author(conversation):
    return db.fetch_data('SELECT author FROM CONVERSATION c where c.cId = %s;', (conversation, ))[0][0]

def get_uid_by_sub(sub):
    return db.fetch_data('SELECT uId FROM USERS u where u.sub = %s;', (sub, ))

def add_user(sub, name):
    return db.execute_query_ret('INSERT INTO USERS (sub, name) VALUES (%s, %s) RETURNING uId;', (sub, name))