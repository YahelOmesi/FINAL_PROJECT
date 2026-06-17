import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# הגדרת תיקיית האב כעוגן
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def predict_scrolls():
    # 1. טעינת המודל והכלים - שימוש ב-BASE_DIR כדי להגיע לתיקיית Data
    data_dir = os.path.join(BASE_DIR, 'Data')
    
    model = load_model(os.path.join(data_dir, 'lstm_model.h5'))
    scaler = joblib.load(os.path.join(data_dir, 'scaler.pkl'))
    le = joblib.load(os.path.join(data_dir, 'label_encoder.pkl'))
    
    # 2. טעינת נתוני המגילות מתיקיית Ready_For_Classifier
    file_path = os.path.join(data_dir, 'Ready_For_Classifier', 'ready_for_classifier_scrolls.csv')
    df = pd.read_csv(file_path)
    
    # 3. בחירת אותן העמודות שהמודל מכיר
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    X = df[feature_cols].values
    
    # 4. נורמליזציה
    X_scaled = scaler.transform(X)
    
    # 5. עיצוב לפורמט של חלון זמן
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # 6. ביצוע תחזית
    predictions = model.predict(X_reshaped)
    
    # 7. הפיכה לתווית
    df['prediction_score'] = predictions
    df['result'] = ['Bavli' if p < 0.5 else 'Yerushalmi' for p in predictions]
    
    # 8. שמירת התוצאות לתיקיית Predictions_Results
    output_path = os.path.join(data_dir, 'Predictions_Results', 'scrolls_prediction_results.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"החיזוי הושלם! התוצאות נשמרו ב-{output_path}")
    
    # סיכום קצר למסך
    print("\nסיכום תוצאות המגילות:")
    print(df.groupby('scroll_name')['result'].value_counts(normalize=True))

if __name__ == "__main__":
    predict_scrolls()