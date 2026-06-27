import pandas as pd
import json
import os

# רשימת חמשת חומשי תורה של תרגום אונקלוס (בדיוק לפי שמות קבצי ה-JSON שיצרנו)
onkelos_books = [
    'TgO_Genesis', 
    'TgO_Exodus', 
    'TgO_Leviticus', 
    'TgO_Numbers', 
    'TgO_Deuteronomy'
]

# רשימת העמודות המדויקת והזהה לחלוטין למבנה של התלמוד
columns = [
    'text', 'url', 'lexicon_0', 'lexicon_1', 'lexicon_2', 'lexicon_3', 'lexicon_4', 
    'meaning_0', 'meaning_1', 'meaning_2', 'meaning_3', 'text_transformed', 'Lema', 
    'merged_lexicon', 'merged_meanings'
]

# נתיבי התיקיות
# הסקריפט יושב ב-Converters, ולכן אנחנו יורדים רמה אחת אחורה לתיקיית האב ומשם נכנסים ל-Data
input_folder = '../Data/Data_Onkelos'
output_folder = '../Data/csv_Onkelos'

# יצירת תיקיית היעד (csv_Onkelos) אם היא עדיין לא קיימת
os.makedirs(output_folder, exist_ok=True)

for name in onkelos_books:
    # בניית הנתיב לקובץ ה-JSON
    json_path = f'{input_folder}/{name}.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # merged_lexicon מקבל את ה-POS המלא שלנו מ-lexicon_0
        df['merged_lexicon'] = df.get('lexicon_0', None)
        
        # חילוץ ה-Lema מתוך split_word_0 (כמו בספר חנוך - לוקח את המילה הראשונה אם יש פסיק)
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
        
        # וידוא שכל עמודות התלמוד קיימות (גם אם הן ריקות) כדי שהמודל לא יקרוס בהמשך
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # סידור העמודות בסדר המדויק של התלמוד
        df = df[columns]
        
        # בניית הנתיב לשמירת ה-CSV בתוך התיקייה החדשה
        csv_path = f'{output_folder}/{name}.csv'
        
        # שמירה בקידוד שמאפשר תמיכה טובה בעברית/ארמית באקסל
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'הצלחנו! הקובץ {name}.csv נוצר במיקום: {csv_path}')
        
    except FileNotFoundError:
        print(f'שגיאה: לא מצאתי את קובץ ה-JSON בנתיב {json_path}.')
    except Exception as e:
        print(f'שגיאה בהמרת הקובץ {name}: {e}')