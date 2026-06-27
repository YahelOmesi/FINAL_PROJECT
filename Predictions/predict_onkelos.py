import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# הגדרת נתיב האב (FINAL_PROJECT) כדי שנוכל לגשת לכל התיקיות בנוחות
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def predict_onkelos():
    # 1. הגדרת נתיבים
    data_dir = os.path.join(BASE_DIR, 'Data')
    ready_dir = os.path.join(data_dir, 'Ready_For_Classifier')
    predictions_dir = os.path.join(data_dir, 'Predictions_Results') 
    
    # נוודא שתיקיית התוצאות קיימת
    os.makedirs(predictions_dir, exist_ok=True)
    
    # 2. טעינת המודל והכלים שלכן (Scaler)
    print("Loading LSTM model and tools...")
    model_path = os.path.join(data_dir, 'lstm_model.h5')
    scaler_path = os.path.join(data_dir, 'scaler.pkl')
    
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    
    # 3. טעינת הנתונים שחילצנו מאונקלוס
    input_path = os.path.join(ready_dir, 'ready_for_classifier_onkelos.csv')
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return
        
    print("Loading Onkelos data...")
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    
    # 4. בחירת אותן העמודות שהמודל מכיר (11 הפיצ'רים הסטטיסטיים שלנו)
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    # חילוץ המטריצה של הפיצ'רים מתוך הדאטה-פריים
    X = df[feature_cols].values
    
    # 5. נורמליזציה (Scaling) כמו שעשינו באימון המודל
    X_scaled = scaler.transform(X)
    
    # 6. התאמת המימדים עבור ה-LSTM [samples, time_steps, features]
    # מכיוון שהמודל צופה חלון זמן (time_step) של 1, אנחנו מעצבים את המערך בהתאם
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # 7. הרצת החיזוי
    print("Running predictions on Onkelos...")
    predictions = model.predict(X_reshaped)
    
    # 8. שמירת התוצאות לתוך ה-DataFrame
    df['prediction_score'] = predictions
    
    # סימון הדיאלקט לפי הציון: 
    # מתחת ל-0.5 נסווג כבבלי (Bavli)
    # מעל 0.5 נסווג כירושלמי / גלילי (Yerushalmi)
    df['predicted_dialect'] = ['Yerushalmi' if p > 0.5 else 'Bavli' for p in predictions]
    
    # 9. שמירת קובץ התוצאות הסופי
    output_path = os.path.join(predictions_dir, 'onkelos_prediction_results.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Success! Predictions saved to: {output_path}")

if __name__ == "__main__":
    predict_onkelos()