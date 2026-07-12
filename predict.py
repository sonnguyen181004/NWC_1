import os
import json
import joblib
import pandas as pd
import numpy as np

def predict_ap(csv_path=None):
    # 1. Paths configuration
    model_dir = "models"
    model_path = os.path.join(model_dir, "XGBoost_model.pkl")
    features_path = os.path.join(model_dir, "feature_cols.json")
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}. Please run run_experiments.py first.")
        return
        
    if not os.path.exists(features_path):
        print(f"Error: Feature columns description not found at {features_path}.")
        return
        
    # 2. Load the best trained model (XGBoost) and the features configuration
    print("=== LOADING TRAINED XGBOOST MODEL ===")
    model = joblib.load(model_path)
    with open(features_path, "r") as f:
        feature_cols = json.load(f)
        
    print(f"Loaded successfully. Model expects {len(feature_cols)} features.")
    
    # 3. Load dataset to predict
    if csv_path is None or not os.path.exists(csv_path):
        dataset_path = r"c:\Users\LOQ\Downloads\PROJ-NWC\dataset\clean_dataset.csv"
        if os.path.exists(dataset_path):
            print(f"No external CSV specified. Loading test samples from {dataset_path}...")
            df = pd.read_csv(dataset_path).dropna()
        else:
            print("Error: No data available for prediction.")
            return
    else:
        print(f"Loading external dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
        
    # 4. Check if required features are present in the target dataset
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        print(f"Error: The input data is missing the following required features: {missing_cols}")
        return
        
    # Extract feature matrix
    X = df[feature_cols]
    
    # 5. Run inference
    print("\n=== RUNNING INFERENCE ===")
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else [None] * len(preds)
    
    df['predicted_label'] = preds
    df['rogue_probability'] = probs
    
    # 6. Display sample predictions (Legitimate vs Rogue side-by-side)
    print("\nSample Prediction Results:")
    sample_size = min(5, len(df))
    if 'is_rogue' in df.columns:
        legit_samples = df[df['is_rogue'] == 0].head(3)
        rogue_samples = df[df['is_rogue'] == 1].head(3)
        samples_to_show = pd.concat([legit_samples, rogue_samples])
    else:
        samples_to_show = df.head(sample_size)
        
    # Choose key diagnostic features to show alongside prediction
    cols_to_print = ['RSSI', 'Channel', 'IsHidden', 'BSSID_LocalAdmin', 'HTStreams']
    if 'is_rogue' in df.columns:
        cols_to_print = ['is_rogue'] + cols_to_print
    cols_to_print = cols_to_print + ['predicted_label', 'rogue_probability']
    
    # Clean up column list
    cols_to_print = [c for c in cols_to_print if c in df.columns]
    
    # Format probabilities as percentage
    display_df = samples_to_show[cols_to_print].copy()
    if 'rogue_probability' in display_df.columns:
        display_df['rogue_probability'] = display_df['rogue_probability'].apply(lambda x: f"{x * 100:.2f}%")
        
    print(display_df.to_markdown(index=False))
    
    # 7. Print overall evaluation summary if ground truth is available
    if 'is_rogue' in df.columns:
        from sklearn.metrics import accuracy_score, classification_report
        acc = accuracy_score(df['is_rogue'], df['predicted_label'])
        print(f"\nOverall Prediction Accuracy on this dataset: {acc * 100:.2f}%")
        print("\nDetailed Classification Report:")
        print(classification_report(df['is_rogue'], df['predicted_label'], target_names=['Legitimate AP (0)', 'Rogue AP (1)']))

if __name__ == "__main__":
    predict_ap()
