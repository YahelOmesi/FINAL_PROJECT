import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import os
import joblib  # Used to save the fitted preprocessing objects.


def load_and_preprocess(file_path):
    """
    Load the extracted linguistic features from a CSV file, encode the dialect
    labels, and standardize the feature values before model training.
    """

    print("Loads data and performs normalization")
    df = pd.read_csv(file_path)

    # Encode the textual dialect labels as numerical classes.
    le = LabelEncoder()
    df['target_encoded'] = le.fit_transform(df['target'])  # Bavli: 0, Yerushalmi: 1

    # Select the linguistic features derived from the research hypotheses.
    feature_cols = [
        'emphatic_ratio', 'absolute_ratio', 'function_words_ratio',
        'lexical_diversity', 'verb_ratio', 'passive_voice_ratio',
        'plural_ratio', 'line_length', 'avg_word_len',
        'v_then_noun_ratio', 'v_then_prep_ratio'
    ]

    # Construct the feature matrix and target-label vector.
    X = df[feature_cols].values
    y = df['target_encoded'].values

    # Standardize each feature to a mean of zero and a standard deviation of one.
    # This prevents features with larger numerical ranges from dominating the model.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Return the normalized features, labels, fitted encoder, and fitted scaler.
    return X_scaled, y, le, scaler


def create_sequences(X, y, seq_length=10):
    """
    Convert the flat feature matrix into fixed-length sliding-window sequences.

    Each input sample contains `seq_length` consecutive feature rows, while its
    target is the label of the row immediately following that sequence.
    """

    X_sequences, y_labels = [], []

    # Iterate through the dataset while leaving enough rows for a complete sequence.
    for i in range(len(X) - seq_length):

        # Create a sliding window containing consecutive feature rows.
        window = X[i : i + seq_length]

        # Assign the label of the row immediately following the current window.
        label = y[i + seq_length]

        # Store the sequence and its corresponding target label.
        X_sequences.append(window)
        y_labels.append(label)

    # Convert the accumulated sequences and labels into NumPy arrays.
    return np.array(X_sequences), np.array(y_labels)


def build_model(input_shape):
    """
    Construct and compile an LSTM-based binary classification model.

    The model uses an LSTM layer to process sequential context, a Dropout layer
    for regularization, and a sigmoid output layer for dialect classification.
    """

    model = Sequential()

    # Process each fixed-length sequence and retain the final LSTM representation.
    model.add(LSTM(units=32, input_shape=input_shape, return_sequences=False))

    # Reduce overfitting by randomly deactivating a portion of the learned units.
    model.add(Dropout(rate=0.3))

    # Produce a probability between zero and one for binary classification.
    model.add(Dense(units=1, activation='sigmoid'))

    # Configure the optimization method, loss function, and evaluation metric.
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":

    file_path = os.path.join('Data', 'ready_for_classifier.csv')

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Please run the preprocessing script first.")
    else:

        # Load and standardize the extracted linguistic features.
        X_scaled, y, le, scaler = load_and_preprocess(file_path)

        # Split each dialect independently to preserve chronological order while
        # ensuring that both classes are represented in the training and test sets.
        bavli_idx = (y == 0)
        yerushalmi_idx = (y == 1)

        X_bavli, y_bavli = X_scaled[bavli_idx], y[bavli_idx]
        X_yer, y_yer = X_scaled[yerushalmi_idx], y[yerushalmi_idx]

        # Calculate the 80% training boundary independently for each dialect.
        split_b = int(len(X_bavli) * 0.8)
        split_y = int(len(X_yer) * 0.8)

        # Create chronological training and test partitions for the Bavli data.
        X_train_b, X_test_b = X_bavli[:split_b], X_bavli[split_b:]
        y_train_b, y_test_b = y_bavli[:split_b], y_bavli[split_b:]

        # Create chronological training and test partitions for the Yerushalmi data.
        X_train_y, X_test_y = X_yer[:split_y], X_yer[split_y:]
        y_train_y, y_test_y = y_yer[:split_y], y_yer[split_y:]

        # Combine both dialect partitions into the final training and test datasets.
        X_train_flat = np.concatenate([X_train_b, X_train_y], axis=0)
        X_test_flat = np.concatenate([X_test_b, X_test_y], axis=0)
        y_train_flat = np.concatenate([y_train_b, y_train_y], axis=0)
        y_test_flat = np.concatenate([y_test_b, y_test_y], axis=0)

        # Transform the flat datasets into fixed-length sequential windows.
        X_train, y_train = create_sequences(X_train_flat, y_train_flat, seq_length=10)
        X_test, y_test = create_sequences(X_test_flat, y_test_flat, seq_length=10)

        # Define the model input dimensions as sequence length and feature count.
        input_shape = (X_train.shape[1], X_train.shape[2])

        # Initialize the LSTM classification model.
        model = build_model(input_shape)

        # Calculate balanced class weights to reduce the effect of class imbalance.
        classes = np.unique(y_train_flat)
        weights = compute_class_weight(
            class_weight='balanced',
            classes=classes,
            y=y_train_flat
        )
        class_weight_dict = dict(zip(classes, weights))

        print(f"Applied balanced class weights: {class_weight_dict}")

        # Train the model using the test partition as validation data.
        print("\nTraining the LSTM model...")
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_test, y_test),
            epochs=15,
            batch_size=32,
            class_weight=class_weight_dict,
            verbose=0
        )

        # Retrieve the performance values recorded during the final training epoch.
        final_epoch = 14

        print("\n=======================================================")
        print("FINAL MODEL PERFORMANCE REPORT")
        print("=======================================================")
        print("train:")
        print(f"  accuracy - {history.history['accuracy'][final_epoch]:.4f}")
        print(f"  loss - {history.history['loss'][final_epoch]:.4f}")
        print("\ntest:")
        print(f"  accuracy - {history.history['val_accuracy'][final_epoch]:.4f}")
        print(f"  loss - {history.history['val_loss'][final_epoch]:.4f}")
        print("=======================================================")

        # Generate class predictions for the test sequences.
        predictions = model.predict(X_test, verbose=0)
        y_pred = (predictions > 0.5).astype(int)

        # Calculate the confusion matrix for the test predictions.
        cm = confusion_matrix(y_test, y_pred)

        # Extract the individual confusion-matrix components.
        # TN and TP are correct Bavli and Yerushalmi predictions, respectively.
        tn, fp, fn, tp = cm.ravel()

        print("\nVISUAL CONFUSION MATRIX (MAPPING TEST PREDICTIONS):")
        print("-------------------------------------------------------")
        print(f"  Actual BAVLI    |  Correctly classified: {tn}  |  Mistakenly called Yerushalmi: {fp}")
        print(f"  Actual YERUSHALMI |  Mistakenly called Bavli:  {fn}  |  Correctly classified: {tp}")
        print("-------------------------------------------------------")

        # Print precision, recall, F1-score, and support for both dialect classes.
        print("\nComprehensive Classification Metrics Report:")
        print(classification_report(y_test, y_pred, target_names=le.classes_))

        # Save the trained model and fitted preprocessing objects for later
        # classification of the Dead Sea Scrolls and other Aramaic texts.
        print("\nSaving model and scaler for future use on Dead Sea Scrolls...")

        model_path = os.path.join('Data', 'lstm_model.h5')
        scaler_path = os.path.join('Data', 'scaler.pkl')
        le_path = os.path.join('Data', 'label_encoder.pkl')

        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        joblib.dump(le, le_path)

        print(f"  - Model saved to: {model_path}")
        print(f"  - Scaler saved to: {scaler_path}")
        print(f"  - Encoder saved to: {le_path}")