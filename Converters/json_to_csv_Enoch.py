import pandas as pd
import json
import os

# הקובץ המרוכז של ספר חנוך
files = ['Enoch_All']

# רשימת העמודות המדויקת והזהה לחלוטין למבנה של התלמוד
columns = [
    'text', 'url', 'lexicon_0', 'lexicon_1', 'lexicon_2', 'lexicon_3', 'lexicon_4', 
    'meaning_0', 'meaning_1', 'meaning_2', 'meaning_3', 'text_transformed', 'Lema', 
    'merged_lexicon', 'merged_meanings'
]

# נתיב תיקיית היעד ל-CSV - יצרתי תיקייה ייעודית לחנוך
output_folder = '../Data/csv_Enoch'
os.makedirs(output_folder, exist_ok=True)

for name in files:
    # ניווט אל תוך תיקיית חנוך החדשה שיצרנו
    json_path = f'../Data/Data_Enoch/{name}.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # merged_lexicon מקבל את ה-POS המלא שלנו מ-lexicon_0
        df['merged_lexicon'] = df.get('lexicon_0', None)
        
        # --- התיקון הקריטי ל-Lema עבור ספר חנוך ---
        # לוקחים את split_word_0 (שם נמצאת המילה), ואם יש פסיק חותכים ולוקחים רק את הראשונה
        if 'split_word_0' in df.columns:
            df['Lema'] = df['split_word_0'].apply(
                lambda x: str(x).split(',')[0].strip() if pd.notnull(x) else None
            )
        else:
            df['Lema'] = None
        
        # חיבור משמעויות עם מפריד | בדיוק כמו בתלמוד
        df['merged_meanings'] = df[['meaning_0', 'meaning_1', 'meaning_2', 'meaning_3']].apply(
            lambda x: ' | '.join([str(val) for val in x if pd.notnull(val)]), axis=1
        )
        
        # וידוא שכל עמודות התלמוד קיימות (גם אם הן ריקות) כדי שהמודל לא יקרוס
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # סידור העמודות בסדר המדויק של התלמוד
        df = df[columns]
        
        # בניית הנתיב לשמירת ה-CSV 
        csv_path = f'{output_folder}/{name}.csv'
        
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'הצלחנו! הקובץ נוצר במיקום: {csv_path}')
        
    except FileNotFoundError:
        print(f'שגיאה: לא מצאתי את קובץ ה-JSON בנתיב {json_path}. ודאו שהשם והמיקום מדויקים.')
    except Exception as e:
        print(f'שגיאה בהמרת הקובץ {name}: {e}')