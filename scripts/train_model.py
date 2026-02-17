import sys
import os
import joblib
import pandas as pd

# Add project root to Python path to allow importing from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.feature_extractor import extract_features
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.ensemble import IsolationForest

import seaborn as sns
import matplotlib.pyplot as plt


# ======================
# LOAD DATA
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "combined_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "honeyport_model.pkl")

df = pd.read_csv(DATA_PATH)

print("Distribusi Label:")
print(df["label"].value_counts())

# =========================
# FEATURE ENGINEERING
# =========================

df = extract_features(df)
if df.isnull().sum().sum() > 0:
    print("Warning: Missing values detected")

print("\nRata-rata fitur baru per kelas:")
print(df.groupby("label")[[
    "failed_ratio",
    "command_ratio",
    "success_ratio",
    "login_failure_density"
]].mean())

# ======================
# SPLIT FEATURE & TARGET
# ======================

x = df.drop("label", axis=1)
y = df["label"]

# ======================
# TRAIN TEST SPLIT
# ======================

x_train, x_test, y_train, y_test = train_test_split(
    x, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)


# ======================
# BUILD MODEL
# ======================

param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [5, 18, None],
    "min_samples_split": [2, 5]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42,
    class_weight={0:1, 1:3}
    ),

    param_grid,
    cv=5,
    scoring="recall",
)

grid_search.fit(x_train, y_train)

model = grid_search.best_estimator_

print("\nBest parameters", grid_search.best_params_)

# ======================
# EVALUATION
# ======================

y_pred = model.predict(x_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nTrain Accuracy:", model.score(x_train, y_train))
print("Test Accuracy :", model.score(x_test, y_test))


# ======================
# CONFUSION MATRIX
# ======================

cm = confusion_matrix(y_test, y_pred)

print("\nConfusion Matrix:")
print(cm)

sns.heatmap(cm, annot=True, fmt="d")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()


# ======================
# FEATURE IMPORTANCE
# ======================

feature_importance = pd.Series(
    model.feature_importances_,
    index=x.columns
)

print("\nFeature Importance:")
print(feature_importance.sort_values(ascending=False))


# ======================
# CROSS VALIDATION
# ======================

scores = cross_val_score(model, x, y, cv=10)
print("\n10-FoldCross Validation Accuracy:", scores.mean())
print("\nFold Scores:", scores)

#========================
#ROC CURVE
#========================

y_prob = model.predict_proba(x_test)[:, 1]

for t in [0.3, 0.25, 0.2, 0.15, 0.1]: 
    y_temp = (y_prob > t).astype(int)
    cm_temp = confusion_matrix(y_test, y_temp)
    tn, fp, fn, tp = cm_temp.ravel()
    print(f"\nThreshold: {t}")
    print(cm_temp)
    print(f"FN: {fn}, FP: {fp}")

threshold = 0.25
y_pred_custom = (y_prob > threshold).astype(int)

print(f"\nCustom Threshold: {threshold}")
print(classification_report(y_test, y_pred_custom))

cm_custom = confusion_matrix(y_test, y_pred_custom)
print("\nConfusion Matrix (Custom Threshold):")
print(cm_custom)


fpr, tpr, roc_threshold = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

print("\nROC AUC:", roc_auc)
print("\nDetail Probalitas vs Label Asli")
for prob, actual in zip(y_prob, y_test):
    print(f"Probalitas: {prob:.3f} | Actual: {actual}")

plt.figure()
plt.plot(fpr, tpr, label=f"AUC={roc_auc:.2f}")
plt.plot([0, 1], [0, 1], linestyle="--") 
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.show()


# ======================
# PRECISION-RECALL CURVE
# ======================

precision, recall, pr_threshold = precision_recall_curve(y_test, y_prob)
pr_auc = average_precision_score(y_test, y_prob)

print("\nPrecision-Recall AUC:", pr_auc)

plt.figure()
plt.plot(recall, precision, label=f"PR AUC={pr_auc:.2f}")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend()
plt.show()

#=======================
# SECURITY MODE REPORT 
#=======================

tn, fp, fn, tp, = cm_custom.ravel()

recall_attack = tp / (tp + fn)
precision_attack = tp / (tp + fp)
false_alarm_rate = fp / (fp + tn)

print("\n=== SECURITY MODE REPORT ===")
print(f"Threshold            : {threshold}")
print(f"Recall Attack        : {recall_attack:.2%}")
print(f"Attack Precision     : {precision_attack:.2%}")
print(f"False Alarm Rate     : {false_alarm_rate:.2%}")
print(f"F1 Attack Lolos (FN) : {fn}")
print(f"False Alarm (FP)     : {fp}")

#=======================
# Isolation Forest
#=======================

iso = IsolationForest(contamination=0.1, random_state=42)
iso.fit(x_train)

df["anomaly_score"] = iso.decision_function(x)
df["is_anomaly"] = iso.predict(x)


# ======================
# SAVE MODEL
# ======================

os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print(f"\nModel berhasil disimpan ke {MODEL_PATH}")

print("\nRata-rata fitur per kelas:")
print(df.groupby("label").mean())

print("\nProbalitas sample:")
print(y_prob[:10])

if "session_duration" in df.columns:
    print(df.groupby("label")["session_duration"].mean())
else:
    print("Column 'session_duration' not found in dataset.")