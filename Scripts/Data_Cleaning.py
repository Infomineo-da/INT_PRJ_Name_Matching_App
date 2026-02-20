import os
import re
import pandas as pd
import config



def merge_stop_words(user_stop_words: list) -> list:
    """
    Merge user stop words into LEGAL_DESIGNATORS without duplicates.
    Returns a combined list.
    """
    # [CONFIG] Replaced local LEGAL_DESIGNATORS with config.LEGAL_DESIGNATORS
    merged = set(config.LEGAL_DESIGNATORS)  # base set
    for sw in user_stop_words:
        sw = sw.strip().upper()
        if sw and sw not in merged:
            merged.add(sw)
    return sorted(merged, key=len, reverse=True)

def clean_text(name: str, stop_words: list = None) -> str:
    # 0. Ensure input is a string
    if not isinstance(name, str):
        return ""

    # 1. Convert to uppercase for consistent processing
    cleaned = name.upper()
    # 2. Perform replacements BEFORE removing special characters
    # [CONFIG] Replaced local REPLACEMENTS with config.CLEANING_REPLACEMENTS
    for old, new in config.CLEANING_REPLACEMENTS.items():
        if old == "&":
        # Special case for ampersand: allow spaces around it
            cleaned = re.sub(r'\s*&\s*', f'{new}', cleaned)
        else:
        # Normal case: match whole words (case-insensitive)
            cleaned = re.sub(r'\b' + re.escape(old) + r'\b', new, cleaned, flags=re.IGNORECASE)
        #cleaned = re.sub(r'\b' + re.escape(old) + r'\b', new, cleaned)
    
    # 3. Remove Legal Entity Designators
    # Merge stop words with LEGAL_DESIGNATORS
    merged_designators = merge_stop_words(stop_words or [])
    pattern = r'\b(' + '|'.join(re.escape(d) for d in merged_designators) + r')\b'
    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # 4. Remove all special characters
    cleaned = re.sub(r'[^A-Z0-9\s]', '', cleaned)
    # Another round of removing stop words
    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # 5. Combine consecutive single-letter words at the start of the name
    cleaned = re.sub(r'^([A-Z]\s+)+', lambda m: m.group(0).replace(' ', '') + ' ', cleaned)

    # 6. Final whitespace cleanup
    return " ".join(cleaned.split()).strip()


def create_sorted_key(text: str) -> str:
    """Create sorted version of cleaned text."""
    if not isinstance(text, str):
        return ""
    words = text.split()
    words.sort()
    return " ".join(words)


def clean_dataframe(df: pd.DataFrame, columns_to_clean: list, stop_words: list = None) -> pd.DataFrame:
    """
    Clean the dataframe and remove any rows that become empty after cleaning.
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    df = df.drop_duplicates()
    # Clean the specified columns
    for col in columns_to_clean:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame. Available: {list(df.columns)}")

        # [CONFIG] Replaced hardcoded "_cleaned" suffix
        df[f"{col}{config.SUFFIX_CLEANED}"] = df[col].apply(lambda x: clean_text(x, stop_words))
        # [CONFIG] Replaced hardcoded "_cleaned" and "_sorted" suffixes
        df[f"{col}{config.SUFFIX_SORTED}"] = df[f"{col}{config.SUFFIX_CLEANED}"].apply(create_sorted_key)

    
    # Remove rows where cleaned text is empty or just whitespace
    for col in columns_to_clean:
        df = df[
            # [CONFIG] Replaced hardcoded "_cleaned" suffix
            df[f"{col}{config.SUFFIX_CLEANED}"].notna() &
            (df[f"{col}{config.SUFFIX_CLEANED}"].str.strip() != "")
        ]
    
    # Reset index after removing empty rows
    df = df.reset_index(drop=True)
    
    # Add unique_id if it doesn't exist
    # [CONFIG] Replaced hardcoded "unique_id" column name
    if config.ID_COLUMN not in df.columns:
        df[config.ID_COLUMN] = range(len(df))
    
    return df
"""
# Test cleaning logic
df = pd.read_excel('Data/Input/Input_Data.xlsx')
# Assume file has exactly 2 columns from user
cols_to_clean = df.columns[:2].tolist()
cleaned_df = clean_dataframe(df, cols_to_clean)
cleaned_df.to_excel('Data/Cleaned_Input/cleaned_output.xlsx', index=False)
"""