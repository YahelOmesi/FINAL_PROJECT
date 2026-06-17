import pandas as pd
import json
import os

# רשימת המגילות שלכן
scrolls = ['1QapGen_Genesis_Apocryphon', '11QtgJob_Job_Scroll']

# רשימת העמודות המדויקת והזהה לחלוטין למבנה של התלמוד
columns = [
    'text', 'url', 'lexicon_0', 'lexicon_1', 'lexicon_2', 'lexicon_3', 'lexicon_4', 
    'meaning_0', 'meaning_1', 'meaning_2', 'meaning_3', 'text_transformed', 'Lema', 
    'merged_lexicon', 'merged_meanings'
]

# נתיב תיקיית היעד ל-CSV - בתוך תיקיית האב Data
output_folder = '../Data/csv_Scrolls'
# מוודא שהתיקייה קיימת, ואם לא - יוצר אותה
os.makedirs(output_folder, exist_ok=True)

for name in scrolls:
    # בניית הנתיב לקובץ ה-JSON - ניווט אל תוך Data ואז Data_Scrolls
    json_path = f'../Data/Data_Scrolls/{name}.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # בניית העמודות הנדרשות למודל על בסיס החילוץ החדש
        df['merged_lexicon'] = df.get('lexicon_0', None)
        df['Lema'] = df.get('split_word_1', None) 
        
        # חיבור משמעויות עם מפריד | בדיוק כמו בתלמוד
        df['merged_meanings'] = df[['meaning_0', 'meaning_1', 'meaning_2', 'meaning_3']].apply(
            lambda x: ' | '.join([str(val) for val in x if pd.notnull(val)]), axis=1
        )
        
        # וידוא שכל עמודות התלמוד קיימות (גם אם הן ריקות)
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # סידור העמודות בסדר המדויק של התלמוד
        df = df[columns]
        
        # בניית הנתיב לשמירת ה-CSV בתוך Data/csv_Scrolls עם השם המדויק של המגילה
        csv_path = f'{output_folder}/{name}.csv'
        
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'הצלחנו! הקובץ נוצר במיקום: {csv_path}')
        
    except FileNotFoundError:
        print(f'שגיאה: לא מצאתי את קובץ ה-JSON בנתיב {json_path}. ודאו שהשם והמיקום מדויקים.')
    except Exception as e:
        print(f'שגיאה בהמרת המגילה {name}: {e}')