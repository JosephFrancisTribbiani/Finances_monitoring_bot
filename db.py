import psycopg2
from config import DATABASE_URL

__connection = None


def get_connection():
    global __connection
    if __connection is None:
        __connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    return __connection

#
# def init_db(force: bool = False):
#     conn = get_connection()
#     cur = conn.cursor()
#
#     if force:
#         cur.execute('DROP TABLE IF EXISTS expenses')
#
#     cur.execute('''CREATE TABLE IF NOT EXISTS expenses(
#                 id SERIAL,
#                 chat_id INTEGER NOT NULL
#                 ''')


def test(msg):
    conn = get_connection()
    cur = conn.cursor()

    user = 3
    fname = msg.chat.first_name
    lname = msg.chat.last_name
    nick = 'Kisonka'

    cur.execute('''
                INSERT INTO users(user_id, fname, lname, nickname)
                VALUES (%s, %s, %s, %s);
                ''', (user, fname, lname, nick))
    conn.commit()
    cur.close()
    conn.close()
