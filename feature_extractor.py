import pandas as pd
import re
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


# parse to (Masekhet, Page, Side, Line)
def parse_url_location(url_string):
    #זה רק הדגמה
    #define the Regex pattern to capture location details
    pattern = r'Masekhet: (\d+), Page: (\w+), Side: (\w+), Line: (\d+)' 
    match = re.search(pattern, str(url_string)) #actual search
    if match:
        return pd.Series([match.group(1), match.group(2), match.group(3), match.group(4)])
    #return default values if no match is found to prevent errors
    return pd.Series(['0', '0', '0', '0']) 

def load_data():

    #creating path to files
    path_b = os.path.join('Data', 'csv_Bavli', 'df_hor_csv.csv')
    path_y = os.path.join('Data', 'csv_Yerushalmi', 'df_yer_hor_csv.csv')
    
    #loading into DataFrame
    df_b = pd.read_csv(path_b) 
    df_y = pd.read_csv(path_y)

    #target classes
    df_b['target'], df_y['target'] = 'Bavli', 'Yerushalmi'
    
    #concatenate both dataset
    df = pd.concat([df_b, df_y], ignore_index=True)

    #extract 'url' to 4 distinct location columns
    df[['masekhet', 'page', 'side', 'line']] = df['url'].apply(parse_url_location)

    # return the final merged and processed table
    return df

# ==========================================
# 2. חילוץ מאפיינים לכל 7 ההשערות
# ==========================================
def extract_features(group):
    # איחוד הטקסטים לחיפוש
    lex_text = " ".join(group['merged_lexicon'].astype(str).tolist()).lower()
    meaning_text = " ".join(group['merged_meanings'].astype(str).tolist()).lower()
    
    word_count = len(group)
    if word_count == 0: return pd.Series()

    # חילוץ המדדים
    features = {
        # השערה 1: מצב שם העצם (Emphatic vs Absolute)
        'emphatic_ratio': round(lex_text.count('emphatic') / word_count, 4),
        'absolute_ratio': round((lex_text.count('abs') + lex_text.count('absolute')) / word_count, 4),
        
        # השערה 2: מילות תפקוד (מילות יחס וקישור)
        'function_words_ratio': round((lex_text.count('prep') + lex_text.count('conj')) / word_count, 4),
        
        # השערה 3: עושר אוצר מילים (Lexical Diversity)
        'lexical_diversity': round(group['Lema'].nunique() / word_count, 4),
        
        # השערה 4: מבנה תחבירי (צפיפות פעלים)
        'verb_ratio': round(lex_text.count('verb') / word_count, 4),
        
        # השערה 5: קול פעיל מול סביל (Passive Voice)
        'passive_voice_ratio': round((lex_text.count('pass') + lex_text.count('passive')) / word_count, 4),
        
        # השערה 6: השפעת שפות זרות (Greek vs Persian)
        'greek_latin_influence': 1 if ('greek' in meaning_text or 'latin' in meaning_text) else 0,
        'persian_influence': 1 if 'persian' in meaning_text else 0,
        
        # השערה 7: אורך משפט/שורה
        'line_length': word_count,
        'avg_word_len': round(group['text_transformed'].astype(str).apply(len).mean(), 4)
    }
    return pd.Series(features)

# ==========================================
# 3. שמירה לאקסל מעוצב עם "פסים" וגבולות
# ==========================================
def save_styled_excel(df, output_path):
    print("⏳ מייצר קובץ אקסל מעוצב עם גבולות ופסים...")
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='ResearchData')
    
    workbook = writer.book
    worksheet = workbook['ResearchData']
    
    # הגדרת סגנונות
    header_fill = PatternFill(start_color='2C3E50', end_color='2C3E50', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)
    thin_border = Border(left=Side(style='thin', color='BDC3C7'), 
                         right=Side(style='thin', color='BDC3C7'), 
                         top=Side(style='thin', color='BDC3C7'), 
                         bottom=Side(style='thin', color='BDC3C7'))
    zebra_fill = PatternFill(start_color='F2F4F4', end_color='F2F4F4', fill_type='solid')
    
    for col_num, column_cells in enumerate(worksheet.columns, 1):
        worksheet.column_dimensions[worksheet.cell(row=1, column=col_num).column_letter].width = 20
        for i, cell in enumerate(column_cells):
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')
            if i == 0:
                cell.fill = header_fill
                cell.font = header_font
            elif i % 2 == 0:
                cell.fill = zebra_fill
    writer.close()

if __name__ == "__main__":
    raw_df = load_data()
    print("⏳ מנתח 7 השערות מחקריות...")
    group_cols = ['masekhet', 'page', 'side', 'line', 'target']
    final_table = raw_df.groupby(group_cols, group_keys=False).apply(extract_features).reset_index()
    
    output = os.path.join('Data', 'ready_for_classifier.xlsx')
    save_styled_excel(final_table, output)
    print(f"\n✅ הצלחה! הקובץ נוצר בנתיב: {output}")