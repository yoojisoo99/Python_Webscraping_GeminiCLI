import pandas as pd
import numpy as np
from loguru import logger
import os
from io import StringIO # Import StringIO

# Set up loguru for debugging. Using English messages initially.
logger.add("yes24/log/debug_eda_{time}.log", rotation="500 MB", encoding="utf-8")
logger.info("Starting debug EDA script.")

# --- 1. Data Loading and Preprocessing ---
logger.info("Attempting to load and preprocess data.")
try:
    df = pd.read_csv('yes24/data/yes24_ai.csv')
    logger.info("Data loaded successfully.")
    logger.info("First 5 rows of data:")
    logger.info(df.head().to_string())

    # Rename columns for consistency with EDA instructions
    df.rename(columns={'sales_price': 'price', 'original_price': 'sale_price'}, inplace=True)

    logger.info("Data types before preprocessing:")
    buffer_before = StringIO()
    df.info(buf=buffer_before)
    logger.info(buffer_before.getvalue())

    # Data Preprocessing
    logger.info("Starting data preprocessing.")
    
    # These columns are already numeric, just ensure they are float/int
    df['price'] = df['price'].astype(float)
    df['sale_price'] = df['sale_price'].astype(float)
    
    # '리뷰 수'와 '판매지수'가 없는 경우 0으로 처리하고 숫자형으로 변환
    df['review_count'] = df['review_count'].fillna(0).astype(int)
    # Assuming 'sales_index' might not exist directly and needs to be created or derived if necessary,
    # for now, if it exists and is not numeric, fillna and convert.
    # From GEMINI.md, '판매지수' is a column, which is likely 'sales_index'
    if 'sales_index' in df.columns:
        df['sales_index'] = df['sales_index'].fillna(0).astype(int)
    else:
        logger.warning("Column 'sales_index' not found. It might be derived later or is missing.")
        df['sales_index'] = 0 # Placeholder if not present
    
    # '발행일'에서 연도, 월 추출 (using regex for robustness against encoding issues and handling NaNs)
    df['publication_year'] = df['publication_date'].str.extract(r'(\d{4})년').fillna('0').astype(int)
    df['publication_month'] = df['publication_date'].str.extract(r'(\d{1,2})월').fillna('0').astype(int)
    
    logger.info("Data preprocessing completed.")
    logger.info("Data types after preprocessing:")
    buffer_after = StringIO()
    df.info(buf=buffer_after)
    logger.info(buffer_after.getvalue())

    logger.info("Debug EDA script finished successfully with data preprocessing.")

except FileNotFoundError:
    logger.error("Error: yes24/data/yes24_ai.csv file not found.")
except Exception as e:
    logger.error(f"An unexpected error occurred during data processing: {e}")
