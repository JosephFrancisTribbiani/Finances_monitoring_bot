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
            func(*args, conn=conn, cur=cur, **kwargs)

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
        cur.execute('DROP TABLE IF EXISTS users, messages, exp_types, expenses, u_expenses;')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                u_id INTEGER PRIMARY KEY,
                f_name TEXT,
                l_name TEXT,
                n_name TEXT,
                l_code TEXT,
                date DATE);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                m_id SERIAL PRIMARY KEY,
                u_id INTEGER REFERENCES users (u_id),
                date DATE,
                message TEXT);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS exp_types (
                type_id SERIAL PRIMARY KEY,
                type_name TEXT UNIQUE);
                ''')
    cur.execute('''INSERT INTO exp_types (type_name)
                    VALUES ('ОБЯЗАТЕЛЬНЫЕ'),
                           ('ПОСТОЯННЫЕ'),
                           ('СЛУЧАЙНЫЕ') ON CONFLICT DO NOTHING;
                    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
                exp_id SERIAL PRIMARY KEY,
                exp_name TEXT);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS u_expenses (
                id SERIAL PRIMARY KEY,
                u_id INTEGER REFERENCES users (u_id),
                exp_id INTEGER REFERENCES expenses (exp_id),
                date DATE,
                value NUMERIC);
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
    cur.execute('''INSERT INTO users (u_id, f_name, l_name, n_name, l_code, date)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
                ''', (usr.id, usr.first_name.capitalize(), usr.last_name.capitalize(), usr.username, usr.language_code, \
                      datetime.today().strftime('%Y-%m-%d')))
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
