import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# הגגרת נתיב האב (FINAL_PROJECT) כדי שנוכל לגשת לכל התיקיות בנוחות
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def predict_levi():
    # 1. הגדרת נתיבי עבודה
    data_dir = os.path.join(BASE_DIR, 'Data')
    ready_dir = os.path.join(data_dir, 'Ready_For_Classifier')
    predictions_dir = os.path.join(data_dir, 'Predictions_Results') 
    
    # נוודא שתיקיית היעד לתוצאות קיימת
    os.makedirs(predictions_dir, exist_ok=True)
    
    # 2. טעינת המודל והכלים שלכן (Scaler)
    print("Loading LSTM model and tools for Levi...")
    model_path = os.path.join(data_dir, 'lstm_model.h5')
    scaler_path = os.path.join(data_dir, 'scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print(f"Error: Model or Scaler missing in {data_dir}. Make sure they are trained and saved.")
        return
        
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    
    # 3. טעינת הנתונים שחילצנו מצוואת לוי (26 השורות שלכן)
    input_path = os.path.join(ready_dir, 'ready_for_classifier_levi.csv')
    if not os.path.exists(input_path):
        print(f"Error: Input file missing at {input_path}. Run feature extraction first.")
        return
        
    df = pd.read_csv(input_path)
    
    # 4. בחירת אותן העמודות שהמודל מכיר (11 הפיצ'רים הסטטיסטיים שלנו)
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    # חילוץ המטריצה של הפיצ'רים
    X = df[feature_cols].values
    
    # 5. נורמליזציה (Scaling) כמו שעשינו באימון
    X_scaled = scaler.transform(X)
    
    # 6. התאמת המימדים עבור ה-LSTM [samples, time_steps, features]
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # 7. הרצת החיזוי דרך הרשת הנוירונית
    print("Running predictions on Testament of Levi...")
    predictions = model.predict(X_reshaped)
    
    # 8. שמירת התוצאות לתוך ה-DataFrame
    df['prediction_score'] = predictions
    
    # סימון הדיאלקט לפי הציון (מתחת ל-0.5 בבלי, מעל 0.5 ירושלמי)
    # משתמשים בשם העמודה 'result' כדי שיתאים בדיוק למבנה של ה-Scrolls בדנדרוגרמה
    df['result'] = ['Yerushalmi' if p > 0.5 else 'Bavli' for p in predictions]
    
    # 9. שמירת קובץ התוצאות החדש
    output_path = os.path.join(predictions_dir, 'levi_predictions_results.csv')
    df.to_csv(output_path, index=False)
    print(f"Successfully saved predictions to {output_path}")
    
    # הדפסת סיכום קצר של החלוקה שהתקבלה בטרמינל
    print("\n--- Prediction Summary for Testament of Levi ---")
    print(df['result'].value_counts())

if __name__ == "__main__":
    predict_levi()