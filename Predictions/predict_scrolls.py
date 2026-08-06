import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Define the project root directory to allow access to shared data folders.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def predict_scrolls():
    # Define the data directory relative to the project root.
    data_dir = os.path.join(BASE_DIR, 'Data')

    # Load the trained LSTM model and the fitted preprocessing objects.
    model = load_model(os.path.join(data_dir, 'lstm_model.h5'))
    scaler = joblib.load(os.path.join(data_dir, 'scaler.pkl'))
    le = joblib.load(os.path.join(data_dir, 'label_encoder.pkl'))

    # Load the extracted feature dataset for the Dead Sea Scrolls.
    file_path = os.path.join(data_dir, 'Ready_For_Classifier', 'ready_for_classifier_scrolls.csv')
    df = pd.read_csv(file_path)

    # Select the linguistic features in the same order used during model training.
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]

    # Construct the feature matrix from the selected columns.
    X = df[feature_cols].values

    # Apply the same feature standardization used during model training.
    X_scaled = scaler.transform(X)

    # Reshape each feature row as a single-timestep sequence for the LSTM model.
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

    # Generate dialect prediction scores for the Dead Sea Scrolls dataset.
    predictions = model.predict(X_reshaped)

    # Add the raw prediction score and corresponding dialect label to each record.
    df['prediction_score'] = predictions
    df['result'] = ['Bavli' if p < 0.5 else 'Yerushalmi' for p in predictions]

    # Save the complete prediction results in the designated output directory.
    output_path = os.path.join(data_dir, 'Predictions_Results', 'scrolls_prediction_results.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"החיזוי הושלם! התוצאות נשמרו ב-{output_path}")

    # Display the proportional distribution of predicted dialects for each scroll.
    print("\nסיכום תוצאות המגילות:")
    print(df.groupby('scroll_name')['result'].value_counts(normalize=True))


if __name__ == "__main__":
    predict_scrolls()