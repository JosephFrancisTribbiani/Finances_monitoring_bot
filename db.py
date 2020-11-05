# import psycopg2
# from config import DB_LINK
#
# __connection = None
#
#
# def get_connection():
#     global __connection
#     if __connection is None:
#         __connection = psycopg2.connect(DB_LINK, sslmode='require')
#     return __connection

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


# def test(msg):
#     conn = get_connection()
#     cur = conn.cursor()
#
#     user = 3
#     fname = msg.chat.first_name
#     lname = msg.chat.last_name
#     nick = 'Kisonka'
#
#     cur.execute(f'''
#                 INSERT INTO users(user_id, fname, lname, nickname)
#                 VALUES (?, ?, ?, ?);
#                 ''', (user, fname, lname, nick))
#     conn.commit()
