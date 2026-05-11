import pymysql
import config as c


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