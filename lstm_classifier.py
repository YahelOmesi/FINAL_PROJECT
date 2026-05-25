import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os

# 1. Loading and initial processing of the data
def load_and_preprocess(file_path):
    """
    Loads the research data from CSV, encodes target categories, 
    and standardizes linguistic features for the neural network.
    """

    print("Loads data and performs normalization")
    df = pd.read_csv(file_path)

    le = LabelEncoder() # creatig encoder
    df['target_encoded'] = le.fit_transform(df['target']) # Bavli - 0 , Yerushalmi - 1
    
    # selecting linguistic features derived from our research hypotheses
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio', 
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio', 
        'plural_ratio', 'line_length', 'avg_word_len', 
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]
    
    X = df[feature_cols].values # feature matrix
    y = df['target_encoded'].values # label vector

    # scaling: normalizes features to a mean of 0 & std of 1
    # this prevents features with larger magnitudes from dominating the model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # returning: normalized features & label vector & encoder
    return X_scaled, y, le


# 2. Creating sequences - The "sliding window"
def create_sequences(X, y, seq_length=10):
    """
    Converts flat data into sequences to give the LSTM temporal context.
    Each sample will consist of 'seq_length' rows of features.
    """

    X_sequences, y_labels = [], []
    
    # loop throgh the data. stopping before the end to avoid index overflow
    for i in range(len(X) - seq_length):

        window = X[i : i + seq_length] # sliding window of "seq_length" consecutive rows
        label = y[i + seq_length] # label of the row following the window
        
        # store the sequence and its corresponding target label
        X_sequences.append(window)
        y_labels.append(label)
        
    # convert lists to numpy arrays
    return np.array(X_sequences), np.array(y_labels)

# 3. Building the LSTM Model Architecture
def build_model(input_shape):
    """
    Creates the network layout with an LSTM layer for sequence memory,
    Dropout for overfitting prevention, and a Dense layer for binary choice.
    """
    model = Sequential()
    
    # Adding the core LSTM layer to process the 10-row text windows
    model.add(LSTM(units=64, input_shape=input_shape, return_sequences=False))
    
    # Regularization layer to prevent the model from memorizing the data
    model.add(Dropout(rate=0.2))
    
    # Final layer with a sigmoid function to output a probability between 0 and 1
    model.add(Dense(units=1, activation='sigmoid'))
    
    # Compiling the model with the tools needed to track performance and learn
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

# 4. Execution, Training & Evaluation
if __name__ == "__main__":
    from sklearn.metrics import classification_report
    
    file_path = os.path.join('Data', 'ready_for_classifier.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Please run the preprocessing script first.")
    else:

        # step 1: Load & scale the flat data
        X_scaled, y, le = load_and_preprocess(file_path)
        
        # step 2: Divide data chronologically but balanced per class (80% Train, 20% Test)
        # Separate the data by target to ensure both classes exist in Train and Test sets
        bavli_idx = (y == 0)
        yerushalmi_idx = (y == 1)
        
        X_bavli, y_bavli = X_scaled[bavli_idx], y[bavli_idx]
        X_yer, y_yer = X_scaled[yerushalmi_idx], y[yerushalmi_idx]
        
        # Calculate split index for each class independently
        split_b = int(len(X_bavli) * 0.8)
        split_y = int(len(X_yer) * 0.8)
        
        # Chronological slice for Bavli
        X_train_b, X_test_b = X_bavli[:split_b], X_bavli[split_b:]
        y_train_b, y_test_b = y_bavli[:split_b], y_bavli[split_b:]
        
        # Chronological slice for Yerushalmi
        X_train_y, X_test_y = X_yer[:split_y], X_yer[split_y:]
        y_train_y, y_test_y = y_yer[:split_y], y_yer[split_y:]
        
        # Combine them back to create the final datasets
        X_train_flat = np.concatenate([X_train_b, X_train_y], axis=0)
        X_test_flat = np.concatenate([X_test_b, X_test_y], axis=0)
        y_train_flat = np.concatenate([y_train_b, y_train_y], axis=0)
        y_test_flat = np.concatenate([y_test_b, y_test_y], axis=0)
        
        # step 3: Transform flat data slices into 10-row time windows
        X_train, y_train = create_sequences(X_train_flat, y_train_flat, seq_length=10)
        X_test, y_test = create_sequences(X_test_flat, y_test_flat, seq_length=10)
        
        # step 4: Extract the input dimensions (window_size, num_of_features)
        input_shape = (X_train.shape[1], X_train.shape[2])
        
        # step 5: Initialize the network architecture
        model = build_model(input_shape)
        
        # step 6: Train the network
        print("\nTraining the LSTM model...")
        model.fit(
            X_train, y_train, 
            validation_data=(X_test, y_test), 
            epochs=15, 
            batch_size=32
            
        )
        
        # step 7: Evaluate model 
        print("\nEvaluating model on unseen test data...")
        predictions = model.predict(X_test)
        
        # convert sigmoid probabilities (0.0 - 1.0) into discrete choices (0 or 1)
        y_pred = (predictions > 0.5).astype(int)
        
        # print Accuracy, Precision, Recall
        print("\nComprehensive Classification Report:")
        print(classification_report(y_test, y_pred, target_names=le.classes_))