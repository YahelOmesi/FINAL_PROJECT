import json
from collections import Counter

file_path = 'Targum_Onkelos.json'

try:
    print("Loading JSON file... this might take a few seconds.")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"\nTotal items (words) in file: {len(data)}")
    
    # ספירת הכמות של כל ספר
    counts = Counter(item.get('scroll_name', 'Unknown/Missing') for item in data)
    
    print("\nBreakdown by scroll:")
    for name, count in counts.items():
        print(f"{name}: {count} words")
        
except json.JSONDecodeError:
    print("Error: The file is not a valid JSON. It might be corrupted or incomplete.")
except Exception as e:
    print(f"An error occurred: {e}")