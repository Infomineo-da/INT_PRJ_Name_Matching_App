# Name-Matching-App
This app provides an interactive solution for comparing and matching text data — such as product names, company names, or descriptions — between two sources(columns).

## Overview

**Table of Contents**:

* [Data_Cleaning](#Data_Cleaning)
* [Text_Matching](#Text_Matching)
* [Prerequisites](#prerequisites)
* [Usage](#usage)
* [Contributing](#contributing)

## Data_Cleaning
The source data goes through various steps of cleaning to ensure a smooth matching process.
* **Type Checking & Normalization** -> Ensures the input is a string.
* **Case Normalization** -> Converts everything to uppercase/lowercase for consistent matching.
* **Abbreviation Expansion** -> Expands short forms into full words (INTL → INTERNATIONAL).
* **Legal Designator Removal** -> Removes suffixes like Ltd, Inc, GmbH, DMCC etc.
* **Special Character Removal** -> Strips punctuation, symbols (&, ., -, , etc.).
* **Handling Consecutive Single-Letter Words** -> Example: "I B M Corporation" → "IBM".
* **Whitespace Normalization** -> Removes duplicate spaces, leading, and trailing spaces.
* **Sorted Key Generation (secondary matching)** -> Handles cases where word order differs.
## Text_Matching

* **FuzzyWuzzy**:

  * Python library that uses **Levenshtein distance** to measure the similarity between two strings.
  * It works well for detecting spelling differences, rearrangements, and partial matches, making it effective for cases where text values are similar but not identical.
  * Levenshtein Distance is a metric used to measure how different two strings are.It represents the minimum number of single-character edits required to transform one string into another.
  * FuzzyWuzzy has 4 main similarity **functions**:
    * **Ratio** -> When you want a strict comparison of the entire string. Best if the strings are already normalized/cleaned and order matters.
    * **Partial_Ratio** -> When one string may be embedded inside another. Good for matching short forms against long descriptions.
    * **token_sort_ratio** -> When the strings have the same words but in different orders.
    * **token_set_ratio** -> When strings share a common subset of words but one has extra info. Best for messy data with additional descriptive words.

* **Semantic Matching (SentenceTransformer)**:
  * It goes beyond string similarity by capturing the meaning of text. It transforms sentences into embeddings (vector representations) and compares them based on semantic closeness.
  * It's effective for understanding context, synonyms, and paraphrases
  * SentenceTransformers don’t look at words as fixed strings, they look at the statistical relationships between words and their contexts, learned from billions of sentences.
  * Some suggested models:
     * **all-MiniLM-L6-v2**: lightweight, fast, and general-purpose model.
     * **paraphrase-MiniLM-L12-v2**: Lightweight but better than all-MiniLM-L6-v2 for short sentences.
     * **all-mpnet-base-v2**: Very strong for short-text semantic similarity. Outperforms MiniLM on tasks like name matching.
     * **paraphrase-multilingual-MiniLM-L12-v2**: Handles cross-lingual cases.

* **LLM Matching (Gemini API)**:
  * Prompting an LLM to match the client name with a list of candidates while strictly following the given instructions.
  * API is expected to return a structured output with:
      * best_match
      * confidence_score
      * reasoning

## Prerequisites

Ensure you have Python 3.8+ installed. Install the required packages:

```bash
pip install sentence_transformers tqdm pandas torch fuzzywuzzy thefuzz
```

Additional dependencies (if used in scripts/notebooks):

* `numpy`
* `joblib`

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/Infomineo-da/Global-Text-Matching.git
   cd Global-Text-Matching
   ```

2. Navigate to the scripts folder:

   ```bash
   cd Banks_Similarity/scripts
   ```

3. Run the Names Cleaning notebook:

   ```bash
   jupyter notebook Names_Cleaning.ipynb
   ```

4. Run the different techniques available.

   ```bash
   jupyter notebook Semantic_Matching.ipynb
   jupyter notebook FuzzyWuzzy_Matching.ipynb
   ```

6. Output files will be saved as `.xlsx` files in the output folder.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add matching technique"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please follow the existing project structure and document any new data sources.
