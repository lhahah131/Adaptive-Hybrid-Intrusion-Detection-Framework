import json
import pandas as pd
import os
import random

# =========================
# BASIC FEATURE ENGINEERING
# =========================

def extract_basic_features(df):

    df["failed_ratio"] = df["login_failed"] / (df["total_events"] + 1)
    df["command_ratio"] = df["total_commands"] / (df["total_events"] + 1)
    df["success_ratio"] = df["login_success"] / (df["total_events"] + 1)
    df["login_failure_density"] = df["login_failed"] / (df["total_commands"] + 1)

    return df


# =========================
# TEMPORAL FEATURE ENGINEERING
# =========================

def extract_temporal_features(df):

    if "session_duration" in df.columns:

        df["event_rate"] = df["total_events"] / (df["session_duration"] + 1)
        df["fail_rate_time"] = df["login_failed"] / (df["session_duration"] + 1)
        df["command_rate_time"] = df["total_commands"] / (df["session_duration"] + 1)
        

        df["failure_velocity"] = df["login_failed"] / (df["session_duration"] + 0.1) 
        

        df["burst_flag"] = ((df["login_failed"] >= 3) & (df["session_duration"] < 5)).astype(int)

    return df


# =========================
# MAIN WRAPPER
# =========================

def extract_features(df):

    df = extract_basic_features(df)
    df = extract_temporal_features(df)

    return df

if __name__ == "__main__":
    log_file = "/home/adi/cowrie/var/log/cowrie/cowrie.json"
    
    data = []
    
    try:
        with open(log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                session = entry.get("session")
                event = entry.get("eventid")
        
                data.append({
                    "session" : session,
                    "event" : event,
                    "timestamp" : entry.get("timestamp"),
                    "src_ip" : entry.get("src_ip")
                })
        
        df = pd.DataFrame(data)
        
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        features = df.groupby("session").agg(
            src_ip=("src_ip", "first"),
            total_events=("event", "count"),
            login_failed=("event", lambda x: (x == "cowrie.login.failed").sum()),
            login_success=("event", lambda x: (x == "cowrie.login.success").sum()),
            total_commands=("event", lambda x: (x == "cowrie.command.input").sum()),
        ).reset_index()
        
        # Apply feature extraction
        features = extract_features(features)

        #============================================
        #HITUNG SESSION DURATIOIN REAL DARI TIMESTAMP
        #============================================

        session_time = df.groupby("session")["timestamp"].agg(["min", "max"]) 
        session_time["session_duration"] = (
            session_time["max"] - session_time["min"]
        ).dt.total_seconds()

        # Reset index agar session menjadi kolom
        session_time = session_time.reset_index()

        #gabungkan ke dalam features
        features = features.merge(
            session_time[["session", "session_duration"]],
            on="session",
            how="left"
        )

        features["session_duration"] = features["session_duration"].fillna(0)    
        features = extract_temporal_features(features)
        features["label"] = 1
        print(features[["total_commands",
                        "session_duration",
                        "command_rate_time"]].head(20))
       
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "features.csv")
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        features.to_csv(OUTPUT_PATH, index=False)
        print(f"Features saved to {OUTPUT_PATH}")
        
        print(features)
        
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print(features["session_duration"].describe())
    print(features["total_commands"].describe())
   
