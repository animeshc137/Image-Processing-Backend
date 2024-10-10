import pandas as pd
import os
import requests
from PIL import Image
from io import BytesIO
import uuid
import pymysql
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

#sql connection details
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

# Directory to store processed images
output_image_dir = OUTPUT_IMAGE_DIR
os.makedirs(output_image_dir, exist_ok=True)

# Function to validate CSV
def validate_csv(df):
    required_columns = ['S.No.', 'Product Name', 'Input Image Urls']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    if df.isnull().values.any():
        raise ValueError("CSV contains null values, which is not allowed")

# Function to download and compress images by 50%
def process_image(image_url):

    try:
        # Download the image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # Compress image by 50%
        output_image_path = os.path.join(output_image_dir, f"{uuid.uuid4()}.jpg")
        img.save(output_image_path, format="JPEG", quality=50)  # Adjust quality for compression

        return output_image_path
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None

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

    # Step 3: Process each image URL
    for _, row in df.iterrows():
        
        #Generate request ID for particular request
        request_id = generate_request_id()
        print(f"Request ID: {request_id}")

        try:
            cursor = connection.cursor()
            cursor.execute(f'''insert into {TABLE} (serial_no, product_name,input_image_urls,status, requestID)
                           VALUES 
                           (\'{row['S.No.']}\',\'{row['Product Name']}\',\'{row['Input Image Urls']}\','processing',\'{request_id}\')''')
            print(cursor.fetchall())
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
            cursor.execute(f'''UPDATE {TABLE}
                               SET status = 'Processed',output_image_urls = \'{', '.join(output_image_urls)}\'       
                               WHERE serial_no = {output_rows[-1]['S.No.']}''')
            cursor.execute("commit")
            print(cursor.fetchall())
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
    
    process_csv(input_csv, output_csv)


