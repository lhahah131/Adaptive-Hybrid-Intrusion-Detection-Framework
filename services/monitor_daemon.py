import joblib 
import pandas as pd

model = joblib.load("../models/honeyport_model.pkl")

threshold = 0.25

def detect(log):
    df = pd.DataFrame([log])
    prob = model.predict_proba(df)[0][1]
    prediction = 1 if prob > threshold else 0

    if prediction == 1:
        print(f"🚨 ALERT! Attack detected (prob={prob:.2f})")
    else:
        print(f"✅ Normal traffic (prob={prob:.2f})")

#log masuk
new_log = {
    "total_events"  : 10,
    "login_failed"  : 6,
    "login_success" : 0,
    "total_commands": 2
}

detect(new_log)