import sys
import os
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# הגדרת נתיב האב כדי שנוכל לגשת לכל התיקיות בנוחות
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def predict_enoch():
    # 1. הגדרת נתיבים
    data_dir = os.path.join(BASE_DIR, 'Data')
    ready_dir = os.path.join(data_dir, 'Ready_For_Classifier')
    
    # תיקיית היעד בתוך Data
    predictions_dir = os.path.join(data_dir, 'Predictions_Results') 
    os.makedirs(predictions_dir, exist_ok=True)
    
    # 2. טעינת המודל והכלים שלכן (Scaler)
    print("Loading LSTM model and tools...")
    model = load_model(os.path.join(data_dir, 'lstm_model.h5'))
    scaler = joblib.load(os.path.join(data_dir, 'scaler.pkl'))
    
    # 3. טעינת הנתונים שחילצנו מחנוך
    input_path = os.path.join(ready_dir, 'ready_for_classifier_enoch.csv')
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return
        
    print("Loading Enoch features...")
    df = pd.read_csv(input_path)
    
    # 4. בחירת העמודות של הפיצ'רים בלבד (חייב להיות בדיוק כמו באימון)
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', \
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', \
        'plural_ratio', 'line_length', 'avg_word_len', \
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    # חילוץ המטריצה של הפיצ'רים
    X = df[feature_cols].values
    
    # 5. נורמליזציה (Scaling) כמו שעשינו באימון
    X_scaled = scaler.transform(X)
    
    # 6. התאמת המימדים עבור ה-LSTM [samples, time_steps, features]
    X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    
    # 7. הרצת החיזוי
    print("Running predictions on Enoch...")
    predictions = model.predict(X_reshaped)
    
    # 8. שמירת התוצאות לתוך ה-DataFrame
    df['prediction_score'] = predictions
    # סימון הדיאלקט לפי הציון (מתחת ל-0.5 בבלי, מעל 0.5 ירושלמי - בהתאמה לקוד שלכן)
    df['predicted_dialect'] = ['Yerushalmi' if p > 0.5 else 'Bavli' for p in predictions]
    
    # 9. שמירת קובץ התוצאות הסופי
    output_path = os.path.join(predictions_dir, 'enoch_prediction_results.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # הדפסת הודעת ההצלחה בפורמט המבוקש בעברית
    print(f"החיזוי הושלם! התוצאות נשמרו ב-{output_path}")
    
    # 10. הדפסת סיכום באחוזים/פרופורציות (normalize=True) בדיוק כמו במגילות!
    print("\nסיכום תוצאות ספר חנוך:")
    summary = df.groupby('scroll_id')['predicted_dialect'].value_counts(normalize=True)
    print(summary)

if __name__ == "__main__":
    predict_enoch()