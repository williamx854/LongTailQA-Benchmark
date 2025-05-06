import requests
import pandas as pd
import time
from tqdm import tqdm
import logging
from urllib.parse import quote

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pageviews_fetch.log'),
        logging.StreamHandler()
    ]
)

YEAR = 2023
HEADERS = {
    "User-Agent": "Your header here"
}
MAX_RETRIES = 3
RETRY_DELAY = 2
RATE_LIMIT_DELAY = 0.1

def get_wikipedia_title_from_wikidata(qid, session):
    if not qid or pd.isna(qid):  # Handle empty QIDs
        return None
        
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "props": "sitelinks",
        "languages": "en"
    }

    try:
        response = session.get(url, params=params, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            entity = data.get('entities', {}).get(qid, {})
            sitelinks = entity.get('sitelinks', {})
            enwiki = sitelinks.get('enwiki', {})
            if enwiki:
                return enwiki.get('title')
        return None
    except Exception as e:
        logging.error(f"Error getting Wikipedia title for {qid}: {str(e)}")
        return None

def fetch_average_page_views(title, year, session):
    """Fetch average monthly page views for a Wikipedia page"""
    if not title:
        return None
        
    encoded_title = quote(title.replace(" ", "_"))
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{encoded_title}/monthly/{year}0101/{year}1231"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                pageviews = response.json().get('items', [])
                if not pageviews:
                    logging.warning(f"No pageviews data found for {title}")
                    return None
                
                total_views = sum(item['views'] for item in pageviews)
                num_months = len(pageviews)
                
                if num_months == 0:
                    return None
                average_views = total_views / num_months
                return round(average_views, 2)
                
            elif response.status_code == 404:
                logging.warning(f"Page not found: {title}")
                return None
                
            elif response.status_code == 429:
                logging.warning("Rate limit hit, waiting longer...")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
                
            else:
                logging.error(f"Error {response.status_code} for {title}")
                
        except Exception as e:
            logging.error(f"Request failed for {title}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            
    return None

def process_dataset(input_file, output_file):
    try:
        df = pd.read_csv(input_file)
        logging.info(f"Successfully loaded CSV with {len(df)} entries")
        
        # Add new columns for Wikipedia title and pageviews
        df['wikipedia_title'] = 'N/A'
        df['monthly_pageviews'] = 'N/A'
        
        with requests.Session() as session:
            for idx in tqdm(df.index, desc="Processing entries"):
                # Get Wikipedia title from Wikidata QID
                qid = df.loc[idx, 'wikidata_id'] 
                wiki_title = get_wikipedia_title_from_wikidata(qid, session)
                df.loc[idx, 'wikipedia_title'] = wiki_title if wiki_title else "N/A"
                
                # Get pageviews if title was found
                if wiki_title:
                    pageviews = fetch_average_page_views(wiki_title, YEAR, session)
                    df.loc[idx, 'monthly_pageviews'] = pageviews if pageviews is not None else "N/A"
                
                time.sleep(RATE_LIMIT_DELAY)
        
        # Save the updated DataFrame
        df.to_csv(output_file, index=False)
        logging.info(f"Data successfully saved to {output_file}")
        
        # Print statistics
        total_entities = len(df)
        successful_title_fetches = sum(df['wikipedia_title'] != 'N/A')
        successful_pageview_fetches = sum(df['monthly_pageviews'] != 'N/A')
        
        logging.info(f"Processing complete:")
        logging.info(f"Total entities processed: {total_entities}")
        logging.info(f"Successful title fetches: {successful_title_fetches}")
        logging.info(f"Title fetch success rate: {(successful_title_fetches/total_entities)*100:.2f}%")
        logging.info(f"Successful pageview fetches: {successful_pageview_fetches}")
        logging.info(f"Pageview fetch success rate: {(successful_pageview_fetches/total_entities)*100:.2f}%")
        
    except Exception as e:
        logging.error(f"Error processing dataset: {str(e)}")

if __name__ == "__main__":
    input_file = "your_input_file_path"  # Change to your input file path
    output_file = "your_output_file_path"  # Change to your desired output path
    
    process_dataset(input_file, output_file)