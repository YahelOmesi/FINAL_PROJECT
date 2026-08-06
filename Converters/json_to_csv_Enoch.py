import pandas as pd
import json
import os

# Define the consolidated Enoch JSON dataset to be converted.
files = ['Enoch_All']

# Define the output columns in the same structure used by the Talmudic datasets.
columns = [
    'text', 'url', 'lexicon_0', 'lexicon_1', 'lexicon_2', 'lexicon_3', 'lexicon_4',
    'meaning_0', 'meaning_1', 'meaning_2', 'meaning_3', 'text_transformed', 'Lema',
    'merged_lexicon', 'merged_meanings'
]

# Define and create the directory for the converted Enoch CSV file.
output_folder = '../Data/csv_Enoch'
os.makedirs(output_folder, exist_ok=True)

for name in files:
    # Construct the path to the consolidated Enoch JSON file.
    json_path = f'../Data/Data_Enoch/{name}.json'

    try:
        # Load the word-level records from the JSON file.
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Use the primary grammatical annotation as the merged lexicon value.
        df['merged_lexicon'] = df.get('lexicon_0', None)
        
        # Extract the primary lemma from the first split-word field.
        # When multiple values are present, retain only the first comma-separated value.
        if 'split_word_0' in df.columns:
            df['Lema'] = df['split_word_0'].apply(
                lambda x: str(x).split(',')[0].strip() if pd.notnull(x) else None
            )
        else:
            df['Lema'] = None
        
        # Combine all available meanings into a single pipe-separated field.
        df['merged_meanings'] = df[['meaning_0', 'meaning_1', 'meaning_2', 'meaning_3']].apply(
            lambda x: ' | '.join([str(val) for val in x if pd.notnull(val)]), axis=1
        )
        
        # Add any missing columns to preserve compatibility with the Talmudic data structure.
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # Arrange the columns in the required classifier-compatible order.
        df = df[columns]
        
        # Construct the output path for the converted CSV file.
        csv_path = f'{output_folder}/{name}.csv'
        
        # Save the converted dataset using UTF-8 encoding with a byte-order mark.
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'הצלחנו! הקובץ נוצר במיקום: {csv_path}')
        
    except FileNotFoundError:
        print(f'שגיאה: לא מצאתי את קובץ ה-JSON בנתיב {json_path}. ודאו שהשם והמיקום מדויקים.')
    except Exception as e:
        print(f'שגיאה בהמרת הקובץ {name}: {e}')