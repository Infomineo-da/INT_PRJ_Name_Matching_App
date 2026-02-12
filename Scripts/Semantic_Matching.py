import pandas as pd
import streamlit as st
import config
import requests

def semantic_match_blocking(unmatched_df, df2, threshold=config.SEMANTIC_DEFAULT_THRESHOLD, progress_callback=None):
    """
    Calls the external Model Service to perform semantic matching.
    """
    # 1. Identify columns (Same as your original code)
    col1_cleaned = [c for c in unmatched_df.columns if c.endswith(config.SUFFIX_CLEANED)][0]
    col2_cleaned = [c for c in df2.columns if c.endswith(config.SUFFIX_CLEANED)][0]

    # 2. Prepare text lists to send over the network
    df1_texts = unmatched_df[col1_cleaned].fillna("").astype(str).tolist()
    df2_texts = df2[col2_cleaned].fillna("").astype(str).tolist()

    if progress_callback:
        progress_callback(20, "🛰️ Sending data to Model Service...")

    # 3. Construct the request
    # Note: INFERENCE_URL will be 'http://model-service:8000/match' in Docker/K8s
    #url = config.get_env("INFERENCE_URL", "http://localhost:8000/match")
    url = config.INFERENCE_URL
    payload = {
        "queries": df1_texts,
        "corpus": df2_texts,
        "threshold": threshold
    }

    try:
        # 4. Make the network call
        response = requests.post(url, json=payload, timeout=600) # Long timeout for large files
        response.raise_for_status()
        matches_data = response.json() # This returns the matches found by the model
    except Exception as e:
        st.error(f"Failed to connect to Model Service: {e}")
        return pd.DataFrame()

    if not matches_data:
        return pd.DataFrame()

    # 5. Build the results DataFrame using the indices returned from the service
    if progress_callback:
        progress_callback(80, "✅ Processing matches...")

    df_matches = pd.DataFrame(matches_data)

    # Merge with original DataFrames (Exactly like your original code)
    result = pd.merge(
        unmatched_df.reset_index(),
        df_matches,
        left_index=True,
        right_on='df1_index'
    )

    result = pd.merge(
        result,
        df2.reset_index(drop=True),
        left_on='df2_index',
        right_index=True,
        how='left'
    )

    result['match_type'] = 'semantic'

    # Clean up temporary columns
    return result.drop(columns=['df1_index', 'df2_index'])