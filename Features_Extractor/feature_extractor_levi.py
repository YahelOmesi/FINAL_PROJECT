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

# Define the input and output directories used by the Levi feature extraction process.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_LEVI = os.path.join(base_dir, 'Data', 'csv_Levi')
OUTPUT_DIR = os.path.join(base_dir, 'Data', 'Ready_For_Classifier')


def parse_levi_location(url_string):
    # Extract the column and line identifiers from the numeric CAL coordinate.
    match = re.search(r'coord=(\d+)', str(url_string))
    if match:
        coord = match.group(1)
        if len(coord) >= 13:
            column = coord[8:11]
            line = coord[11:13]
            return pd.Series([column, line])

    # Return default identifiers when the expected coordinate format is unavailable.
    return pd.Series(['000', '00'])


def extract_features_for_group(group):
    # Use the number of records in the group as the word count for the current line.
    word_count = len(group)

    # Combine the lexical annotations and expand compound values into individual tags.
    lex_tokens = [t for raw in " ".join(group['merged_lexicon'].fillna('').astype(str)).lower().split() for t in expand_tag(raw)]

    # Count all identified number forms and the subset marked as plural.
    total_numbers = len([t for t in lex_tokens if t in PLURAL_TAGS or t in SINGULAR_TAGS])
    plural_count = len([t for t in lex_tokens if t in PLURAL_TAGS])

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
        'v_then_noun_ratio': round(sum(1 for t in lex_tokens if t in VERB_TAGS) / sum(1 for t in lex_tokens if t in NOUN_TAGS), 4) if sum(1 for t in lex_tokens if t in NOUN_TAGS) > 0 else 0,
        'v_then_prep_ratio': round(sum(1 for t in lex_tokens if t in VERB_TAGS) / sum(1 for t in lex_tokens if t in PREPOSITION_TAGS), 4) if sum(1 for t in lex_tokens if t in PREPOSITION_TAGS) > 0 else 0
    }

    return pd.Series(features)


if __name__ == "__main__":
    # Load the processed word-level dataset for the Testament of Levi.
    df = pd.read_csv(os.path.join(DIR_LEVI, 'Levi_All.csv'))

    # Add the source name and extract the textual location fields required for grouping.
    df['scroll_name'] = 'Levi_All'
    df[['column', 'line']] = df['url'].apply(parse_levi_location)

    # Group records by manuscript and textual location before extracting features.
    group_cols = ['scroll_name', 'column', 'line']
    final_table = df.groupby(group_cols).apply(extract_features_for_group).reset_index()

    # Save the extracted feature table in the classifier-ready data directory.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_table.to_csv(os.path.join(OUTPUT_DIR, 'ready_for_classifier_levi.csv'), index=False, encoding='utf-8-sig')
    print("Successfully created ready_for_classifier_levi.csv")