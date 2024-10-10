import pymysql
from vars import *
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

# run once to create the tabele in sql
try:
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE output_data (serial_no INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, input_image_urls TEXT NOT NULL, output_image_urls TEXT, status VARCHAR(25)) ")
    print(cursor.fetchall())
finally:
  connection.close()