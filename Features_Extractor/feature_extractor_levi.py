import pandas as pd
import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Features_Extractor.tag_normalizer import expand_tag
from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PLURAL_TAGS, SINGULAR_TAGS, PASSIVE_VERB_TAGS
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_LEVI = os.path.join(base_dir, 'Data', 'csv_Levi')
OUTPUT_DIR = os.path.join(base_dir, 'Data', 'Ready_For_Classifier')

def parse_levi_location(url_string):
    # חילוץ קואורדינטות מה-URL כדי שיהיה לנו עמודה ושורה
    match = re.search(r'coord=(\d+)', str(url_string))
    if match:
        coord = match.group(1)
        if len(coord) >= 13:
            column = coord[8:11]
            line = coord[11:13]
            return pd.Series([column, line])
    return pd.Series(['000', '00'])

def extract_features_for_group(group):
    word_count = len(group)
    lex_tokens = [t for raw in " ".join(group['merged_lexicon'].fillna('').astype(str)).lower().split() for t in expand_tag(raw)]
    total_numbers = len([t for t in lex_tokens if t in PLURAL_TAGS or t in SINGULAR_TAGS])
    plural_count = len([t for t in lex_tokens if t in PLURAL_TAGS])
    
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
    df = pd.read_csv(os.path.join(DIR_LEVI, 'Levi_All.csv'))
    
    # התיקון הקריטי: הוספת העמודות החסרות
    df['scroll_name'] = 'Levi_All' # שם שמתאים למודל
    df[['column', 'line']] = df['url'].apply(parse_levi_location)
    
    # עכשיו הקיבוץ יעבוד כי העמודות scroll_name, column, line קיימות
    group_cols = ['scroll_name', 'column', 'line']
    final_table = df.groupby(group_cols).apply(extract_features_for_group).reset_index()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_table.to_csv(os.path.join(OUTPUT_DIR, 'ready_for_classifier_levi.csv'), index=False, encoding='utf-8-sig')
    print("Successfully created ready_for_classifier_levi.csv")