import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Define the project root directory to allow access to shared data folders.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def predict_onkelos():
    # Define the input and output directories used by the prediction process.
    data_dir = os.path.join(BASE_DIR, 'Data')
    ready_dir = os.path.join(data_dir, 'Ready_For_Classifier')
    predictions_dir = os.path.join(data_dir, 'Predictions_Results')

    # Create the prediction results directory if it does not already exist.
    os.makedirs(predictions_dir, exist_ok=True)

    # Load the trained LSTM model and the fitted feature scaler.
    print("Loading LSTM model and tools...")
    model_path = os.path.join(data_dir, 'lstm_model.h5')
    scaler_path = os.path.join(data_dir, 'scaler.pkl')

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # Locate the extracted feature dataset for Targum Onkelos.
    input_path = os.path.join(ready_dir, 'ready_for_classifier_onkelos.csv')
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return
    
    print("Loading Onkelos data...")
    df = pd.read_csv(input_path, encoding='utf-8-sig')

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

    # Generate dialect prediction scores for the Onkelos dataset.
    print("Running predictions on Onkelos...")
    predictions = model.predict(X_reshaped)

    # Add the raw prediction score to each record.
    df['prediction_score'] = predictions

    # Assign scores above 0.5 to Yerushalmi and all remaining scores to Bavli.
    df['predicted_dialect'] = ['Yerushalmi' if p > 0.5 else 'Bavli' for p in predictions]

    # Save the complete prediction results as a CSV file.
    output_path = os.path.join(predictions_dir, 'onkelos_prediction_results.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Success! Predictions saved to: {output_path}")

    # Display the proportional distribution of predicted dialects for each book.
    print("\nסיכום תוצאות אונקלוס:")
    summary_onkelos = df.groupby('book_name')['predicted_dialect'].value_counts(normalize=True)
    print(summary_onkelos)


if __name__ == "__main__":
    predict_onkelos()