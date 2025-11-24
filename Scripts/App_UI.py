import streamlit as st
import pandas as pd
import io
from Data_Cleaning import clean_dataframe
from Fuzzy_Matching import exact_match, fuzzy_match_blocking, build_final_output, map_ui_method_to_fuzzy
from Hypird_Matching import hybrid_match_blocking
from Semantic_Matching import semantic_match_blocking


st.set_page_config(page_title="InfoMatch 🔍",page_icon="Data\Square logo small 128x128 px.svg", layout="wide")


# Title
# Create two columns: a small one for the logo, a wide one for the title
col1, col2 = st.columns([1, 15]) # Adjust the ratio to fit your logo size

with col1:
    #st.write("")
    #st.write("")
    st.image("Data\Square logo small 128x128 px.svg", use_container_width = False) # Adjust width as needed

with col2:
    st.title("InfoMatch 🔍")
#st.title("**InfoMatch**🔍")

# Upload Section
uploaded_file = st.file_uploader(
"""Upload your Excel file: containing two text columns to match.\n
• **Column 1: Principal Column** (The main list)\n
• **Column 2: Match Column** (The list to be compared to the principal list)"""
, type=["xlsx", "xls"])

# Preview uploaded file
if uploaded_file:
    try:
        # Read the uploaded file
        df = pd.read_excel(uploaded_file)

        # HANDLING Empty File
        if df.empty:
            st.error("❌ The file is empty.")
            uploaded_file = None
            st.stop()
            
        # Function to check if a column is text type
        def is_text_column(series):
            return series.dtype == 'object' or series.dtype == 'string'
            
        # Get list of text columns
        text_columns = [col for col in df.columns if is_text_column(df[col])]
        
        if len(text_columns) < 2:
            st.error("❌ The file must have at least 2 text columns. Please check your data types.")
            st.write("Found text columns:", ", ".join(text_columns) if text_columns else "None")
            non_text = [f"{col} ({df[col].dtype})" for col in df.columns if col not in text_columns]
            st.write("Non-text columns:", ", ".join(non_text))
            uploaded_file = None
            st.stop()

        # Let user select which 2 columns to use
        if len(text_columns) == 2:
            df = df[text_columns]
        else:  # More than 2 text columns
            st.info("ℹ️ Please select exactly two text columns to match.")
            selected_cols = st.multiselect(
                "**Select exactly two text columns for matching:**",
                text_columns,  # Only show text columns as options
                default=text_columns[:] if len(text_columns) >= 2 else text_columns
            )
            if len(selected_cols) != 2:
                st.warning("Please select exactly two columns to proceed.")
                uploaded_file = None
                st.stop()
            else:
                # Verify selected columns are text type (double check)
                if not all(is_text_column(df[col]) for col in selected_cols):
                    st.error("❌ All selected columns must be text type.")
                    uploaded_file = None
                    st.stop()
                df = df[selected_cols]

        with st.spinner(''):
            st.write("Preview of Uploaded File:")
            st.dataframe(df.head())
        
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
    

# Matching Techniques Dropdown with Helper Icon
dropdown, score, icon = st.columns([0.80, 0.15, 0.05])  # keep dropdown and helper aligned
with dropdown:
    matching_method = st.selectbox(
        #: Click on the ℹ️ icon for details.
        "**Choose a Matching Technique**",
        ["Exact Sequence Match", "Substring Inclusion Match", "Order-Insensitive Match", "Core Word Set Match",
         "Semantic Match","Hybrid Match"]
    )
with score:
    score=st.number_input("Minimum Score Threshold", min_value=60, max_value=100, value=75, step=5)
with icon:
    # Push popover down a bit to alighn with the title
    st.markdown("<br>", unsafe_allow_html=True)
    with st.popover("ℹ️",help="Description of matching methods"):
        st.markdown("""
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
        """)

st.write(f"You selected: **{matching_method}** with Threshold of **{score}**")

