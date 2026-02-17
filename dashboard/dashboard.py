import streamlit as st
import joblib 
import pandas as pd

model = joblib.load("../models/honeyport_model.pkl")

st.title("AI Intrusion Detection System")

total_events = st.slider("Total Events", 1, 20, 5)
login_failed = st.slider("Login Failed", 0, 10, 1)
login_success = st.selectbox("Login Success", [0, 1])
total_commands = st.slider("Total Commands", 0, 10, 2)

if st.button("Predict"):
    data = {
        "total_events"  : total_events,
        "login_failed"  : login_failed,
        "login_success" : login_success,
        "total_commands": total_commands
    }
    
    df = pd.DataFrame([data])
    
    # Feature Engineering (Must match training features)
    df["failed_ratio"] = df["login_failed"] / (df["total_events"] + 1)
    df["command_ratio"] = df["total_commands"] / (df["total_events"] + 1)
    df["success_ratio"] = df["login_success"] / (df["total_events"] + 1)

    prob = model.predict_proba(df)[0][1]

    if prob > 0.25:
        st.error(f" Attack Detected (prob={prob:.2f})")
    else:
        st.success(f" Normal Activity (prob={prob:.2f})")