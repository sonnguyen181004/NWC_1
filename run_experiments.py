import os
import time
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

import xgboost as xgb
import lightgbm as lgb
import shap

# Set style for plots
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

# Create directories
os.makedirs("plots", exist_ok=True)
os.makedirs("models", exist_ok=True)
dataset_dir = r"c:\Users\LOQ\Downloads\PROJ-NWC\dataset"

print("Loading datasets...")
df_clean_raw = pd.read_csv(os.path.join(dataset_dir, "clean_dataset.csv"))
df_knn_raw = pd.read_csv(os.path.join(dataset_dir, "dataset_knn_imputer.csv"))
df_mice_raw = pd.read_csv(os.path.join(dataset_dir, "dataset_iterative_imputer.csv"))
df_pad_raw = pd.read_csv(os.path.join(dataset_dir, "dataset_padding.csv"))

# Drop NaNs from clean_dataset to train directly on the clean dataset as requested
df_clean = df_clean_raw.dropna()
# For imputed datasets, we keep their full rows but make sure we align the test set
# Wait, for a fair comparison of imputation methods, we will evaluate all of them on the same test split
# Let's align df_knn, df_mice, df_pad to the same rows as df_clean or keep them as is.
# To keep it simple and correct, we will train all models on the clean dropped dataset, and for imputation comparison,
# we will compare training on the respective datasets.

# Target column
target_col = 'is_rogue'

# CRITICAL: Drop temporal leak columns to prevent 1.0 accuracy (leakage of capture session timing)
time_leak_cols = ['Timestamp_ms', 'BeaconTimestamp', 'LowTSF', 'Timestamp_Ratio', 'time_delta']
feature_cols = [c for c in df_clean.columns if c != target_col and c not in time_leak_cols]

print(f"Features used for training: {feature_cols}")
print(f"Clean dataset shape after dropping NaNs and temporal leaks: {df_clean[feature_cols].shape}")

# Define models to train
results = []

def evaluate_model(model_name, X_train, X_test, y_train, y_test, scale_features=False):
    print(f"Training {model_name}...")
    start_time = time.time()
    
    # Scale features if requested (important for KNN and SVM)
    if scale_features:
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
    else:
        X_train_scaled = X_train
        X_test_scaled = X_test
        
    # Check model type
    if "XGBoost" in model_name:
        model = xgb.XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1)
    elif "LightGBM" in model_name:
        model = lgb.LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1)
    elif "Random Forest" in model_name:
        model = RandomForestClassifier(random_state=42, n_jobs=-1, n_estimators=100)
    elif "SVM" in model_name:
        model = LinearSVC(dual=False, random_state=42, max_iter=10000)
    elif "KNN" in model_name:
        model = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
        
    model.fit(X_train_scaled, y_train)
    train_time = time.time() - start_time
    
    start_time = time.time()
    y_pred = model.predict(X_test_scaled)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
    elif hasattr(model, "decision_function"):
        y_prob = model.decision_function(X_test_scaled)
        # Normalize decision function to [0,1] for ROC AUC calculations
        if y_prob.max() != y_prob.min():
            y_prob = (y_prob - y_prob.min()) / (y_prob.max() - y_prob.min())
        else:
            y_prob = np.zeros_like(y_prob)
    else:
        y_prob = y_pred
        
    test_time = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    print(f"{model_name} - Acc: {acc:.4f}, F1: {f1:.4f}, Recall: {rec:.4f}, Time: {train_time:.2f}s")
    
    # ── Save model as .pkl ──────────────────────────────────────────
    safe_name = model_name.replace(" ", "_").replace("/", "_")
    model_path = os.path.join("models", f"{safe_name}_model.pkl")
    joblib.dump(model, model_path)
    print(f"  [Saved] {model_path}")
    if scale_features:
        scaler_path = os.path.join("models", f"{safe_name}_scaler.pkl")
        joblib.dump(scaler, scaler_path)
        print(f"  [Saved] {scaler_path}")
    # ────────────────────────────────────────────────────────────────

    return {
        'Model': model_name,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-Score': f1,
        'AUC-ROC': auc,
        'Train Time (s)': train_time,
        'Inference Time (s)': test_time,
        'model_object': model,
        'scaler_object': scaler if scale_features else None
    }