# Stop Words Input
# Wrap text_area + button in a form
with st.form("stop_words_form"):
    stop_words = st.text_area(
    "**Ignore Words**: List any words to exclude from the comparison process. These words will not influence the name-matching score. Separate multiple entries with commas.",
    placeholder="e.g. station, fuel, gas, corp, ltd, inc, group, university, hospital, restaurant"
    )
    st.caption(
    "These are common or generic words that don’t change the actual name:\n"
    "- For gas stations → station, fuel, gas, etc.\n"
    "- For companies → corp, ltd, inc, co, group, etc.\n"
    "- For hospitals → hospital, clinic, medical center, etc.\n"
    "- You may also ignore common words like -> the, in, a, of, over, etc. but be careful! Sometimes they are part of the real name"
    )
    # Add spacer and submit button - uses st.write() for spacing instead of hardcoded columns
    _, col_button = st.columns([10, 1])  # Dynamic ratio that adapts to screen size
    with col_button:
        submitted = st.form_submit_button(label="Proceed..", width = "stretch")

# Process and show the provided stop words after submission
stop_words_list=[]
if submitted and len(stop_words) != 0:
    stop_words_list = [w.strip() for w in stop_words.split(",") if w.strip()]
    st.write("Ignored words:")
    st.write("",", ".join(stop_words_list))

