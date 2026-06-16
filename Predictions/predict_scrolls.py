import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import os

def predict_scrolls():
    # 1. טעינת המודל והכלים ששמרנו
    model = load_model(os.path.join('Data', 'lstm_model.h5'))
    scaler = joblib.load(os.path.join('Data', 'scaler.pkl'))
    le = joblib.load(os.path.join('Data', 'label_encoder.pkl'))
    
    # 2. טעינת נתוני המגילות
    file_path = os.path.join('Data', 'ready_for_classifier_scrolls.csv')
    df = pd.read_csv(file_path)
    
    # 3. בחירת אותן העמודות שהמודל מכיר
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    X = df[feature_cols].values
    
    # 4. נורמליזציה עם ה-Scaler המקורי (קריטי!)
    X_scaled = scaler.transform(X)
    
    # 5. עיצוב לפורמט של חלון זמן (LSTM דורש (samples, time_steps, features))
    # אנחנו נשתמש ב-reshape פשוט כדי להציג למודל שורה-שורה כרצף
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # 6. ביצוע תחזית
    predictions = model.predict(X_reshaped)
    
    # הפיכה לתווית (בבלי/ירושלמי)
    df['prediction_score'] = predictions
    df['result'] = ['Bavli' if p < 0.5 else 'Yerushalmi' for p in predictions]
    
    # 7. שמירת התוצאות
    output_path = os.path.join('Data', 'scrolls_prediction_results.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"החיזוי הושלם! התוצאות נשמרו ב-{output_path}")
    
    # סיכום קצר למסך
    print("\nסיכום תוצאות המגילות:")
    print(df.groupby('scroll_name')['result'].value_counts(normalize=True))

if __name__ == "__main__":
    predict_scrolls()