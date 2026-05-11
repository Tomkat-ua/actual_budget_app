import pymysql
import config as c
from contextlib import contextmanager

@contextmanager
def get_db_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()

db_config = {
    'host': c.db_host,
    'port': c.db_port,
    'user': c.db_user,
    'password': c.db_password,
    'database': c.db_name ,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    conn = pymysql.connect(**db_config)
    return conn