# python starbucks_stores\starbucks_scraper.py
import requests
import pandas as pd
from loguru import logger
import os
import json

# Loguru 설정
logger.add("starbucks_scraper_{time}.log", rotation="500 MB")

def scrape_starbucks_stores():
    all_stores = []
    
    # 01부터 17까지 p_sido_cd 반복
    for i in range(1, 18):
        p_sido_cd = str(i).zfill(2) # '01', '02', ..., '17'
        logger.info(f"Scraping stores for p_sido_cd: {p_sido_cd}")

        url = "https://www.starbucks.co.kr/store/getStore.do?r=X2D6LNU8AB"
        headers = {
            "Host": "www.starbucks.co.kr",
            "Origin": "https://www.starbucks.co.kr",
            "Referer": "https://www.starbucks.co.kr/store/store_map.do",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        payload = f"in_biz_cds=0&in_scodes=0&ins_lat=37.56682&ins_lng=126.97865&search_text=&p_sido_cd={p_sido_cd}&p_gugun_cd=&isError=true&in_distance=0&in_biz_cd=&iend=1000&searchType=C&set_date=&rndCod=9QQ7ILZT2H&all_store=0&T03=0&T01=0&T27=0&T12=0&T09=0&T30=0&T05=0&T22=0&T21=0&T36=0&T43=0&Z9999=0&T64=0&T66=0&P02=0&P10=0&P50=0&P20=0&P60=0&P30=0&P70=0&P40=0&P80=0&whcroad_yn=0&P90=0&P01=0&new_bool=0"

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
            data = response.json()
            
            stores = data.get("list", [])
            if stores:
                logger.info(f"Found {len(stores)} stores for p_sido_cd: {p_sido_cd}")
                all_stores.extend(stores)
            else:
                logger.warning(f"No stores found for p_sido_cd: {p_sido_cd}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for p_sido_cd {p_sido_cd}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for p_sido_cd {p_sido_cd}: {e}")
            logger.debug(f"Response content: {response.text[:500]}...") # Log partial response for debugging
        except Exception as e:
            logger.error(f"An unexpected error occurred for p_sido_cd {p_sido_cd}: {e}")

    if all_stores:
        df = pd.DataFrame(all_stores)
        output_dir = "starbucks_stores/data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "starbucks_ai.csv")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.success(f"Successfully scraped {len(all_stores)} stores and saved to {output_path}")
    else:
        logger.warning("No stores were scraped.")

if __name__ == "__main__":
    scrape_starbucks_stores()
