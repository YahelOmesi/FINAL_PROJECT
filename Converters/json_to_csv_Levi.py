import pandas as pd
import json
import os

# שם המגילה כפי שיופיע בעיבוד הנתונים
levi_book = ['Levi_All']

# רשימת העמודות המדויקת והזהה לחלוטין למבנה של שאר הקבצים בפרויקט
columns = [
    'text', 'url', 'lexicon_0', 'lexicon_1', 'lexicon_2', 'lexicon_3', 'lexicon_4', 
    'meaning_0', 'meaning_1', 'meaning_2', 'meaning_3', 'text_transformed', 'Lema', 
    'merged_lexicon', 'merged_meanings'
]

# נתיבי התיקיות
input_folder = '../Data/Data_Levi'
output_folder = '../Data/csv_Levi'

# יצירת תיקיית היעד אם אינה קיימת
os.makedirs(output_folder, exist_ok=True)

for name in levi_book:
    json_path = f'{input_folder}/{name}.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # בניית העמודות הנדרשות למודל
        df['merged_lexicon'] = df.get('lexicon_0', None)
        
        # חילוץ Lema - לוקחים את המילה הראשונה מ-split_word_0 אם קיימת
        if 'split_word_0' in df.columns:
            df['Lema'] = df['split_word_0'].apply(
                lambda x: str(x).split(',')[0].strip() if pd.notnull(x) else None
            )
        else:
            df['Lema'] = None
        
        # חיבור משמעויות עם מפריד |
        df['merged_meanings'] = df[['meaning_0', 'meaning_1', 'meaning_2', 'meaning_3']].apply(
            lambda x: ' | '.join([str(val) for val in x if pd.notnull(val)]), axis=1
        )
        
        # וידוא שכל עמודות המודל קיימות
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # סידור העמודות בסדר המדויק
        df = df[columns]
        
        # שמירת ה-CSV
        csv_path = f'{output_folder}/Levi_All.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Successfully created: {csv_path}")
        
    except Exception as e:
        print(f"Error processing {name}: {e}")