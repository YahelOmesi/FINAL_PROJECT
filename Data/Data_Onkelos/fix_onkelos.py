import json
import re

input_file = 'Targum_Onkelos.json'

# מילון הממיר את הקוד ב-URL לשם הספר
CODE_MAP = {
    '51001': 'TgO_Genesis',
    '51002': 'TgO_Exodus',
    '51003': 'TgO_Leviticus',
    '51004': 'TgO_Numbers',
    '51005': 'TgO_Deuteronomy'
}

# הכנת מילון שיחזיק את הרשימות לכל ספר בנפרד
books_data = {name: [] for name in CODE_MAP.values()}
missing_urls = 0

print(f"Loading {input_file}...")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        url = item.get('url', '')
        
        # חיפוש הקוד בן 5 הספרות בתוך ה-URL (אחרי המילה coord=)
        match = re.search(r'coord=(5100[1-5])', url)
        if match:
            base_code = match.group(1)
            scroll_name = CODE_MAP[base_code]
            
            # עדכון השדה החסר
            item['scroll_name'] = scroll_name
            
            # הוספה לרשימה של הספר המתאים
            books_data[scroll_name].append(item)
        else:
            missing_urls += 1

    # שמירת הנתונים ל-5 קבצים נפרדים
    for name, items in books_data.items():
        if len(items) > 0:
            output_filename = f"{name}.json"
            with open(output_filename, 'w', encoding='utf-8') as out_f:
                # שמירה בפורמט JSON קריא ומסודר
                json.dump(items, out_f, ensure_ascii=False, indent=4)
            print(f"Saved {len(items)} words to {output_filename}")

    if missing_urls > 0:
        print(f"\nWarning: Could not identify {missing_urls} words from their URLs.")
    else:
        print("\nSuccess! All words were successfully matched and split into 5 files.")

except Exception as e:
    print(f"An error occurred: {e}")