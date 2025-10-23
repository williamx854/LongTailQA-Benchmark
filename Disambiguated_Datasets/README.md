# LongTailQA Dataset

**LongTailQA** is a benchmark dataset for evaluating **Large Language Models (LLMs)** and **Retrieval-Augmented Generation (RAG)** systems on questions involving *long-tail entities* — i.e., entities that are infrequent in web corpora and model training data but essential for factual reasoning.

This repository provides the **disambiguated subsets** of three widely used open-domain QA resources, where entity ambiguity has been resolved using **Wikidata identifiers and canonical entity labels**.

---

## Overview

The dataset is designed to assess how well models can:

1. Retrieve or recall factual knowledge about rare entities.  
2. Distinguish between multiple entities sharing the same name.  
3. Maintain consistent reasoning when entity linking is required.

Each question is associated with structured metadata aligning it to **Wikidata triples** (`subject`, `predicate`, `object`) and enriched with surface forms and canonical entity labels.

All text is in **English**.

---

## Dataset Structure

The dataset is organized into three CSV files:

| File | Source Dataset | Description |
|------|----------------|--------------|
| `disambig_witqa.csv` | WITQA | General factual questions covering world knowledge and locations. |
| `disambig_popqa.csv` | PopQA | Entity-centric questions sampled from popular knowledge graphs. |
| `disambig_entityqa.csv` | EntityQA | Questions grounded in Wikidata entities, typically with biographical or factual focus. |

Each file contains one row per question with the following abstract schema:

| Column | Description |
|---------|--------------|
| `question` | Natural-language question string. |
| `answers` | One or more acceptable textual answers. |
| `subject`, `predicate`, `object` | Wikidata triple components representing the factual relation queried. |
| `subject_label`, `predicate_label`, `object_label` | Human-readable labels for the Wikidata entities and relation. |
| `triple` | The triple represented as a compact string (`subject predicate object`). |
| `aliases` / `surface_forms` | Alternative entity or answer expressions observed in text. |
| Additional metadata | Depending on the source dataset, may include IDs, relation names, popularity scores, or Wikipedia titles. |

---

## Disambiguation Process

1. Each original question was mapped to its corresponding Wikidata entities.  
2. Entity mentions were resolved to unique QIDs using entity descriptions and type constraints.  
3. Ambiguous entity names were replaced with their canonical forms.  
4. The resulting disambiguated triples were merged into the unified LongTailQA benchmark.

---

## Statistics

- **Total questions:** 6,537  
- **Distinct relation types:** 55  
- **Languages:** English  
- **Source datasets:** WITQA, PopQA, EntityQA  

---

## Anonymization & Availability

This repository has been anonymized for review purposes.  

The public release (after acceptance) will include:
- Complete dataset files with unified headers  
- Code for preprocessing and entity disambiguation  
- A detailed documentation file describing all fields and mapping scripts  

---

## License

The dataset will be released under the **Creative Commons Attribution 4.0 (CC-BY 4.0)** license, allowing free use and redistribution with proper attribution.



