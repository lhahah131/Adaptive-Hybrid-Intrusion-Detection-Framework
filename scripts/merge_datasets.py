import os
import pandas as pd

#===================
# PATH CONFIGURATION
#===================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAIN_PATH = os.path.join(BASE_DIR, "data", "processed", "features.csv")
TEST_PATH = os.path.join(BASE_DIR, "data", "raw", "external_generated.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "combined_dataset.csv")

#load dataset

print("Loading datasets...")

df_train = pd.read_csv(TRAIN_PATH)
df_external = pd.read_csv(TEST_PATH)

print(f"Training data shape: {df_train.shape}")
print(f"External data shape: {df_external.shape}")

# Drop non-feature columns
drop_cols = ["session", "src_ip", "timestamp"]
for col in drop_cols:
    if col in df_train.columns:
        df_train = df_train.drop(col, axis=1)

#validate colums
if set(df_train.columns) != set(df_external.columns):
    # Print difference for debugging
    print("Train columns:", df_train.columns)
    print("External columns:", df_external.columns)
    print("Diff:", set(df_train.columns) ^ set(df_external.columns))
    raise ValueError("Columns mismatch betweem training and external ")
print("Columns match. Proceeding...")

#MARGE DATASET
df_combined = pd.concat([df_train, df_external], ignore_index=True)
print(f"Combined dataset shape: {df_combined.shape}")

#SAVE OUTPUT
df_combined.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset berhasil digabungkan dan disimpan.")
print(f"\nLabel distribution after marge:")
print(df_combined["label"].value_counts())
print(df_combined.columns)
df = pd.read_csv(OUTPUT_PATH)
print(df.columns)