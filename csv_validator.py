from vars import *
# Function to validate CSV
def validate_csv(df):
    required_columns = ['S.No.', 'Product Name', 'Input Image Urls']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    if df.isnull().values.any():
        raise ValueError("CSV contains null values, which is not allowed")