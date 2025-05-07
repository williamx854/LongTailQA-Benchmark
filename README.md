# Supplementary Material for: LongTailQA: Benchmarking LLMs and RAG Models on Disambiguated Long-Tail Entities

This supplementary material accompanies our ECAI 2025 submission and provides additional resources related to the construction and evaluation of the LongTailQA benchmark.

<p align="center">
  <img src="Images/process_overview.png" alt="Disambiguation Process" width="800"/>
  <br>
  <em>Figure 1: Overview of the disambiguation process to construct the LongTailQA datasets with disambiguated long-tail entities.</em>
</p>


## Contents:

### 1. Disambiguated Datasets
* This directory contains the final disambiguated long-tail question-answering datasets that constitute the LongTailQA benchmark.
* Files are in CSV format, including columns for the disambiguated question, the answer(s), the subject entity ID, object entity ID, relation type, relation ID
* Files included:
  * `DisambPopQA.csv`: Disambiguated long-tail subset derived from PopQA.
  * `DisambEntityQA.csv`: Disambiguated long-tail subset derived from EntityQA.
  * `DisambWITQA.csv`: Disambiguated long-tail subset derived from WITQA.

### 2. Disambiguation Prompts
* This directory contains the specific few-shot prompts provided to GPT-4o for the query-refinement and answer-filtering steps of our entity disambiguation process, as described in Section 3.2.2 of the main paper.
* Files included:
  * `disambiguation_prompt.txt`: Prompt used to incorporate Wikidata descriptions and disambiguate queries.
  * `filtering_prompt.txt`: Prompt used for the final filtering step to remove potentially answer-revealing information.

### 3. Code
* This directory contains Python scripts used for data preprocessing.
* Files included:
  * `entity_linking.py`: Script used to perform entity linking on the EntityQA dataset, identifying and mapping entity mentions to their corresponding Wikidata IDs. This was a crucial preprocessing step for establishing entity identities and enabling our disambiguation process.
  * `extract_pageviews.py`: Script used to query the Wikidata API and calculate the average monthly Wikipedia page views for entities in the EntityQA and WITQA datasets during 2023. This was used to establish a consistent popularity metric as described in Section 3.1.
  * `scrape_gold_docs.py`: Script used to query Wikidata for the corresponding Wikipedia article URL for each entity in LongTailQA and subsequently scrape the full text content used as the gold documents in the perfect retrieval experiments (Section 4.2.4).

### Note on RAG Model Implementations
The core implementations for running the Self-RAG and InstructRAG models as well as baeline models in our experiments were adapted from their respective official public repositories:
* Self-RAG: [https://github.com/AkariAsai/self-rag](https://github.com/AkariAsai/self-rag)
* InstructRAG: [https://github.com/uf-hobi-informatics-lab/InstructRAG](https://github.com/weizhepei/InstructRAG)

Our code primarily involves scripts running these models on the LongTailQA benchmark data.

