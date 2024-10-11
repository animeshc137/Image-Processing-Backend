import requests
from PIL import Image
from io import BytesIO
import os
import uuid
from vars import *

#function to download image
def download_image(image_url):
    response = requests.get(image_url)
    return Image.open(BytesIO(response.content))
#function to compress the image

def image_compressor(img):
    output_image_path = os.path.join(OUTPUT_IMAGE_DIR, f"{uuid.uuid4()}.jpg")
    img.save(output_image_path, format="JPEG", quality=50)  # Adjust quality for compression
    return output_image_path

# Function to download and compress images by 50%
def process_image(image_url):
    try:
        # Download the image
        img = download_image(image_url)
        # Compress image by 50%
        output_image_path = image_compressor(img) # Adjust quality for compression
        return output_image_path
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None