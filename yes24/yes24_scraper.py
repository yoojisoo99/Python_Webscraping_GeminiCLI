
import requests
from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger
import os
import re
import time

# --- Configuration ---
LOG_DIR = "yes24/log"
DATA_DIR = "yes24/data"
CSV_PATH = os.path.join(DATA_DIR, "yes24_ai.csv")

# --- Setup Directories ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# --- Logger Setup ---
logger.add(os.path.join(LOG_DIR, "scraper_{time}.log"), rotation="500 MB")

# --- Scraping Constants ---
BASE_URL = "https://www.yes24.com/product/category/CategoryProductContents"
HEADERS = {
    'Referer': 'https://www.yes24.com/product/category/display/001001003032',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Whale/4.35.351.16 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
BASE_PARAMS = {
    'dispNo': '001001003032',
    'order': 'SINDEX_ONLY',
    'size': 24,
}

def get_text_or_none(element, selector):
    """Safely find an element and return its text, or None if not found."""
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else None

def parse_price(price_str):
    """Remove commas and convert to integer."""
    if price_str:
        return int(re.sub(r',', '', price_str))
    return 0

def parse_review_count(review_str):
    """Extract number from review count string like '(21건)'."""
    if review_str:
        match = re.search(r'\((\d+)\)', review_str)
        if match:
            return int(match.group(1))
    return 0

def get_book_data(item):
    """Extracts all necessary data from a single book item."""
    title = get_text_or_none(item, 'a.gd_name')
    author = get_text_or_none(item, 'span.info_auth > a')
    publisher = get_text_or_none(item, 'span.info_pub > a')
    publication_date = get_text_or_none(item, 'span.info_date')

    sales_price_str = get_text_or_none(item, 'strong.txt_num > em.yes_b')
    original_price_str = get_text_or_none(item, 'span.txt_num.dash > em.yes_m')
    sales_price = parse_price(sales_price_str)
    original_price = parse_price(original_price_str)

    rating_str = get_text_or_none(item, 'span.rating_grade > em.yes_b')
    rating = float(rating_str) if rating_str else 0.0

    review_count_str = get_text_or_none(item, 'span.rating_rvCount')
    review_count = parse_review_count(review_count_str)


    if not title:
        return None

    return {
        'title': title,
        'author': author,
        'publisher': publisher,
        'publication_date': publication_date,
        'sales_price': sales_price,
        'original_price': original_price,
        'rating': rating,
        'review_count': review_count,
    }


def scrape_yes24(pages_to_scrape=3):
    """Scrapes the specified number of pages from Yes24."""
    all_books = []
    logger.info(f"Starting to scrape {pages_to_scrape} pages.")

    for page in range(1, pages_to_scrape + 1):
        params = BASE_PARAMS.copy()
        params['page'] = page
        
        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info(f"Successfully fetched page {page}. Status: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('div.itemUnit')

            if not items:
                logger.warning(f"No items found on page {page}. Stopping.")
                break

            for item in items:
                book_data = get_book_data(item)
                if book_data:
                    all_books.append(book_data)
            
            # Be a good web citizen
            time.sleep(1) 

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch page {page}. Error: {e}")
            break
            
    logger.info(f"Finished scraping. Total books found: {len(all_books)}")
    return all_books

if __name__ == "__main__":
    PAGES_TO_SCRAPE = 5  # Scrape the first 5 pages
    
    books_list = scrape_yes24(pages_to_scrape=PAGES_TO_SCRAPE)

    if books_list:
        df = pd.DataFrame(books_list)
        
        # Ensure all columns are present
        all_cols = ['title', 'author', 'publisher', 'publication_date', 'sales_price', 'original_price', 'rating', 'review_count']
        for col in all_cols:
            if col not in df.columns:
                df[col] = None

        df = df[all_cols] # Reorder columns

        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
        logger.info(f"Successfully saved {len(df)} books to {CSV_PATH}")
    else:
        logger.warning("No books were scraped. CSV file not created.")