# ----------------- EXPERIMENT 1: Objective 1.2 (Algorithm Comparison) -----------------
print("\n=== RUNNING EXPERIMENT 1: Model Comparison (Objective 1.2) ===")

X_clean = df_clean[feature_cols]
y_clean = df_clean[target_col]
X_train, X_test, y_train, y_test = train_test_split(
    X_clean, y_clean, test_size=0.2, random_state=42, stratify=y_clean
)

res_knn = evaluate_model("KNN", X_train, X_test, y_train, y_test, scale_features=True)
res_svm = evaluate_model("SVM", X_train, X_test, y_train, y_test, scale_features=True)
res_rf = evaluate_model("Random Forest", X_train, X_test, y_train, y_test, scale_features=False)
res_xgb = evaluate_model("XGBoost", X_train, X_test, y_train, y_test, scale_features=False)
res_lgb = evaluate_model("LightGBM", X_train, X_test, y_train, y_test, scale_features=False)

all_results = [res_knn, res_svm, res_rf, res_xgb, res_lgb]

# Create DataFrame for results
df_results = pd.DataFrame([{k: v for k, v in r.items() if k not in ['model_object', 'scaler_object']} for r in all_results])
df_results.to_csv("plots/model_comparison_results.csv", index=False)
print("\nComparison results on Clean Dataset (No Leaks):")
print(df_results.to_markdown(index=False))

# Save feature column names so we can reload models correctly later
with open("models/feature_cols.json", "w") as f:
    json.dump(feature_cols, f, indent=2)
print(f"[Saved] models/feature_cols.json  ({len(feature_cols)} features)")

# Plot Comparison Chart
plt.figure(figsize=(12, 7))
df_melted = pd.melt(df_results, id_vars=['Model'], value_vars=['Accuracy', 'Recall', 'F1-Score'])
sns.barplot(x='Model', y='value', hue='variable', data=df_melted, palette='viridis')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Score')
plt.title('Comparison of Supervised Machine Learning Algorithms (Objective 1.2 - No Leaks)')
plt.ylim(0.5, 1.02)
plt.tight_layout()
plt.savefig("plots/model_comparison.png", dpi=300)
plt.close()

# ----------------- EXPERIMENT 2: Objective 1.1 (Feature Importance) -----------------
print("\n=== RUNNING EXPERIMENT 2: Feature Importance (Objective 1.1) ===")
best_model_data = res_xgb
best_model = best_model_data['model_object']
importances = best_model.feature_importances_
indices = np.argsort(importances)[::-1]

# Plot top 15 features
plt.figure(figsize=(10, 6))
top_k = min(15, len(feature_cols))
sns.barplot(
    x=importances[indices[:top_k]], 
    y=[feature_cols[i] for i in indices[:top_k]], 
    palette='magma'
)
plt.xlabel('Importance Score')
plt.title('Top Features for Rogue AP Detection (XGBoost - Leak-free)')
plt.tight_layout()
plt.savefig("plots/feature_importance.png", dpi=300)
plt.close()

# SHAP explanations on best model
print("Calculating SHAP values...")
X_shap_sample = X_test.sample(min(1000, len(X_test)), random_state=42)
explainer = shap.TreeExplainer(best_model)
shap_values = explainer(X_shap_sample)

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_shap_sample, show=False)
plt.title('SHAP Summary Plot for Leak-free XGBoost Model', fontsize=14)
plt.tight_layout()
plt.savefig("plots/shap_summary.png", dpi=300)
plt.close()

# ----------------- EXPERIMENT 3: RQ2 (Imputation comparison & Noise Robustness) -----------------
print("\n=== RUNNING EXPERIMENT 3: Robustness Analysis (RQ2) ===")

# For imputation comparison, we drop NaNs in respective files to keep the split same
# Or evaluate on the aligned index of df_clean to see how they predict on the same test set
df_knn_dropped = df_knn_raw.loc[df_clean.index]
df_mice_dropped = df_mice_raw.loc[df_clean.index]
df_pad_dropped = df_pad_raw.loc[df_clean.index]

