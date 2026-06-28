import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

# 1. הגדרת הנתיבים
files = {
    "Enoch": "Data/Predictions_Results/enoch_prediction_results.csv",
    "Onkelos": "Data/Predictions_Results/onkelos_prediction_results.csv",
    "Scrolls": "Data/Predictions_Results/scrolls_prediction_results.csv",
    "Levi": "Data/Predictions_Results/levi_predictions_results.csv"
}

# העמודות המספריות שקיימות בכל הקבצים שלך
common_features = [
    'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
    'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
    'plural_ratio', 'line_length', 'avg_word_len', 
    'v_then_noun_ratio', 'v_then_prep_ratio'
]

dfs = []
for name, file_path in files.items():
    try:
        df = pd.read_csv(file_path)
        
        # 2. זיהוי דינמי של עמודת השם
        if 'scroll_name' in df.columns:
            group_col = 'scroll_name'
        elif 'book_name' in df.columns:
            group_col = 'book_name'
        else:
            group_col = df.columns[0]
            
        # בחירת עמודת השם + המאפיינים המשותפים בלבד
        cols_to_use = [group_col] + common_features
        df_subset = df[cols_to_use]
        
        # חישוב ממוצע לקבוצה
        df_grouped = df_subset.groupby(group_col).mean()
        
        # הוספת קידומת לשם הטקסט כדי שנבדיל ביניהם בדנדרוגרמה
        df_grouped.index = [f"{name}_{idx}" for idx in df_grouped.index]
        
        dfs.append(df_grouped)
        print(f"Successfully loaded {name} with {len(df_grouped)} groups")
        
    except Exception as e:
        print(f"An error occurred with {name}: {e}")

# 3. איחוד וניקוי
if dfs:
    final_data = pd.concat(dfs).fillna(0)
    
    # הסרת עמודות ללא שונות (std = 0)
    final_data = final_data.loc[:, final_data.std() > 0]
    
    print(f"Number of rows after cleaning: {len(final_data)}")
    
    if len(final_data) > 1:
        # 4. נרמול
        final_data_normalized = (final_data - final_data.mean()) / final_data.std()
        final_data_normalized = final_data_normalized.fillna(0)

        # 5. Clustering
        distance_matrix = pdist(final_data_normalized, metric='euclidean')
        Z = linkage(distance_matrix, method='ward')
        
        # 6. שרטוט
        plt.figure(figsize=(14, 8))
        dendrogram(
            Z, 
            labels=final_data.index.tolist(), 
            leaf_rotation=90,
            leaf_font_size=10
        )
        plt.title("Dendrogram of Textual Similarity (Scrolls/Enoch/Onkelos)")
        plt.xlabel("Text Source")
        plt.ylabel("Euclidean Distance")
        plt.tight_layout()
        plt.show()
    else:
        print("Not enough data points.")