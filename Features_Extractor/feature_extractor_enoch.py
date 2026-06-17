import pandas as pd
import os
import sys

# הגדרת נתיבים - יוצאים מתיקיית Features_Extractor לתיקיית האב
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ייבוא התגיות מהקונפיגורציה שלכן (ודאו שהקובץ config.py קיים בתיקיית האב)
from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PASSIVE_VERB_TAGS
)

def extract_features_enoch():
    # 1. טעינת ה-CSV של חנוך
    input_path = os.path.join(BASE_DIR, 'Data', 'csv_Enoch', 'Enoch_All.csv')
    df = pd.read_csv(input_path)
    
    # 2. ניקוי והכנה - נחלק את הנתונים לפי scroll_name (אם יש לכן כמה מקטעים) או לקובץ אחד
    # המודל מצפה לקבוצות של שורות (כדי ליצור את ה"חלונות" של ה-LSTM)
    df['scroll_name'] = df['scroll_name'].fillna('Enoch')
    
    def calculate_row_features(group):
        word_count = len(group)
        if word_count == 0:
            return None
        
        # המרה של תגיות ה-POS לרשימה נקייה (בהתבסס על מה שחילצנו ב-lexicon_0)
        lex_tokens = [str(t).strip() for t in group['merged_lexicon'] if pd.notnull(t)]
        
        # חישוב יחסים ומדדים (בדיוק כמו במגילות)
        features = {
            'scroll_name': group['scroll_name'].iloc[0],
            'emphatic_ratio': round(sum(1 for t in lex_tokens if any(tag in t for tag in EMPHATIC_STATE_TAGS)) / word_count, 4),
            'absolute_ratio': round(sum(1 for t in lex_tokens if any(tag in t for tag in ABSOLUTE_STATE_TAGS)) / word_count, 4),
            'function_words_ratio': round(sum(1 for t in lex_tokens if any(tag in t for tag in PREPOSITION_TAGS or tag in CONJUNCTION_TAGS)) / word_count, 4),
            'lexical_diversity': round(group['Lema'].nunique() / word_count, 4) if word_count > 3 else 0.5,
            'verb_ratio': round(sum(1 for t in lex_tokens if any(tag in t for tag in VERB_TAGS)) / word_count, 4),
            'passive_voice_ratio': round(sum(1 for t in lex_tokens if any(tag in t for tag in PASSIVE_VERB_TAGS)) / word_count, 4),        
            'avg_word_len': round(group['text'].astype(str).apply(len).mean(), 4),
            'line_length': word_count
        }
        return pd.Series(features)

    # 3. גרופ-ביי לפי הבלוקים (בחנוך זה יהיה לפי ה-scroll_name, ואם תרצו - ניתן להוסיף חלוקה לעמודות/שורות אם יהיה ב-JSON)
    print("Extracting features from Enoch dataset...")
    final_features = df.groupby(['scroll_name']).apply(calculate_row_features)
    
    # 4. שמירה לתיקייה המיועדת למודל
    output_dir = os.path.join(BASE_DIR, 'Data', 'Ready_For_Classifier')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'ready_for_classifier_enoch.csv')
    final_features.to_csv(output_path, index=False)
    
    print(f"Features extracted! Data saved to: {output_path}")

if __name__ == "__main__":
    extract_features_enoch()