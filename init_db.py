from database import db

db.execute_query('DROP TABLE IF EXISTS PRIVILEGES CASCADE;')
db.execute_query('CREATE TABLE PRIVILEGES ('
                                'level SERIAL PRIMARY KEY,'
                                'tokens_quota INTEGER NOT NULL);'
                                )

db.execute_query('DROP TABLE IF EXISTS USERS CASCADE;')
db.execute_query('CREATE TABLE USERS ('
                                'uId SERIAL PRIMARY KEY,'
                                'name TEXT NOT NULL,'
                                'total_spent INTEGER DEFAULT 0,'
                                'tokens_left INTEGER DEFAULT 0,'
                                'lvl INTEGER NOT NULL DEFAULT 1,'
                                'FOREIGN KEY (lvl) REFERENCES PRIVILEGES(level));'
                                )

db.execute_query('DROP TABLE IF EXISTS CONVERSATION CASCADE;')
db.execute_query('CREATE TABLE CONVERSATION ('
                                    'cId SERIAL PRIMARY KEY,'
                                    'author INTEGER NOT NULL,'
                                    'FOREIGN KEY (author) REFERENCES USERS(uId) on delete cascade);'
                                    )

db.execute_query('DROP TABLE IF EXISTS MESSAGE;')
db.execute_query('CREATE TABLE MESSAGE ('
                                'mId SERIAL PRIMARY KEY,'
                                'role text NOT NULL,'
                                'content text NOT NULL,'
                                'create_t timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,'
                                'conversation INTEGER NOT NULL,'
                                'FOREIGN KEY (conversation) REFERENCES CONVERSATION(cId) on delete cascade);'
                                )

db.execute_query('CREATE OR REPLACE VIEW user_quota AS '
                 'SELECT uId, tokens_quota FROM USERS u '
                 'left join PRIVILEGES p on u.lvl = p.level;'
                 )


db.execute_query('CREATE OR REPLACE FUNCTION set_default_value() RETURNS trigger AS '
                 '$$ BEGIN '
                 'NEW.tokens_left := (SELECT tokens_quota FROM PRIVILEGES WHERE level = NEW.lvl);'
                 'RETURN NEW; '
                 'END; $$ '
                 'LANGUAGE plpgsql;'
                 )

db.execute_query('CREATE OR REPLACE TRIGGER trg_set_default_value '
                 'BEFORE INSERT ON USERS '
                 'FOR EACH ROW EXECUTE FUNCTION set_default_value();')


db.execute_query('CREATE OR REPLACE FUNCTION update_total_token_used() RETURNS trigger AS '
                 '$$ BEGIN '
                 'IF NEW.tokens_left < OLD.tokens_left THEN '
                 'UPDATE Users SET total_spent = total_spent + OLD.tokens_left - NEW.tokens_left WHERE uId = NEW.uId; '
                 'END IF; RETURN NEW; '
                 'END; $$ '
                 'LANGUAGE plpgsql;'
                 )

db.execute_query('CREATE OR REPLACE TRIGGER trg_update_total_token_used '
                 'AFTER UPDATE OF tokens_left ON USERS '
                 'FOR EACH ROW EXECUTE FUNCTION update_total_token_used();')



db.execute_query('INSERT INTO PRIVILEGES (tokens_quota) VALUES (%s);', (5000, ))
db.execute_query('INSERT INTO PRIVILEGES (tokens_quota) VALUES (%s);', (10000, ))
db.execute_query('INSERT INTO PRIVILEGES (tokens_quota) VALUES (%s);', (20000, ))

db.execute_query('INSERT INTO USERS (name) VALUES (%s);', ('Clark', ))
db.execute_query('INSERT INTO USERS (name) VALUES (%s);', ('Dave', ))
db.execute_query('INSERT INTO USERS (name) VALUES (%s);', ('Ava', ))


db.execute_query('INSERT INTO CONVERSATION (author) VALUES (%s);', (1, ))
db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', ("assist", "You are the best", 1))
db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', ("user", "Are you ok?", 1))
db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', ("system", "Yep", 1))

db.execute_query('INSERT INTO CONVERSATION (author) VALUES (%s);', (1, ))
db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', ("assist", "You are the best", 2))

db.execute_query('INSERT INTO CONVERSATION (author) VALUES (%s);', (2, ))
db.execute_query('INSERT INTO MESSAGE (role, content, conversation) VALUES (%s, %s, %s);', ("assist", "You are the best", 3))
