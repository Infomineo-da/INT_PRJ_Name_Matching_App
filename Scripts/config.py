# config.py
import os

# Helper to look for Kubernetes ConfigMap values (Environment Variables)
def get_env(key, default):
    return os.getenv(key, str(default))



# ==========================================
# Extracted from: APP UI
# ==========================================


# --- Application Settings ---
APP_TITLE = "InfoMatch 🔍"
APP_ICON_PATH = "Data/Square logo small 128x128 px.svg"
APP_LAYOUT = "wide"

# --- File Handling ---
ALLOWED_EXTENSIONS = ["xlsx", "xls"]

# --- Matching Configuration ---
MATCHING_METHODS = [
    "Exact Sequence Match",
    "Substring Inclusion Match",
    "Order-Insensitive Match",
    "Core Word Set Match",
    "Semantic Match",
    "Hybrid Match"
]

# Score Thresholds
SCORE_MIN = 60
SCORE_MAX = 100
SCORE_DEFAULT = 75
SCORE_STEP = 5

# Metrics
HIGH_QUALITY_THRESHOLD = 90  # Used for "High Quality" metric display

# Hybrid Match Specifics
HYBRID_FUZZY_METHOD_DEFAULT = "token_set_ratio"

# --- UI Text & Descriptions ---
STOP_WORDS_PLACEHOLDER = "e.g. station, fuel, gas, corp, ltd, inc, group, university, hospital, restaurant"

STOP_WORDS_CAPTION = (
    "These are common or generic words that don’t change the actual name:\n"
    "- For gas stations → station, fuel, gas, etc.\n"
    "- For companies → corp, ltd, inc, co, group, etc.\n"
    "- For hospitals → hospital, clinic, medical center, etc.\n"
    "- You may also ignore common words like -> the, in, a, of, over, etc. but be careful! Sometimes they are part of the real name"
)

HELP_TEXT_MARKDOWN = """
#### **Choose the matching methodology**
##### **FuzzyWuzzy**
- **Exact Sequence Match**: Performs a strict, full-string comparison. This method is ideal when both strings are already normalized and the exact order of characters matters.
- **Substring Inclusion Match**: Detects cases where one string is embedded within another, such as matching abbreviations, truncated forms, or shorter references to longer text descriptions.
- **Order-Insensitive Match**: Evaluates similarity based on the same set of words appearing in different orders. Useful when word arrangement varies but the overall content remains equivalent.
- **Core Word Set Match**: Focuses on the shared subset of words between two strings, while ignoring additional or extraneous terms. Well-suited for noisy or descriptive data where extra details may be present.
##### **Semantic Matching**
- **SentenceTransformer**: It's effective for understanding context, synonyms, and paraphrases. learned from billions of sentences.
##### **Minimum Score Threshold**
The Minimum Score Threshold defines the lowest similarity score required for two text values to be considered a valid match.
It acts as a filter to exclude weak or irrelevant matches, ensuring that only results with sufficient similarity are accepted.
- **Range**: 60% (minimum) and above
- **Guideline**: The higher the threshold, the stricter and more accurate the matching results will be.
- **Example**: A threshold of 60% allows moderately similar text to qualify as a match, while 85–90% ensures only very closely related text pairs are considered.
##### **Disclaimer**: 
Sentence transformers capture semantic meaning but may over-match by treating related concepts as equivalent, leading to false positives. Fuzzy matching, on the other hand, focuses on text similarity but may under-match when the same concept is expressed in different wording.
"""

# ==========================================
# Extracted from: Data_Cleaning.py
# ==========================================

# Standard Legal Designators to remove
LEGAL_DESIGNATORS = [
    'PRIVATE LIMITED', 'PVT LTD', 'LIMITED', 'LTD', 'INCORPORATED', 'INC',
    'CORPORATION', 'CORP', 'PLC', 'LLC', 'LLP', 'LP', 'COMPANY', 'CO',
    'GMBH', 'AG', 'SA', 'SL', 'SARL', 'NV', 'BV',
    'PUBLIC LIMITED COMPANY', 'SAE', 'SAOG', 'BSC', 'PJSC', 'PSC', 'KSC',
    'WLL', 'FZE', 'FZC', 'DMCC'
]

# Word Replacements (Abbreviations -> Full Words)
CLEANING_REPLACEMENTS = {
    '&': ' AND ',
    'INTL': 'INTERNATIONAL',
    'MFG': 'MANUFACTURING',
    'TECH': 'TECHNOLOGY',
    'SOLNS': 'SOLUTIONS',
    'SVCS': 'SERVICES',
    'MKTG': 'MARKETING',
    'TRDG': 'TRADING'
}

# Column Naming Constants & Suffixes
SUFFIX_CLEANED = "_cleaned"
SUFFIX_SORTED = "_sorted"
ID_COLUMN = "unique_id"


# ==========================================
# Extracted from: Fuzzy_Matching.py
# ==========================================

# Mapping UI names to FuzzyWuzzy functions
FUZZY_METHOD_MAPPING = {
    "Exact Sequence Match": "ratio",
    "Substring Inclusion Match": "partial_ratio",
    "Order-Insensitive Match": "token_sort_ratio",
    "Core Word Set Match": "token_set_ratio"
}

# Fuzzy Matching Defaults
FUZZY_DEFAULT_METHOD = "token_set_ratio"
FUZZY_DEFAULT_THRESHOLD = 80

# Blocking Configuration
BLOCK_PREFIX_LENGTH = 4  # Number of characters to use for blocking keys


# ==========================================
# Extracted from: Hypird_Matching.py
# ==========================================

# Hybrid Matching Default Settings
HYBRID_DEFAULT_THRESHOLD = 80
HYBRID_SEMANTIC_THRESHOLD = 75

# ==========================================
# Extracted from: Semantic_Matching.py
# ==========================================

# NLP Model Configuration
SEMANTIC_MODEL_NAME = 'all-mpnet-base-v2'

# Default Threshold for Semantic Matching
SEMANTIC_DEFAULT_THRESHOLD = 75

