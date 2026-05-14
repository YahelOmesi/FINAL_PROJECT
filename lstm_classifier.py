import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
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

        window = X[i : i + seq_length] # sliding window of 10 consecutive rows
        label = y[i + seq_length] # label of the row following the window
        
        # store the sequence and its corresponding target label
        X_sequences.append(window)
        y_labels.append(label)
        
    # convert lists to numpy arrays
    return np.array(X_sequences), np.array(y_labels)