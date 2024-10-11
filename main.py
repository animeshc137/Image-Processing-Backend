import uuid
import os
import pandas as pd
from get_sql_connection import get_connection
from csv_validator import validate_csv
from image_processing import process_image
# below vars.py contains following environment variables 
# SQLHOST sql hostname
# DB database name
# TABLE tablename
# SQLPASS sql password
# SQLUSER sql username
# OUTPUT_IMAGE_DIR directory where output images will be stored
# CSV_INPUT path to input csv file
# CSV_OUTPUT path where outputcsv file will be stored
from vars import *

connection = get_connection()
# Directory to store processed images
output_image_dir = OUTPUT_IMAGE_DIR
os.makedirs(output_image_dir, exist_ok=True)
# Function to process the CSV
def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Step 2: Validate CSV
    try:
        validate_csv(df)
    except ValueError as e:
        print(f"Validation error: {e}")
        return
    output_rows = []
    #Process each image URL
    for _, row in df.iterrows(): 
        #Generate request ID for particular request
        request_id = generate_request_id()
        print(f"Request ID: {request_id}")
        try:
            cursor = connection.cursor()
            cursor.execute(f'''
                            INSERT INTO {TABLE} (serial_no, product_name, input_image_urls, status, requestID)
                            VALUES (%s, %s, %s, %s, %s)
                            ''', (row['S.No.'], row['Product Name'], row['Input Image Urls'], 'processing', request_id))
            # print(cursor.fetchall())
        except Exception as exception:
            print("Exception occured in SQL Connection",exception)
            exit()
        input_image_urls = row['Input Image Urls'].split(',')
        output_image_urls = []
        for image_url in input_image_urls:
            image_url = image_url.strip()
            processed_image_url = process_image(image_url)
            if processed_image_url:
                output_image_urls.append(processed_image_url)
            else:
                output_image_urls.append('Error')
        output_rows.append({
            'S.No.': row['S.No.'],
            'Product Name': row['Product Name'],
            'Input Image Urls': row['Input Image Urls'],
            'Output Image Urls': ', '.join(output_image_urls)
        })
        try:
            cursor = connection.cursor()
            cursor.execute(f'''
                            UPDATE {TABLE}
                            SET status = %s, output_image_urls = %s
                            WHERE serial_no = %s
                            ''', ('Processed', ', '.join(output_image_urls), row['S.No.']))
            connection.commit()
            # print(cursor.fetchall())
        except Exception as exception:
            print("Exception occured in SQL Connection",exception)
            exit()
        print(output_rows[-1]['S.No.'])
    try:
        print(cursor.fetchall())
    finally: 
        connection.close()
    #Save the processed data to a new CSV
    output_df = pd.DataFrame(output_rows)
    output_df.to_csv(output_csv, index=False)
    print(f"Processed data saved to {output_csv}")

# Assign a unique request ID
def generate_request_id():
    return str(uuid.uuid4())

# Sample execution
if __name__ == "__main__":
    input_csv = CSV_INPUT
    output_csv = CSV_OUTPUT
    # Receive CSV and process images
    process_csv(input_csv, output_csv)