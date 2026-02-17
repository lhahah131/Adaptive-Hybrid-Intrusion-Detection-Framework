import sys
import os
import joblib
import pandas as pd
import numpy as np

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.feature_extractor import extract_features
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# CONFIGURATION
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "enhanced_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "honeyport_model.pkl")

# ======================
# LOAD & PREPARE DATA
# ======================
if not os.path.exists(DATA_PATH):
    print(f"Error: Dataset not found at {DATA_PATH}")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape}")
print("Label distribution:\n", df["label"].value_counts())

# Generate derived features
# Note: extract_features expects raw columns which are present in enhanced_dataset.csv
df = extract_features(df)

# Check for NaNs
df = df.fillna(0)

# Feature Selection (Explicitly list features to match simulation)
feature_cols = [
    "total_events", "login_failed", "login_success", "total_commands",
    "failed_ratio", "command_ratio", "success_ratio", "login_failure_density",
    "session_duration", "event_rate", "fail_rate_time", "command_rate_time",
    "failure_velocity", "burst_flag"  # New features
]

# Ensure all columns exist
for col in feature_cols:
    if col not in df.columns:
        print(f"Warning: Missing column {col}, filling with 0")
        df[col] = 0

X = df[feature_cols]
y = df["label"]

print("\nFeature Summary (Mean per Class):")
print(df.groupby("label")[feature_cols].mean().T)

# ======================
# TRAINING
# ======================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Enhanced Grid Search for STABILITY
# We impose constraints to prevent overfitting to small "noisy" patterns
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [5, 8, 10], # Limit depth to avoid memorizing unique samples
    "min_samples_split": [5, 10], # Require more samples to split
    "min_samples_leaf": [2, 4, 8], # Require more samples in leaf -> smoother probability
    "max_features": ["sqrt", "log2"]
}

rf = RandomForestClassifier(random_state=42, class_weight="balanced")

print("\nTraining with Grid Search...")
grid_search = GridSearchCV(rf, param_grid, cv=5, scoring="roc_auc", n_jobs=-1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"\nBest Parameters: {grid_search.best_params_}")
print(f"Best CV AUC: {grid_search.best_score_:.4f}")

# ======================
# EVALUATION
# ======================
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

print("\nClassification Report (Test Set):")
print(classification_report(y_test, y_pred))

auc_score = roc_auc_score(y_test, y_prob)
print(f"Test AUC Score: {auc_score:.4f}")

# Sanity Check on "Grey Area" samples from Test Set
# Let's filter test set for low failures
test_df_eval = X_test.copy()
test_df_eval["label"] = y_test
test_df_eval["prob"] = y_prob

print("\n--- SANITY CHECK: Low Failure Samples in Test Set ---")
# Filter: login_failed <= 2
low_fail_samples = test_df_eval[test_df_eval["login_failed"] <= 2]
if not low_fail_samples.empty:
    print(f"Found {len(low_fail_samples)} samples with <= 2 failures.")
    print("Mean Probability:", low_fail_samples["prob"].mean())
    print("Max Probability:", low_fail_samples["prob"].max())
    print("Sample:\n", low_fail_samples[["login_failed", "session_duration", "label", "prob"]].head(10))
else:
    print("No low failure samples in test set.")

# SAVE MODEL
joblib.dump(best_model, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")
