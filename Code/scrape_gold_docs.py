import pandas as pd
import time
import random
import requests
import csv
import re
from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON

# Load the datasets
pqa = pd.read_csv("popqa_original_ecai.csv")
eq = pd.read_csv("entity_questions_long_tail.csv")
witqa = pd.read_csv("witqa_long_tail.csv")

# Set up SPARQL connection
endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)
sparql.agent = "MyResearchBot (uwe.hadler@l3s.de)"

def execute_sparql_query(query, retries=3, delay=5):
    for attempt in range(retries):
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            return sparql.query().convert()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            else:
                raise

get_entid_from_url = lambda x: x.split("/")[-1]

# Function to extract content from Wikipedia pages
def extract_wikipedia_content(wikipedia_url):  
    try:
        response = requests.get(wikipedia_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Use main content div to avoid irrelevant parts
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return {"full_page": "Content division not found.", "introduction": "Content division not found."}

        # Extract paragraph tags
        paragraphs = content_div.find_all('p')

        intro_paragraphs = []
        full_paragraphs = []

        # Get, clean and append text (whole page + introduction only)
        for idx, para in enumerate(paragraphs):
            text = para.get_text().strip()
            clean_text = re.sub(r'\[\d+\]', '', text)  # Remove inline citations like [1]
            if clean_text:
                full_paragraphs.append(clean_text)
                if idx==0:
                    intro_paragraphs.append(clean_text)

        return {
            "full_page": '\n'.join(full_paragraphs) if full_paragraphs else "Error: No meaningful content found.",
            "introduction": '\n'.join(intro_paragraphs) if intro_paragraphs else "Error: Introduction not found."
        }

    except NameError as e:
        print(f"Failed to get webpage, missing URL: {e}")
        return {"full_page": "n/a", "introduction": "n/a"}
    except requests.RequestException as e:
        print(f"Failed to fetch Wikipedia page: {e}")
        return {"full_page": "Error fetching content.", "introduction": "Error fetching content."}

# Function to gather Wikipedia URLs for entities
def gather_wikipedia_urls(fname, uris):
    # Write results to tsv while scraping to work around timeouts / bans
    with open(fname, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['URI', 'Wikipedia URI', 'Description', 'Label'])

        # Iterate over the list of URIs
        for uri in uris:
            # Query for entity name, short description + wikipedia URL
            query = f"""
            SELECT ?wikipediaURI ?description ?label WHERE {{

            OPTIONAL {{
                ?wikipediaURI schema:about wd:{uri} .
                ?wikipediaURI schema:isPartOf <https://en.wikipedia.org/>.
            }}

            OPTIONAL {{
                wd:{uri} schema:description ?description .
                FILTER(LANG(?description) = "en") .
            }}

            OPTIONAL {{
                wd:{uri} rdfs:label ?label .
                FILTER(LANG(?label) = "en") .
            }}

            }}
            """
        
            # Execute query
            try:
                results = execute_sparql_query(query)
            
                # Extract and write results to tsv
                for result in results["results"]["bindings"]:
                    wikipedia_uri = result.get("wikipediaURI", {}).get("value", "")
                    description = result.get("description", {}).get("value", "")
                    label = result.get("label", {}).get("value", "")
                
                    writer.writerow([f'https://www.wikidata.org/wiki/{uri}', wikipedia_uri, description, label])

                # Random backoff to avoid hitting rate limit / timeouts
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Failed to fetch data for {uri}: {e}")

    print(f"Results saved to {fname}")

# Function to crawl Wikipedia pages and extract content
def crawl_wikipedia_pages(in_fname, out_fname):
    df = pd.read_csv(in_fname, sep='\t', encoding='utf-8')
    
    full_texts = []
    intro_texts = []
    
    # Read and extract wikipedia page for each instance
    for _, row in df.iterrows():
        wikipedia_uri = str(row.get('Wikipedia URI', '')).strip()
        
        if wikipedia_uri:
            texts = extract_wikipedia_content(wikipedia_uri)
        else:
            texts = {"full_page": "n/a", "introduction": "n/a"}
        
        full_texts.append(texts["full_page"])
        intro_texts.append(texts["introduction"])
    
    # Append to df and save to new tsv
    df['fullpage_text'] = full_texts
    df['intro_text'] = intro_texts
    df.to_csv(out_fname, sep='\t', index=False, encoding='utf-8')
    
    print(f"Enriched results saved to {out_fname}")

# Process PopQA data
print("Processing PopQA data...")
subject_uris = [get_entid_from_url(x) for x in pqa["s_uri"]]
gather_wikipedia_urls(fname="pqa_results.tsv", uris=subject_uris)
crawl_wikipedia_pages(in_fname="pqa_results.tsv", out_fname="pqa_enriched_results.tsv")
df = pd.read_csv("pqa_enriched_results.tsv", sep='\t', encoding='utf-8')
df.to_excel("pqa_enriched_results.xlsx")
print(f"PopQA processing complete. Total entries: {len(pqa)}")

# Process EntityQA data
print("Processing EntityQA data...")
eq_uris = eq["wikidata_id"]
gather_wikipedia_urls(fname="eq_results.tsv", uris=eq_uris)
crawl_wikipedia_pages(in_fname="eq_results.tsv", out_fname="eq_enriched_results.tsv")
df = pd.read_csv("eq_enriched_results.tsv", sep='\t', encoding='utf-8')
df.to_excel("eq_enriched_results.xlsx")
print(f"EntityQA processing complete. Total entries: {len(eq)}")

# Process WITQA data
print("Processing WITQA data...")
witqa_uris = witqa["subject"]
gather_wikipedia_urls(fname="witqa_results.tsv", uris=witqa_uris)
crawl_wikipedia_pages(in_fname="witqa_results.tsv", out_fname="witqa_enriched_results.tsv")
df = pd.read_csv("witqa_enriched_results.tsv", sep='\t', encoding='utf-8')
df.to_excel("witqa_enriched_results.xlsx")
print(f"WITQA processing complete. Total entries: {len(witqa)}")