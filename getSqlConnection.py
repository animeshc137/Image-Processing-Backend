from vars import *
import pymysql

def get_connection():
    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db=DB,
    host=SQLHOST,
    password=SQLPASS,
    read_timeout=timeout,
    port=11252,
    user=SQLUSER,
    write_timeout=timeout,
    )
    return connection