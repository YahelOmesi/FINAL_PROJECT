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

# מעודכן: יוצאים מתיקיית Features_Extractor אל תיקיית האב ואז נכנסים ל-Data
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_SCROLLS = os.path.join(base_dir, 'Data', 'csv_Scrolls')

def parse_scroll_location(url_string):
    match = re.search(r'coord=(\d+)', str(url_string))
    if match:
        coord = match.group(1)
        if len(coord) >= 9:
            scroll_id = coord[0:5]
            column = coord[5:7]
            line = coord[7:9]
            return pd.Series([scroll_id, column, line])
    return pd.Series(['0', '0', '0']) 

def load_data():
    _files_scrolls = [f for f in os.listdir(DIR_SCROLLS) if f.endswith('.csv')] if os.path.exists(DIR_SCROLLS) else []
    
    list_scrolls = []
    print(f"Loading {len(_files_scrolls)} Scrolls tractates automatically...")
    for filename in _files_scrolls:
        full_path = os.path.join(DIR_SCROLLS, filename)
        if os.path.exists(full_path):
            df_temp = pd.read_csv(full_path)
            df_temp['scroll_name'] = filename.replace('.csv', '')
            list_scrolls.append(df_temp)
            
    df = pd.concat(list_scrolls, ignore_index=True) if list_scrolls else pd.DataFrame()

    if not df.empty:
        df[['scroll_id', 'column', 'line']] = df['url'].apply(parse_scroll_location)
    return df

def extract_features(group):
    # (הפונקציה נשארת זהה למה שהיה לך, אין צורך לשנות את המתמטיקה)
    lex_text = " ".join(group['merged_lexicon'].fillna('').astype(str).tolist()).lower()
    lex_tokens = [t for raw in lex_text.split() for t in expand_tag(raw)]
    word_count = len(group) 
    if word_count == 0: return pd.Series() 
    
    plural_count = sum(1 for t in lex_tokens if t in PLURAL_TAGS)
    singular_count = sum(1 for t in lex_tokens if t in SINGULAR_TAGS)
    total_numbers = plural_count + singular_count
    verb_indices = [i for i, t in enumerate(lex_tokens) if t in VERB_TAGS]
    verb_count_total = len(verb_indices)
    v_then_noun_count = 0
    v_then_prep_count = 0
    
    if verb_count_total > 0:
        for i in verb_indices:
            if i + 1 < len(lex_tokens):
                next_tag = lex_tokens[i+1]
                if next_tag in NOUN_TAGS:
                    v_then_noun_count += 1
                elif next_tag in PREPOSITION_TAGS:
                    v_then_prep_count += 1
        v_n_ratio = round(v_then_noun_count / verb_count_total, 4)
        v_p_ratio = round(v_then_prep_count / verb_count_total, 4)
    else:
        v_n_ratio = 0
        v_p_ratio = 0

    features = {
        'emphatic_ratio': round(sum(1 for t in lex_tokens if t in EMPHATIC_STATE_TAGS) / word_count, 4),
        'absolute_ratio': round(sum(1 for t in lex_tokens if t in ABSOLUTE_STATE_TAGS) / word_count, 4),
        'function_words_ratio': round(sum(1 for t in lex_tokens if t in PREPOSITION_TAGS or t in CONJUNCTION_TAGS) / word_count, 4),
        'lexical_diversity': round(group['Lema'].nunique() / word_count, 4) if word_count > 3 else 0.5,
        'verb_ratio': round(sum(1 for t in lex_tokens if t in VERB_TAGS) / word_count, 4),
        'passive_voice_ratio': round(sum(1 for t in lex_tokens if t in PASSIVE_VERB_TAGS) / word_count, 4),        
        'plural_ratio': round(plural_count / total_numbers, 4) if total_numbers > 0 else 0.0,
        'line_length': word_count,
        'avg_word_len': round(group['text'].astype(str).apply(len).mean(), 4),
        'v_then_noun_ratio': v_n_ratio,
        'v_then_prep_ratio': v_p_ratio
    }
    return pd.Series(features)

if __name__ == "__main__":
    raw_df = load_data()
    print("Extracting features for the Dead Sea Scrolls...")
    
    group_cols = ['scroll_name', 'column', 'line']
    final_table = raw_df.groupby(group_cols, group_keys=False).apply(extract_features).reset_index()
    
    # שימוש ב-base_dir כדי להבטיח נתיב מוחלט ומדויק לתיקייה החדשה
    output_dir = os.path.join(base_dir, 'Data', 'Ready_For_Classifier')
    os.makedirs(output_dir, exist_ok=True)
    csv_output = os.path.join(output_dir, 'ready_for_classifier_scrolls.csv')

    final_table.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"\nSuccess! File created in: {csv_output}")