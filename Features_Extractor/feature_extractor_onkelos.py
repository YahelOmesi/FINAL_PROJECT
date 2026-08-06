import pandas as pd
import re
import os
import sys

# Add the project root directory to the Python module search path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Features_Extractor.tag_normalizer import expand_tag
from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PLURAL_TAGS, SINGULAR_TAGS, PASSIVE_VERB_TAGS
)

# Define the input and output directories used by the Onkelos feature extraction process.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ONKELOS = os.path.join(base_dir, 'Data', 'csv_Onkelos')
OUTPUT_DIR = os.path.join(base_dir, 'Data', 'Ready_For_Classifier')

# Map each numeric CAL book identifier to its corresponding Targum Onkelos book name.
BOOK_MAP = {
    '51001': 'TgO_Genesis',
    '51002': 'TgO_Exodus',
    '51003': 'TgO_Leviticus',
    '51004': 'TgO_Numbers',
    '51005': 'TgO_Deuteronomy'
}


def parse_onkelos_location(url_string):
    """
    Extract the book, chapter, and verse identifiers from a CAL coordinate.

    Onkelos coordinates generally contain the book code followed by the
    chapter and verse numbers.
    """

    match = re.search(r'coord=(\d+)', str(url_string))
    if match:
        coord = match.group(1)
        if len(coord) >= 9:
            book_code = coord[0:5]
            chapter = coord[5:7]
            verse = coord[7:9]
            return pd.Series([book_code, chapter, verse])

    # Return default identifiers when the expected coordinate format is unavailable.
    return pd.Series(['0', '0', '0'])


def load_data():
    # Retrieve all available Onkelos CSV files from the configured directory.
    files = [f for f in os.listdir(DIR_ONKELOS) if f.endswith('.csv')]
    df_list = []

    # Load each CSV file and collect the successfully imported datasets.
    for file in files:
        file_path = os.path.join(DIR_ONKELOS, file)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df_list.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    # Combine all loaded Onkelos records into a single DataFrame.
    if df_list:
        return pd.concat(df_list, ignore_index=True)

    return pd.DataFrame()


def extract_features_for_group(group):
    # Retain the non-empty lexical annotations in the current verse.
    raw_tokens = [str(t) for t in group['merged_lexicon'] if pd.notnull(t)]

    # Normalize and expand compound annotations into individual grammatical tags.
    lex_tokens = [
        expanded
        for raw in group['merged_lexicon'].dropna().astype(str).str.lower().tolist()
        for t in raw.split()
        for expanded in expand_tag(t)
    ]

    # Use the number of annotated records as the word count for the current verse.
    word_count = len(raw_tokens)

    if word_count == 0:
        return pd.Series()
    
    # Count plural and singular forms for the plurality feature.
    plural_count = sum(1 for t in lex_tokens if t in PLURAL_TAGS)
    singular_count = sum(1 for t in lex_tokens if t in SINGULAR_TAGS)
    total_numbers = plural_count + singular_count

    # Count adjacent verb-to-noun and verb-to-preposition tag transitions.
    v_n_count, v_p_count = 0, 0
    for i in range(len(lex_tokens) - 1):
        if lex_tokens[i] in VERB_TAGS:
            if lex_tokens[i+1] in NOUN_TAGS:
                v_n_count += 1
            elif lex_tokens[i+1] in PREPOSITION_TAGS:
                v_p_count += 1
            
    # Calculate the transition ratios relative to the number of possible adjacent pairs.
    v_n_ratio = round(v_n_count / (word_count - 1), 4) if word_count > 1 else 0.0
    v_p_ratio = round(v_p_count / (word_count - 1), 4) if word_count > 1 else 0.0

    # Calculate the linguistic features used by the dialect classifier.
    features = {
        'emphatic_ratio': round(sum(1 for t in lex_tokens if t in EMPHATIC_STATE_TAGS) / word_count, 4),
        'absolute_ratio': round(sum(1 for t in lex_tokens if t in ABSOLUTE_STATE_TAGS) / word_count, 4),
        'function_words_ratio': round(sum(1 for t in lex_tokens if t in PREPOSITION_TAGS or t in CONJUNCTION_TAGS) / word_count, 4),
        'lexical_diversity': round(group['Lema'].nunique() / word_count, 4) if word_count > 3 else 0.5,
        'verb_ratio': round(sum(1 for t in lex_tokens if t in VERB_TAGS) / word_count, 4),
        'passive_voice_ratio': round(sum(1 for t in lex_tokens if t in PASSIVE_VERB_TAGS) / word_count, 4),        
        'plural_ratio': round(plural_count / total_numbers, 4) if total_numbers > 0 else 0.0,
        'line_length': word_count,
        'avg_word_len': round(group['text'].fillna('').astype(str).apply(len).mean(), 4),
        'v_then_noun_ratio': v_n_ratio,
        'v_then_prep_ratio': v_p_ratio
    }

    return pd.Series(features)


if __name__ == "__main__":
    print("Loading Onkelos CSVs...")
    raw_df = load_data()

    # Stop the process when no Onkelos records are available.
    if raw_df.empty:
        print("No data found! Check if the CSV files exist in Data/csv_Onkelos.")
        sys.exit()

    # Extract the book, chapter, and verse identifiers from each URL.
    print("Parsing URL coordinates (Books, Chapters, Verses)...")
    raw_df[['book_code', 'chapter', 'verse']] = raw_df['url'].apply(parse_onkelos_location)

    # Group records by verse before calculating the linguistic features.
    print("Extracting linguistic features per verse...")
    group_cols = ['book_code', 'chapter', 'verse']
    final_table = raw_df.groupby(group_cols).apply(extract_features_for_group).reset_index()

    # Add the full book name corresponding to each numeric CAL identifier.
    final_table['book_name'] = final_table['book_code'].map(BOOK_MAP).fillna('Unknown')

    # Arrange the identification columns before the extracted linguistic features.
    cols = ['book_name', 'chapter', 'verse'] + [
        c for c in final_table.columns
        if c not in ['book_code', 'book_name', 'chapter', 'verse']
    ]
    final_table = final_table[cols]

    # Create the classifier-ready output directory if it does not already exist.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the extracted feature table as a CSV file.
    output_path = os.path.join(OUTPUT_DIR, 'ready_for_classifier_onkelos.csv')
    final_table.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"Success! Features extracted for {len(final_table)} verses.")
    print(f"File saved to: {output_path}")