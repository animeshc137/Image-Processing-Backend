from get_sql_connection import get_connection

connection = get_connection()

# run once to create the tabele in sql
try:
    cursor = connection.cursor()
    #cursor.execute("CREATE TABLE output_data (serial_no INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, input_image_urls TEXT NOT NULL, output_image_urls TEXT, status VARCHAR(25)) ")
    cursor.execute("select * from output_data")
    print(cursor.fetchall())
finally:
  connection.close()