import pandas as pd
import re
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


# parse to (Masekhet, Page, Side, Line)
def parse_url_location(url_string):

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


def extract_features(group):

    # merge the texts for search
    lex_text = " ".join(group['merged_lexicon'].fillna('').astype(str).tolist()).lower()
    
    # Create a list of individual tags (tokens) to handle short tags like 'v' or 'p' accurately
    lex_tokens = lex_text.split()
    
    meaning_text = " ".join(group['merged_meanings'].fillna('').astype(str).tolist()).lower()
    
    word_count = len(group) # count num of words in line
    if word_count == 0: return pd.Series() # security check

    # Define tag groups based on our Lexicon investigation
    verb_tags = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', 'h)aphel', 'ethpay/w', 'ethpolal', 'quad']
    function_tags = ['prep', 'preposition', 'p', 'conj', 'conjunction', 'proclitic']
    
    # Identify where all the verbs are in the sentence
    verb_indices = [i for i, t in enumerate(lex_tokens) if t in verb_tags]
    verb_count_total = len(verb_indices)
    
    v_then_noun_count = 0
    v_then_prep_count = 0
    
    # For each verb found, check what is the NEXT tag
    if verb_count_total > 0:
        for i in verb_indices:
            # Safety check: make sure the verb is not the last word in the list
            if i + 1 < len(lex_tokens):
                next_tag = lex_tokens[i+1]
                if next_tag == 'noun':
                    v_then_noun_count += 1
                elif next_tag in function_tags:
                    v_then_prep_count += 1
        
        # Calculate ratios relative to total number of verbs
        v_n_ratio = round(v_then_noun_count / verb_count_total, 4)
        v_p_ratio = round(v_then_prep_count / verb_count_total, 4)
    else:
        v_n_ratio = 0
        v_p_ratio = 0

    

    features = {
        # שורה לדוגמא

        # Hypothesis 1: Emphatic vs Absolute 
        'emphatic_ratio': round((lex_text.count('emphatic') + lex_text.count('determined')) / word_count, 4),
        'absolute_ratio': round((lex_text.count('abs') + lex_text.count('absolute')) / word_count, 4),
        
        # Hypothesis 2: Prepositions & conjunctions 
        'function_words_ratio': round(sum(1 for t in lex_tokens if t in function_tags) / word_count, 4),
        
        # Hypothesis 3: Lexical Diversity
        # We only trust this metric if the line has more than 3 words. 
        # Otherwise, we give it a neutral 0.5 value to avoid biasing the model.
        'lexical_diversity': round(group['Lema'].nunique() / word_count, 4) if word_count > 3 else 0.5,
        
        # Hypothesis 4: Verb density
        'verb_ratio': round(sum(1 for t in lex_tokens if t in verb_tags) / word_count, 4),
        
        # Hypothesis 5: Passive Voice
        'passive_voice_ratio': round((lex_text.count('pass') + lex_text.count('passive')) / word_count, 4),
        
        # Hypothesis 6: Plurality Ratio 
        'plural_ratio': round((lex_text.count('pl') + lex_text.count('plural')) / word_count, 4),
        
        # Hypothesis 7: Sentence length
        'line_length': word_count,
        'avg_word_len': round(group['text_transformed'].astype(str).apply(len).mean(), 4),

        # Hypothesis 8: Syntactic Transitions 
        'v_then_noun_ratio': v_n_ratio,
        'v_then_prep_ratio': v_p_ratio
    }

    return pd.Series(features)


def save_styled_excel(df, output_path):
    print("⏳ מייצר קובץ אקסל מעוצב עם גבולות ופסים...")
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='ResearchData')
    
    workbook = writer.book
    worksheet = workbook['ResearchData']
    
    #styles
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
    print("⏳ מנתח 8 השערות מחקריות...")
    group_cols = ['masekhet', 'page', 'side', 'line', 'target']
    final_table = raw_df.groupby(group_cols, group_keys=False).apply(extract_features).reset_index()
    
    # Setting result paths
    excel_output = os.path.join('Data', 'ready_for_classifier.xlsx')
    csv_output = os.path.join('Data', 'ready_for_classifier.csv')


    save_styled_excel(final_table, excel_output)
    final_table.to_csv(csv_output, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ הצלחה! נוצרו שני קבצים בתיקיית Data:")
    print(f"   - אקסל מעוצב: {excel_output}")
    print(f"   - קובץ CSV למודל: {csv_output}")