# Process the data if file is uploaded and stop words are submitted
if uploaded_file and submitted:
    # Stage 1: Data Cleaning
    with st.spinner('Stage 1/3: Cleaning data in progress...'):
        # Get the column names
        cols = df.columns[:2].tolist()
        
        # Split into two dataframes
        df1 = df[[cols[0]]].copy()
        df2 = df[[cols[1]]].copy()
        
        # Clean each dataframe separately
        cleaned_df1 = clean_dataframe(df1, [cols[0]], stop_words=stop_words_list)
        cleaned_df2 = clean_dataframe(df2, [cols[1]], stop_words=stop_words_list)
        
        # Save both cleaned dataframes
        cleaned_df1.to_excel('Data/Cleaned_Input/cleaned_df1.xlsx', index=False)
        cleaned_df2.to_excel('Data/Cleaned_Input/cleaned_df2.xlsx', index=False)
        
        st.success('Stage 1/3: Data cleaning completed!')
        
        # Display cleaning statistics in custom format
        st.write("📊 Data Cleaning Summary:")
        
        # Calculate stats for both columns
        col1_total = df1[cols[0]].notna().sum()
        col1_cleaned = len(cleaned_df1)
        col1_removed = col1_total - col1_cleaned
        
        col2_total = df2[cols[1]].notna().sum()
        col2_cleaned = len(cleaned_df2)
        col2_removed = col2_total - col2_cleaned
        
        # Display in custom format with pipe separators
        st.write(f"**Col 1: {cols[0]}**   |   {col1_cleaned:,} Records Cleaned   |   {col1_removed:,} Duplicates Removed")
        st.write(f"**Col 2: {cols[1]}**   |   {col2_cleaned:,} Records Cleaned   |   {col2_removed:,} Duplicates Removed")

    # Stage 2: Exact Matching
    with st.spinner('Stage 2/3: Performing exact matching...'):
        try:
            matched_df, unmatched_df = exact_match(cleaned_df1, cleaned_df2)
            st.success('Stage 2/3: Exact matching completed!')
            
            # Display exact matching statistics
            st.write("📊 Exact Matching Summary:")
            #col1, col2 = st.columns(2)
            #with col1:
            primary_matches = len(matched_df[matched_df['match_type'] == 'Exact Match'])
            st.metric("Exact Matches", f"{primary_matches:,} Records")
            #with col2:
                #sorted_matches = len(matched_df[matched_df['match_type'] == 'sorted key'])
                #st.metric("Sorted Key Matches", f"{sorted_matches:,} Records")
            
            matched_df.to_excel('Data/Output/matched_exact.xlsx', index=False)
        except Exception as e:
            st.error(f"⚠️ Stage 2 failed: {e}")
            st.stop()
    # Stage 3: Advanced Matching (Fuzzy or Semantic)
    with st.spinner(f'Stage 3/3: Performing {matching_method} matching...'):
        try:
            # Set up progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if matching_method == "Semantic Match":
                status_text.text("🔄 Loading model and Analyzing your data...")
                stage3_matches = semantic_match_blocking(
                    unmatched_df,   # df1 records left unmatched
                    cleaned_df2,    # full df2 reference
                    threshold=score,    # adjust threshold as needed
                    progress_callback=lambda p, msg: (progress_bar.progress(p), status_text.text(msg))
                )
                match_type = "Semantic"
            elif matching_method == "Hybrid Match":
                stage3_matches = hybrid_match_blocking(
                unmatched_df,
                cleaned_df2,
                threshold=score,
                fuzzy_method="token_set_ratio",   # default fuzzy method
                semantic_threshold=score,         # reuse same threshold
                progress_callback=lambda p, msg: (progress_bar.progress(p), status_text.text(msg))
                )
                match_type = "Hybrid"
            else:
                status_text.text("🔄 Preparing fuzzy matching...")
                stage3_matches = fuzzy_match_blocking(
                    unmatched_df,   # df1 records left unmatched
                    cleaned_df2,    # full df2 reference
                    method=map_ui_method_to_fuzzy(matching_method),  
                    threshold=score,    # adjust threshold as needed
                    progress_callback=lambda p, msg: (progress_bar.progress(p), status_text.text(msg))
                )
                match_type = "fuzzy"
            
            # Clear progress indicators after completion
            progress_bar.empty()
            status_text.empty()
            
            st.success('Stage 3/3: Advanced matching completed!')
            
            # Display advanced matching statistics
            st.write(f"📊 {matching_method}ing Summary:")
            col1, col2, col3 = st.columns(3)
            with col1:
                advanced_matches = len(stage3_matches)
                st.metric(f"{matching_method}s", 
                         f"{advanced_matches:,} records")
            with col2:
                if not stage3_matches.empty:
                    avg_score = stage3_matches['match_score'].mean()
                    st.metric("Average Match Score", 
                            f"{avg_score:.1f}%")
            with col3:
                if not stage3_matches.empty:
                    high_quality = len(stage3_matches[stage3_matches['match_score'] >= 90])
                    st.metric("High Quality Matches (≥90%)", 
                            f"{high_quality:,} records")
            
            stage3_matches.to_excel(f'Data/Output/matched_{match_type}.xlsx', index=False)
        except Exception as e:
            st.error(f"⚠️ Stage 3 failed: {e}")
            st.stop()
    try:
        final = build_final_output(cleaned_df1,matched_df,stage3_matches)
        
        # Calculate and display total matching statistics
        st.write("📊 Overall Matching Results:")
        total_records = len(cleaned_df1)
        matched_records = len(final[final['match_type'] != 'unmatched'])
        match_rate = (matched_records / total_records * 100) if total_records > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", f"{total_records:,}")
        with col2:
            st.metric("Total Matched", f"{matched_records:,}")
        with col3:
            st.metric("Total Match Rate", f"{match_rate:.1f}%")
            
        st.write("---")  # Add a visual separator
        st.write("Final results preview:")
        st.dataframe(final.head())
        final.to_excel('Data/Output/matched_final.xlsx', index=False)

        output_buffer = io.BytesIO()
        final.to_excel(output_buffer, index=False, engine="openpyxl")
        output_buffer.seek(0)
        
        col1, col2 = st.columns([0.85, 0.15])
        with col2:
            st.download_button(
                label="📥 Download File",
                data=output_buffer,
                file_name=f'{matching_method} Results.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width = "stretch"
            )
    except Exception as e:
            st.error(f"⚠️ Final output failed: {e}")
            st.stop()