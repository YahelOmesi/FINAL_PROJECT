import pandas as pd
import re
import os
import sys

# הוספת נתיב לתיקיית האב כדי שנוכל לייבא את config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PLURAL_TAGS, SINGULAR_TAGS, PASSIVE_VERB_TAGS
)

# הגדרת נתיבים
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ONKELOS = os.path.join(base_dir, 'Data', 'csv_Onkelos')
OUTPUT_DIR = os.path.join(base_dir, 'Data', 'Ready_For_Classifier')

# מילון הממיר את קידומת הספר לשם מפורש כדי שהמודל יוכל להבחין בין החומשים
BOOK_MAP = {
    '51001': 'TgO_Genesis',
    '51002': 'TgO_Exodus',
    '51003': 'TgO_Leviticus',
    '51004': 'TgO_Numbers',
    '51005': 'TgO_Deuteronomy'
}

def parse_onkelos_location(url_string):
    """
    מחלץ את המיקום המדויק מתוך ה-URL של CAL.
    באונקלוס ה-coord מורכב לרוב מ-10 ספרות, לדוגמה: 5100101311
    51001 = ספר, 01 = פרק, 31 = פסוק, 1 = חצי פסוק/מילה
    """
    match = re.search(r'coord=(\d+)', str(url_string))
    if match:
        coord = match.group(1)
        if len(coord) >= 9:
            book_code = coord[0:5]   # קוד הספר (51001-51005)
            chapter = coord[5:7]     # מספר הפרק
            verse = coord[7:9]       # מספר הפסוק
            return pd.Series([book_code, chapter, verse])
    return pd.Series(['0', '0', '0']) 

def load_data():
    files = [f for f in os.listdir(DIR_ONKELOS) if f.endswith('.csv')]
    df_list = []
    for file in files:
        file_path = os.path.join(DIR_ONKELOS, file)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df_list.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

def extract_features_for_group(group):
    # סינון ערכים ריקים
    lex_tokens = [str(t) for t in group['merged_lexicon'] if pd.notnull(t)]
    word_count = len(lex_tokens)
    
    if word_count == 0:
        return pd.Series()
        
    plural_count = sum(1 for t in lex_tokens if t in PLURAL_TAGS)
    singular_count = sum(1 for t in lex_tokens if t in SINGULAR_TAGS)
    total_numbers = plural_count + singular_count
    
    # חישוב תבניות של מילים סמוכות (Bigrams)
    v_n_count, v_p_count = 0, 0
    for i in range(len(lex_tokens) - 1):
        if lex_tokens[i] in VERB_TAGS:
            if lex_tokens[i+1] in NOUN_TAGS:
                v_n_count += 1
            elif lex_tokens[i+1] in PREPOSITION_TAGS:
                v_p_count += 1
                
    v_n_ratio = round(v_n_count / (word_count - 1), 4) if word_count > 1 else 0.0
    v_p_ratio = round(v_p_count / (word_count - 1), 4) if word_count > 1 else 0.0
    
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
    
    if raw_df.empty:
        print("No data found! Check if the CSV files exist in Data/csv_Onkelos.")
        sys.exit()
    
    print("Parsing URL coordinates (Books, Chapters, Verses)...")
    # חילוץ קוד הספר, הפרק והפסוק מתוך ה-URL
    raw_df[['book_code', 'chapter', 'verse']] = raw_df['url'].apply(parse_onkelos_location)
    
    print("Extracting linguistic features per verse...")
    # הקיבוץ נעשה לפי ספר, פרק ופסוק כדי שכל שורה בטבלה הסופית תייצג פסוק אחד בחומש
    group_cols = ['book_code', 'chapter', 'verse']
    final_table = raw_df.groupby(group_cols).apply(extract_features_for_group).reset_index()
    
    # הוספת עמודת השם המפורש של הספר, כדי שתוכלי להשוות בין החומשים בקלות!
    final_table['book_name'] = final_table['book_code'].map(BOOK_MAP).fillna('Unknown')
    
    # סידור העמודות (הסרת ה-book_code כי יש לנו כבר את השם המלא)
    cols = ['book_name', 'chapter', 'verse'] + [c for c in final_table.columns if c not in ['book_code', 'book_name', 'chapter', 'verse']]
    final_table = final_table[cols]
    
    # יצירת תיקיית היעד אם אינה קיימת
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    output_path = os.path.join(OUTPUT_DIR, 'ready_for_classifier_onkelos.csv')
    final_table.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"Success! Features extracted for {len(final_table)} verses.")
    print(f"File saved to: {output_path}")