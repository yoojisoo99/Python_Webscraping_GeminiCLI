import requests
from bs4 import BeautifulSoup
from loguru import logger
# import koreanize_matplotlib # Temporarily commented out due to ModuleNotFoundError: No module named 'distutils'

# Configure loguru as per GEMINI.md
logger.add("file_{time}.log", rotation="500 MB")

class Yes24Scraper:
    def __init__(self):
        self.base_url = "https://www.yes24.com/product/category/CategoryProductContents"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Whale/4.35.351.16 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp, Selene;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.yes24.com",
            "Referer": "https://www.yes24.com/product/category/display/001001003032",
            "sec-ch-ua": '"Chromium";v="142", "Whale";v="4", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.params = {
            "dispNo": "001001003032",
            "order": "SINDEX_ONLY",
            "addOptionTp": "0",
            "page": 1,  # Start with page 1
            "size": 24,
            "statGbYn": "N",
            "viewMode": "",
            "_options": "",
            "directDelvYn": "",
            "usedTp": "0",
            "elemNo": "0",
            "elemSeq": "0",
            "seriesNumber": "0"
        }

    def fetch_page(self, page_num):
        self.params["page"] = page_num
        try:
            response = requests.get(self.base_url, headers=self.headers, params=self.params)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            logger.info(f"Successfully fetched page {page_num}")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {page_num}: {e}")
            return None

    def parse_book_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        book_list = []
        
        items = soup.find_all('div', class_='itemUnit')
        for item in items:
            title = item.find('a', class_='gd_name').text.strip() if item.find('a', class_='gd_name') else 'N/A'
            
            # Author and Publisher are in the same div, separated by '저'
            author_publisher_info = item.find('div', class_='info_pubGrp')
            author = 'N/A'
            publisher = 'N/A'
            if author_publisher_info:
                author_span = author_publisher_info.find('span', class_='info_auth')
                if author_span:
                    author_a = author_span.find('a')
                    author = author_a.text.strip() if author_a else author_span.text.replace('저', '').strip()
                
                publisher_span = author_publisher_info.find('span', class_='info_pub')
                if publisher_span:
                    publisher_a = publisher_span.find('a')
                    publisher = publisher_a.text.strip() if publisher_a else publisher_span.text.strip()

            pub_date = item.find('span', class_='info_date').text.strip() if item.find('span', class_='info_date') else 'N/A'
            
            # Price extraction
            price_info = item.find('div', class_='info_price')
            sales_price = 'N/A'
            original_price = 'N/A'
            if price_info:
                sales_price_em = price_info.find('strong', class_='txt_num').find('em', class_='yes_b')
                if sales_price_em:
                    sales_price = sales_price_em.text.replace(',', '').strip()

                original_price_em = price_info.find('span', class_='txt_num dash')
                if original_price_em:
                    original_price = original_price_em.find('em', class_='yes_m').text.replace(',', '').strip()

            # Rating extraction
            rating_info = item.find('div', class_='info_rating')
            rating = 'N/A'
            review_count = 'N/A'
            if rating_info:
                rating_grade_span = rating_info.find('span', class_='rating_grade')
                if rating_grade_span:
                    rating_em = rating_grade_span.find('em', class_='yes_b')
                    if rating_em:
                        rating = rating_em.text.strip()
                
                review_count_span = rating_info.find('span', class_='rating_rvCount')
                if review_count_span:
                    review_count_a = review_count_span.find('a')
                    if review_count_a:
                        review_count = review_count_a.text.replace('회원리뷰(', '').replace('건)', '').strip()

            book_list.append({
                'title': title,
                'author': author,
                'publisher': publisher,
                'publication_date': pub_date,
                'sales_price': sales_price,
                'original_price': original_price,
                'rating': rating,
                'review_count': review_count
            })
        return book_list

    def scrape_pages(self, num_pages=1):
        all_books = []
        for page in range(1, num_pages + 1):
            logger.info(f"Scraping page {page}...")
            html_content = self.fetch_page(page)
            if html_content:
                books_on_page = self.parse_book_data(html_content)
                all_books.extend(books_on_page)
                logger.info(f"Found {len(books_on_page)} books on page {page}")
        return all_books

if __name__ == "__main__":
    scraper = Yes24Scraper()
    # Scrape 2 pages as an example
    scraped_books = scraper.scrape_pages(num_pages=2)
    
    if scraped_books:
        # Save to CSV
        import pandas as pd
        import os

        output_dir = "yes24/data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "yes24_ai.csv")

        df = pd.DataFrame(scraped_books)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Scraped data saved to {output_file}")

        for book in scraped_books:
            logger.info(book)
        logger.info(f"Total books scraped: {len(scraped_books)}")
    else:
        logger.warning("No books were scraped.")