X_train_knn_imp, X_test_knn_imp, y_train_knn_imp, y_test_knn_imp = train_test_split(
    df_knn_dropped[feature_cols], df_knn_dropped[target_col], test_size=0.2, random_state=42, stratify=df_knn_dropped[target_col]
)
X_train_mice, X_test_mice, y_train_mice, y_test_mice = train_test_split(
    df_mice_dropped[feature_cols], df_mice_dropped[target_col], test_size=0.2, random_state=42, stratify=df_mice_dropped[target_col]
)
X_train_pad, X_test_pad, y_train_pad, y_test_pad = train_test_split(
    df_pad_dropped[feature_cols], df_pad_dropped[target_col], test_size=0.2, random_state=42, stratify=df_pad_dropped[target_col]
)

res_xgb_knn_imp = evaluate_model("XGBoost (on KNN Imputed)", X_train_knn_imp, X_test_knn_imp, y_train_knn_imp, y_test_knn_imp, scale_features=False)
res_xgb_mice = evaluate_model("XGBoost (on MICE/Iterative)", X_train_mice, X_test_mice, y_train_mice, y_test_mice, scale_features=False)
res_xgb_pad = evaluate_model("XGBoost (on Padding)", X_train_pad, X_test_pad, y_train_pad, y_test_pad, scale_features=False)

imputation_comparison = pd.DataFrame([
    {'Imputation Method': 'No Imputation (Clean)', 'F1-Score': res_xgb['F1-Score'], 'Accuracy': res_xgb['Accuracy']},
    {'Imputation Method': 'Constant Padding (-100)', 'F1-Score': res_xgb_pad['F1-Score'], 'Accuracy': res_xgb_pad['Accuracy']},
    {'Imputation Method': 'KNN Imputer', 'F1-Score': res_xgb_knn_imp['F1-Score'], 'Accuracy': res_xgb_knn_imp['Accuracy']},
    {'Imputation Method': 'Iterative Imputer (MICE)', 'F1-Score': res_xgb_mice['F1-Score'], 'Accuracy': res_xgb_mice['Accuracy']}
])

plt.figure(figsize=(10, 6))
df_melted_imp = pd.melt(imputation_comparison, id_vars=['Imputation Method'], value_vars=['Accuracy', 'F1-Score'])
sns.barplot(x='Imputation Method', y='value', hue='variable', data=df_melted_imp, palette='coolwarm')
plt.ylabel('Score')
plt.title('Comparison of Imputation Methods for Missing Values (RQ2 - No Leaks)')
plt.ylim(0.5, 1.01)
plt.tight_layout()
plt.savefig("plots/imputation_comparison.png", dpi=300)
plt.close()

# 3.2: RSSI Noise Injection Test on XGBoost
print("Running RSSI Noise Injection Test...")
noise_levels = np.arange(0, 16, 2)  # 0 to 14 dBm noise
noise_f1_scores = []
noise_recalls = []
noise_accuracies = []

for noise in noise_levels:
    X_test_noisy = X_test.copy()
    if noise > 0:
        # Add gaussian noise to RSSI column
        noise_vector = np.random.normal(0, noise, size=len(X_test_noisy))
        X_test_noisy['RSSI'] = X_test_noisy['RSSI'] + noise_vector
        
    y_pred_noisy = best_model.predict(X_test_noisy)
    f1_noisy = f1_score(y_test, y_pred_noisy)
    recall_noisy = recall_score(y_test, y_pred_noisy)
    acc_noisy = accuracy_score(y_test, y_pred_noisy)
    
    noise_f1_scores.append(f1_noisy)
    noise_recalls.append(recall_noisy)
    noise_accuracies.append(acc_noisy)
    print(f"Noise level: {noise} dBm -> Acc: {acc_noisy:.4f}, F1-Score: {f1_noisy:.4f}, Recall: {recall_noisy:.4f}")

# Plot noise robustness curve
plt.figure(figsize=(10, 6))
plt.plot(noise_levels, noise_accuracies, marker='o', linewidth=2, color='green', label='Accuracy')
plt.plot(noise_levels, noise_f1_scores, marker='x', linewidth=2, color='blue', label='F1-Score')
plt.plot(noise_levels, noise_recalls, marker='s', linewidth=2, color='red', linestyle='--', label='Recall')
plt.xlabel('RSSI Noise Level (Standard Deviation $\sigma$ in dBm)')
plt.ylabel('Score')
plt.title('Model Performance Decay Under RSSI Noise Injection (RQ2 - No Leaks)')
plt.xticks(noise_levels)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("plots/rssi_noise_robustness.png", dpi=300)
plt.close()

print("\nAll experiments completed! Plots saved in 'plots/' directory.")
