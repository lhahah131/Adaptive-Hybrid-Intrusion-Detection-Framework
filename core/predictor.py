import joblib
import pandas as pd

model = joblib.load("../models/honeyport_model.pkl")


#contoh untuk sebauh data baru
data = {
    "total_events": [5],
    "login_failed": [3],
    "login_success": [0],
    "total_commands": [2],
}

df = pd.DataFrame(data)

# Prediksi
prediction = model.predict(df)

if prediction[0] == 1:
    print("⚠️ ATTACK DETECTED")
else:
    print("✅ Normal Activity")