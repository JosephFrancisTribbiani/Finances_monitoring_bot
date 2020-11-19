import psycopg2
from functools import wraps
from config import DATABASE_URL
from datetime import datetime


def get_connection(func):
    """
    Декоратор для создания подключения к базе и гарантированного его закрытия
    :param func: функция, которой требуется подключиться к базе
    :return:
    """
    @wraps(func)
    def inner(*args, **kwargs):
        with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
            res = func(*args, conn=conn, cur=cur, **kwargs)
        return res
    return inner


@get_connection
def init_db(conn, cur, force: bool = False):
    """
    Функция формирует систему таблиц базы данных
    :param conn: connection к базе
    :param cur: курсор подключения к базе
    :param force: True если необходимо пересоздать базу данных (все данные будут удалены)
    :return: nothing
    """

    if force:
        cur.execute('DROP TABLE IF EXISTS users, limits, messages, u_inout, inout;')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                u_id INTEGER PRIMARY KEY,
                f_name TEXT,
                l_name TEXT,
                n_name TEXT,
                l_code TEXT,
                date DATE NOT NULL,
                u_state INTEGER);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS limits (
                l_id SERIAL PRIMARY KEY,
                u_id INTEGER NOT NULL REFERENCES users (u_id),
                date DATE NOT NULL,
                value NUMERIC NOT NULL);
                ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                m_id SERIAL PRIMARY KEY,
                u_id INTEGER NOT NULL REFERENCES users (u_id),
                date DATE NOT NULL,
                message TEXT NOT NULL);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS u_inout (
                io_id SERIAL PRIMARY KEY,
                u_id INTEGER REFERENCES users (u_id),
                description TEXT,
                type TEXT CHECK (type IN ('in', 'out')),
                UNIQUE (u_id, description));
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS inout (
                id SERIAL PRIMARY KEY,
                io_id INTEGER NOT NULL REFERENCES u_inout (io_id),
                value NUMERIC NOT NULL,
                date DATE NOT NULL);
                ''')
    conn.commit()


@get_connection
def collect_user(usr, conn, cur):
    """
    Функция вносит информацию о новом пользователе в базу данных в таблицу users (если если пользователя с таким ID нет)
    :param usr:
    :param conn:
    :param cur:
    :return: nothing
    """
    cur.execute('''INSERT INTO users (u_id, f_name, l_name, n_name, l_code, date, u_state)
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
                ''', (usr.id, usr.first_name, usr.last_name, usr.username, usr.language_code,
                      datetime.today().strftime('%Y-%m-%d'), 0))
    conn.commit()


@get_connection
def collect_msg_into_db(u_id: str, msg: str, conn, cur):
    """
    Функция записывает в таблицу messages текст сообщения
    :param u_id: id пользователя
    :param msg: текст сообщения
    :param conn:
    :param cur:
    :return: nothing
    """
    cur.execute('''INSERT INTO messages (u_id, date, message)
                VALUES (%s, %s, %s);
                ''', (u_id, datetime.today().strftime('%Y-%m-%d'), msg))
    conn.commit()


@get_connection
def check_category(cat: str, u_id: str, conn, cur):
    """
    Функция проверяет новую ли категорию указал пользователь, или она уже присутствует в таблице u_inout
    :param cat: название категории (все буквы маленькие)
    :param u_id: id пользователя
    :param cur:
    :return: True или False
    """
    cur.execute('''SELECT EXISTS (SELECT 1 FROM u_inout WHERE u_id=%s AND description=%s);
                ''', (u_id, cat))
    return cur.fetchone()[0]


@get_connection
def add_cat_into_db(*args, conn, cur):
    cur.execute('''INSERT INTO u_inout (u_id, description, type)
                    VALUES (%s, %s, %s);
                    ''', args)
    conn.commit()


@get_connection
def check_user(u_id: str, conn, cur) -> bool:
    """
    Функция проверят есть ли пользователь в таблице users
    :param u_id: id пользователя
    :param conn:
    :param cur:
    :return: True или False
    """
    cur.execute('''SELECT EXISTS (SELECT 1 FROM users WHERE u_id=%s);
                ''', (u_id,))
    return cur.fetchone()[0]


@get_connection
def get_my_cat_db(u_id: str, conn, cur) -> list:
    cur.execute('''SELECT description, type FROM u_inout WHERE u_id=%s;
                ''', (u_id,))
    return cur.fetchall()


@get_connection
def add_exp_into_db(*args, conn, cur):
    cur.execute('''
    INSERT INTO inout (io_id, value, date)
    VALUES ((SELECT io_id FROM u_inout WHERE u_id = %s AND description = %s), %s, %s);
    ''', args)  # args -> u_id, category, amount, date
    conn.commit()


@get_connection
def get_limit(u_id, conn, cur):
    cur.execute('''
    SELECT value FROM LIMITS
    WHERE u_id = %s
    ORDER BY date
    DESC LIMIT 1;
    ''', (u_id, ))
    res = cur.fetchone()
    if res is not None:
        return res[0]


@get_connection
def set_state(*args, conn, cur):
    cur.execute('''
    UPDATE users
    SET u_state = %s
    WHERE u_id = %s;
    ''', args)
    conn.commit()


@get_connection
def get_state(u_id, conn, cur):
    cur.execute('''
    SELECT u_state FROM users
    WHERE u_id = %s;
    ''', (u_id, ))
    return cur.fetchone()[0]


@get_connection
def set_limit_db(*args, conn, cur):
    u_id, value = args
    td = datetime.today().strftime('%Y-%m-%d')
    cur.execute('''
    SELECT EXISTS (SELECT 1 FROM limits WHERE u_id = %s AND date = %s);
    ''', (u_id, td))

    if not cur.fetchone()[0]:
        cur.execute('''
        INSERT INTO limits (u_id, date, value)
        VALUES (%s, %s, %s);
        ''', (u_id, td, value))
    else:
        cur.execute('''
        UPDATE limits
        SET value = %s
        WHERE date = %s;
        ''', (value, td))
    conn.commit()


@get_connection
def spent_daily(u_id, conn, cur, c_type='out',
                d_from=datetime.today().strftime('%Y-%m-%d'),
                d_to=datetime.today().strftime('%Y-%m-%d')):
    cur.execute('''
    SELECT sum(t2.value)
    FROM u_inout AS t1
    INNER JOIN inout AS t2
    ON t1.io_id = t2.io_id
    WHERE t1.u_id = %s AND t1.type = %s
    AND t2.date BETWEEN %s AND %s
    GROUP BY t1.u_id;
    ''', (u_id, c_type, d_from, d_to))

    return cur.fetchone()[0]
