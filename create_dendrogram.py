import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

# Define the input files used in the comparative clustering analysis.
files = {
    # Combined feature dataset containing both Bavli and Yerushalmi tractates.
    "Talmud_Merged": "Data/ready_for_classifier.csv", 
    
    # Feature and prediction datasets for the additional Aramaic texts.
    "Enoch": "Data/Predictions_Results/enoch_prediction_results.csv",
    "Onkelos": "Data/Predictions_Results/onkelos_prediction_results.csv",
    "Scrolls": "Data/Predictions_Results/scrolls_prediction_results.csv",
    "Levi": "Data/Predictions_Results/levi_predictions_results.csv"
}

# Linguistic features shared by all input datasets and used for clustering.
common_features = [
    'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
    'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
    'plural_ratio', # Additional optional features: 'line_length', 'avg_word_len'
    'v_then_noun_ratio', 'v_then_prep_ratio'
]

dfs = []

def process_dataframe(df, name):
    """Prepare and aggregate a dataset for the hierarchical clustering analysis."""

    # Dynamically identify the column containing the textual unit name.
    if 'scroll_name' in df.columns:
        group_col = 'scroll_name'
    elif 'book_name' in df.columns:
        group_col = 'book_name'
    elif 'masekhet_name' in df.columns:
        group_col = 'masekhet_name'
    elif 'masekhet' in df.columns:
        group_col = 'masekhet'
    else:
        group_col = df.columns[0] # Use the first column as a fallback identifier.
        
    # Retain only the group identifier and the linguistic features used in the analysis.
    cols_to_use = [group_col] + common_features
    df_subset = df[cols_to_use]
    
    # Calculate the mean feature values for each tractate, book, or manuscript section.
    df_grouped = df_subset.groupby(group_col).mean()
    
    # Prefix each group name with its source to produce unambiguous dendrogram labels.
    df_grouped.index = [f"{name}_{idx}" for idx in df_grouped.index]
    return df_grouped

# Load and process each configured input dataset.
for name, file_path in files.items():
    try:
        df = pd.read_csv(file_path)
        
        # Process the combined Talmudic dataset separately to distinguish the two dialects.
        if name == "Talmud_Merged":
            print("Processing Merged Talmud file...")

            # Exclude rows with invalid, missing, or placeholder tractate identifiers.
            df = df[~df['masekhet'].astype(str).str.strip().isin(['0', '0000000', '0.0', 'nan'])]
            
            # Column containing the Bavli or Yerushalmi source label.
            type_column = 'target' 
            
            if type_column in df.columns:
                # Extract and aggregate the Bavli tractates.
                df_bavli = df[df[type_column].str.lower().str.contains('bavli', na=False)]
                if not df_bavli.empty:
                    grouped_bavli = process_dataframe(df_bavli, "Bavli")
                    dfs.append(grouped_bavli)
                    print(f"Successfully extracted Bavli with {len(grouped_bavli)} groups")
                
                # Extract and aggregate the Yerushalmi tractates.
                df_yerushalmi = df[df[type_column].str.lower().str.contains('yerushalmi', na=False)]
                if not df_yerushalmi.empty:
                    grouped_yerushalmi = process_dataframe(df_yerushalmi, "Yerushalmi")
                    dfs.append(grouped_yerushalmi)
                    print(f"Successfully extracted Yerushalmi with {len(grouped_yerushalmi)} groups")
            else:
                # Process the file as a single dataset when no dialect label column is available.
                print(f"Warning: Column '{type_column}' not found. Loading as single dataset.")
                grouped_talmud = process_dataframe(df, "Talmud")
                dfs.append(grouped_talmud)
                
        else:
            # Apply the standard aggregation procedure to each additional text dataset.
            df_grouped = process_dataframe(df, name)
            dfs.append(df_grouped)
            print(f"Successfully loaded {name} with {len(df_grouped)} groups")
            
    except Exception as e:
        print(f"An error occurred with {name}: {e}")

# Combine the processed datasets and prepare them for clustering.
if dfs:
    final_data = pd.concat(dfs).fillna(0)
    
    # Remove features with no variance across the combined dataset.
    final_data = final_data.loc[:, final_data.std() > 0]
    
    print(f"\nTotal number of rows for clustering: {len(final_data)}")
    
    if len(final_data) > 1:
        # Standardize each feature to a mean of zero and a standard deviation of one.
        final_data_normalized = (final_data - final_data.mean()) / final_data.std()
        final_data_normalized = final_data_normalized.fillna(0)

        # Calculate Euclidean distances and construct the hierarchical clustering tree.
        distance_matrix = pdist(final_data_normalized, metric='euclidean')
        Z = linkage(distance_matrix, method='ward')
        
        # Generate the dendrogram visualization.
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
        
        # Save a high-resolution copy of the dendrogram in the current working directory.
        plt.savefig("dendrogram_output.png", dpi=300, bbox_inches='tight')
        print("\nDendrogram saved successfully as 'dendrogram_output.png'")
        
        plt.show()

        # Calculate the distance of each additional text from the Bavli and Yerushalmi centroids.
        print("\n" + "="*40)
        print("POLE-DISTANCE ANALYSIS (CENTROIDS)")
        print("="*40)
        
        # Select the normalized feature vectors belonging to each Talmudic dialect.
        bavli_rows = final_data_normalized[final_data_normalized.index.str.contains('Bavli')]
        yerushalmi_rows = final_data_normalized[final_data_normalized.index.str.contains('Yerushalmi')]
        
        # Calculate the centroid representing each Talmudic dialect.
        bavli_centroid = bavli_rows.mean()
        yerushalmi_centroid = yerushalmi_rows.mean()
        
        # Define the additional text collections included in the distance analysis.
        new_corpora = ['Enoch', 'Onkelos', 'Scrolls', 'Levi']
        
        for corpus in new_corpora:
            # Select all normalized rows associated with the current text collection.
            corpus_rows = final_data_normalized[final_data_normalized.index.str.contains(corpus)]
            
            if not corpus_rows.empty:
                # Calculate the centroid of the current text collection.
                corpus_centroid = corpus_rows.mean()
                
                # Calculate its Euclidean distance from both Talmudic centroids.
                dist_to_bavli = np.linalg.norm(corpus_centroid - bavli_centroid)
                dist_to_yerushalmi = np.linalg.norm(corpus_centroid - yerushalmi_centroid)
                
                closer_to = "Yerushalmi (West)" if dist_to_yerushalmi < dist_to_bavli else "Bavli (East)"
                
                print(f"\nCorpus: {corpus}")
                print(f"  -> Distance to Bavli Centroid (Eastern Pole):  {dist_to_bavli:.4f}")
                print(f"  -> Distance to Yerushalmi Centroid (Western Pole): {dist_to_yerushalmi:.4f}")
                print(f"  >> Conclusion: Closer to {closer_to}")
        print("="*40)
    
    else:
        print("Not enough data points.")
else:
    print("No data was loaded successfully.")