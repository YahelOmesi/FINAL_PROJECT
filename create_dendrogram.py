import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

# 1. הגדרת הנתיבים המעודכנת
files = {
    # הקובץ המאוחד של התלמודים (בהנחה שאת מריצה מתוך תיקיית FINAL_PROJECT)
    "Talmud_Merged": "Data/ready_for_classifier.csv", 
    
    # הקבצים החדשים שלכן
    "Enoch": "Data/Predictions_Results/enoch_prediction_results.csv",
    "Onkelos": "Data/Predictions_Results/onkelos_prediction_results.csv",
    "Scrolls": "Data/Predictions_Results/scrolls_prediction_results.csv",
    "Levi": "Data/Predictions_Results/levi_predictions_results.csv"
}

# העמודות המספריות שקיימות בכל הקבצים שלך (הפיצ'רים הלשוניים)
common_features = [
    'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
    'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
    'plural_ratio', 'line_length', 'avg_word_len', 
    'v_then_noun_ratio', 'v_then_prep_ratio'
]

dfs = []

def process_dataframe(df, name):
    """פונקציית עזר לעיבוד, קיבוץ והכנת ה-DataFrame לדנדרוגרמה"""
    # 2. זיהוי דינמי של עמודת השם
    if 'scroll_name' in df.columns:
        group_col = 'scroll_name'
    elif 'book_name' in df.columns:
        group_col = 'book_name'
    elif 'masekhet_name' in df.columns:
        group_col = 'masekhet_name'
    elif 'masekhet' in df.columns:
        group_col = 'masekhet'
    else:
        group_col = df.columns[0] # גיבוי: ייקח את העמודה הראשונה
        
    # בחירת עמודת השם + המאפיינים המשותפים בלבד
    cols_to_use = [group_col] + common_features
    df_subset = df[cols_to_use]
    
    # חישוב ממוצע לקבוצה (למשל לפי מסכת או ספר)
    df_grouped = df_subset.groupby(group_col).mean()
    
    # הוספת קידומת לשם הטקסט כדי שנבדיל ביניהם בבירור בדנדרוגרמה
    df_grouped.index = [f"{name}_{idx}" for idx in df_grouped.index]
    return df_grouped

# לולאת טעינת הקבצים
for name, file_path in files.items():
    try:
        df = pd.read_csv(file_path)
        
        # טיפול מיוחד בקובץ התלמוד המאוחד
        if name == "Talmud_Merged":
            print("Processing Merged Talmud file...")
            
            # ❗❗ חשוב: ודאי ששם העמודה כאן תואם לשם האמיתי בקובץ ה-CSV שלך ❗❗
            # החליפי את 'label' בשם העמודה שמפרידה בין בבלי לירושלמי (למשל 'corpus')
            type_column = 'target' 
            
            if type_column in df.columns:
                # פיצול לבבלי (הפונקציה מחפשת את המילה 'bavli')
                df_bavli = df[df[type_column].str.lower().str.contains('bavli', na=False)]
                if not df_bavli.empty:
                    grouped_bavli = process_dataframe(df_bavli, "Bavli")
                    dfs.append(grouped_bavli)
                    print(f"Successfully extracted Bavli with {len(grouped_bavli)} groups")
                
                # פיצול לירושלמי (הפונקציה מחפשת את המילה 'yerushalmi')
                df_yerushalmi = df[df[type_column].str.lower().str.contains('yerushalmi', na=False)]
                if not df_yerushalmi.empty:
                    grouped_yerushalmi = process_dataframe(df_yerushalmi, "Yerushalmi")
                    dfs.append(grouped_yerushalmi)
                    print(f"Successfully extracted Yerushalmi with {len(grouped_yerushalmi)} groups")
            else:
                # גיבוי במקרה שאין עמודת הפרדה
                print(f"Warning: Column '{type_column}' not found. Loading as single dataset.")
                grouped_talmud = process_dataframe(df, "Talmud")
                dfs.append(grouped_talmud)
                
        else:
            # טיפול רגיל בשאר הקבצים החדשים
            df_grouped = process_dataframe(df, name)
            dfs.append(df_grouped)
            print(f"Successfully loaded {name} with {len(df_grouped)} groups")
            
    except Exception as e:
        print(f"An error occurred with {name}: {e}")

# 3. איחוד וניקוי
if dfs:
    final_data = pd.concat(dfs).fillna(0)
    
    # הסרת עמודות ללא שונות (std = 0)
    final_data = final_data.loc[:, final_data.std() > 0]
    
    print(f"\nTotal number of rows for clustering: {len(final_data)}")
    
    if len(final_data) > 1:
        # 4. נרמול (Standardization)
        final_data_normalized = (final_data - final_data.mean()) / final_data.std()
        final_data_normalized = final_data_normalized.fillna(0)

        # 5. Clustering (בניית העץ)
        distance_matrix = pdist(final_data_normalized, metric='euclidean')
        Z = linkage(distance_matrix, method='ward')
        
        # 6. שרטוט
        plt.figure(figsize=(16, 9)) 
        dendrogram(
            Z, 
            labels=final_data.index.tolist(), 
            leaf_rotation=90,
            leaf_font_size=11 
        )
        
        plt.title("Hierarchical Clustering of Aramaic Texts (Talmudic Baselines vs. New Texts)", fontsize=14)
        plt.xlabel("Text Source", fontsize=12)
        plt.ylabel("Euclidean Distance (Ward's Method)", fontsize=12)
        plt.tight_layout()
        
        # שמירת הגרף לקובץ תמונה (באיכות גבוהה) - יישמר בתיקייה שממנה מורץ הקוד
        plt.savefig("dendrogram_output.png", dpi=300, bbox_inches='tight')
        print("\nDendrogram saved successfully as 'dendrogram_output.png'")
        
        plt.show()
    else:
        print("Not enough data points.")
else:
    print("No data was loaded successfully.")