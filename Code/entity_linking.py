
import pandas as pd
import requests
from time import sleep

class WikidataLinker:
    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.cache = {}
        self.property_mappings = {
            '17': 'P17',   # country
            '19': 'P19',   # place of birth
            '20': 'P20',   # place of death
            '26': 'P26',   # spouse
            '36': 'P36',   # capital
            '40': 'P40',   # child
            '50': 'P50',   # author
            '69': 'P69',   # educated at
            '106': 'P106', # occupation
            '112': 'P112', # founded by
            '127': 'P127', # owned by
            '131': 'P131', # located in administrative territory
            '136': 'P136', # genre
            '159': 'P159', # headquarters location
            '170': 'P170', # creator
            '175': 'P175', # performer
            '176': 'P176', # manufacturer
            '264': 'P264', # record label
            '276': 'P276', # location
            '407': 'P407', # language of work
            '413': 'P413', # position held
            '495': 'P495', # country of origin
            '740': 'P740', # location of formation
            '800': 'P800'  # notable work
        }

    def get_entity_id_and_description(self, subject: str, answer: str, file_num: str) -> tuple[str, str]:
        entity_id = self.get_entity_id(subject, answer, file_num)
        
        if entity_id == "N/A":
            return ("N/A", "N/A")
            
        description = self.get_entity_description(entity_id)
        return (entity_id, description)

    def get_entity_id(self, subject: str, answer: str, file_num: str) -> str:
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": subject,
            "limit": 50
        }

        try:
            response = requests.get(self.api_url, params=params)
            results = response.json().get('search', [])
            
            matching_qids = []
            for result in results:
                if result['label'].lower() == subject.lower():
                    qid = result['id']
                    if self.check_property(qid, answer, file_num):
                        matching_qids.append(int(qid[1:]))
            
            return f"Q{min(matching_qids)}" if matching_qids else "N/A"
            
        except Exception as e:
            print(f"Error processing {subject}: {e}")
            return "N/A"

    def check_property(self, qid: str, expected_value: str, file_num: str) -> bool:
        property_id = self.property_mappings.get(file_num)
        if not property_id:
            return False
            
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": qid,
            "props": "claims"
        }
        
        try:
            response = requests.get(self.api_url, params=params)
            data = response.json()['entities'][qid]
            
            if property_id not in data.get('claims', {}):
                return False
                
            for claim in data['claims'][property_id]:
                value_id = claim['mainsnak']['datavalue']['value'].get('id')
                if value_id:
                    value_label = self.get_entity_label(value_id)
                    if value_label.lower() == expected_value.lower():
                        return True
            return False
            
        except Exception:
            return False

    def get_entity_label(self, qid: str) -> str:
        if qid in self.cache:
            return self.cache[qid]
            
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": qid,
            "props": "labels",
            "languages": "en"
        }
        
        try:
            response = requests.get(self.api_url, params=params)
            label = response.json()['entities'][qid]['labels']['en']['value']
            self.cache[qid] = label
            return label
        except Exception:
            return ""

    def get_entity_description(self, entity_id: str) -> str:
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": entity_id,
            "props": "descriptions",
            "languages": "en"
        }
        
        try:
            response = requests.get(self.api_url, params=params)
            description = response.json()['entities'][entity_id]['descriptions']['en']['value']
            return description
        except Exception:
            return "N/A"

def process_file(input_file: str, output_file: str, file_num: str):
    df = pd.read_csv(input_file)
    linker = WikidataLinker()
    
    df['wikidata_id'] = 'N/A'
    df['description'] = 'N/A'
    
    for idx, row in df.iterrows():
        if row['exact_matches'] > 0 and row['property_matches'] > 0:
            qid, description = linker.get_entity_id_and_description(row['subject'], row['answer'], file_num)
            df.at[idx, 'wikidata_id'] = qid
            df.at[idx, 'description'] = description
        print(f"Processed {row['subject']}: {df.at[idx, 'wikidata_id']} ({df.at[idx, 'description']})")
        sleep(0.1)
        
    df.to_csv(output_file, index=False)

# Process all files
file_numbers = ['19', '20', '26', '36', '40', '50', '69', '106', '112', '127', '131', 
                '136', '159', '170', '175', '176', '264', '276', '407', '413', 
                '495', '740', '800']

for num in file_numbers:
    input_file = f"F{num}_entity_counts.csv"
    output_file = f"P{num}_with_ids.csv"
    process_file(input_file, output_file, num)



