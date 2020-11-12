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
        cur.execute('DROP TABLE IF EXISTS users, messages, expenses, u_expenses;')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                u_id INTEGER PRIMARY KEY,
                f_name TEXT,
                l_name TEXT,
                n_name TEXT,
                l_code TEXT,
                date DATE NOT NULL);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                m_id SERIAL PRIMARY KEY,
                u_id INTEGER NOT NULL REFERENCES users (u_id),
                date DATE NOT NULL,
                message TEXT NOT NULL);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS u_expenses (
                exp_id SERIAL PRIMARY KEY,
                u_id INTEGER REFERENCES users (u_id),
                exp_name TEXT,
                UNIQUE (u_id, exp_name));
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                exp_id INTEGER NOT NULL REFERENCES u_expenses (exp_id),
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


@get_connection
def check_category(cat: str, u_id: str, conn, cur):
    """
    Функция проверяет новую ли категорию указал пользователь, или она уже присутствует в таблице u_expenses
    :param cat: название категории (все буквы маленькие)
    :param u_id: id пользователя
    :param cur:
    :return: True или False
    """
    cur.execute('''SELECT EXISTS (SELECT 1 FROM u_expenses WHERE u_id=%s AND exp_name=%s);
                ''', (u_id, cat))
    return cur.fetchone()[0]


@get_connection
def add_cat_into_db(u_id, category, conn, cur):
    cur.execute('''INSERT INTO u_expenses (u_id, exp_name)
                    VALUES (%s, %s);
                    ''', (u_id, category))
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
def get_my_cat(u_id: str, conn, cur) -> list:
    cur.execute('''SELECT exp_name FROM u_expenses WHERE u_id=%s;
                ''', (u_id,))
    return cur.fetchall()


@get_connection
def add_exp_into_db(*args, conn, cur):
    cur.execute('''
    INSERT INTO expenses (exp_id, value, date)
    VALUES ((SELECT exp_id FROM u_expenses WHERE u_id = %s AND exp_name = %s), %s, %s);
    ''', args)  # args -> u_id, category, amount, date
    conn.commit()
