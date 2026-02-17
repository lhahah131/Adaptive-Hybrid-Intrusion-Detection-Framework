import json
import joblib
import time
import os
import sys
import pandas as pd
import logging
from datetime import datetime, timezone

# ======================
# CONFIGURATION
# ======================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "honeyport_model.pkl")
# Use os.path.join or environment variable for cowrie log if possible, but hardcoded fallback is acceptable for specific env
COWRIE_LOG_PATH = os.getenv("COWRIE_LOG_PATH", "/home/adi/cowrie/var/log/cowrie/cowrie.json")
ALERT_LOG_PATH = os.path.join(BASE_DIR, "alerts.log")
REPUTATION_FILE = os.path.join(BASE_DIR, "ip_reputation.json")

# Thresholds & Settings
CLEANUP_INTERVAL = 300  # Cleanup every 5 minutes (in seconds)
SESSION_TIMEOUT = 300   # Remove sessions inactive for > 5 minutes
MIN_EVENTS_TO_EVALUATE = 3
DEBUG = False # Set to True for verbose logging

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ======================
# GLOBAL STATE
# ======================

model = None
sessions = {}
last_cleanup_time = time.time()
ip_reputation = {}

# ======================
# FEATURES & REPUTATION
# ======================

def load_model():
    """Loads the trained machine learning model from disk."""
    global model
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model not found at {MODEL_PATH}")
        sys.exit(1)
    
    logger.info(f"Loading model from {MODEL_PATH}...")
    try:
        model = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.critical(f"Failed to load model: {e}")
        sys.exit(1)

def load_reputation():
    """Loads IP reputation data from JSON file."""
    global ip_reputation
    if os.path.exists(REPUTATION_FILE):
        try:
            with open(REPUTATION_FILE, "r") as f:
                ip_reputation = json.load(f)
            logger.info(f"Loaded {len(ip_reputation)} IPs from reputation database.")
        except Exception as e:
            logger.error(f"Error loading reputation: {e}")

def save_reputation():
    """Saves IP reputation data to JSON file."""
    try:
        with open(REPUTATION_FILE, "w") as f:
            json.dump(ip_reputation, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving reputation: {e}")

def get_ip_score(ip):
    """Retrieves the reputation score for a specific IP."""
    if ip not in ip_reputation:
        return 0
    return ip_reputation[ip]["score"]

def update_ip_reputation(ip, outcome):
    """
    Update IP score based on visual behavior.
    
    Args:
        ip (str): The source IP address.
        outcome (str): The classification outcome (SAFE, HIGH, BLOCKED, etc).
        
    Returns:
        int: The updated score.
    """
    global ip_reputation
    
    if ip == "Unknown":
        return 0

    if ip not in ip_reputation:
        ip_reputation[ip] = {"score": 0, "first_seen": datetime.now().isoformat(), "history": []}
    
    score_change = 0
    if outcome == "SAFE":
        score_change = -1 # Bonus for good behavior
    elif outcome == "EARLY_WARNING":
        score_change = 2
    elif outcome == "SUSPICIOUS":
        score_change = 5
    elif outcome == "HIGH":
        score_change = 10
    elif outcome == "CRITICAL":
        score_change = 20
    elif outcome == "BLOCKED":
        score_change = 50
    
    # Update score
    ip_reputation[ip]["score"] = max(0, ip_reputation[ip]["score"] + score_change) # Min 0
    ip_reputation[ip]["last_seen"] = datetime.now().isoformat()
    
    save_reputation()
    return ip_reputation[ip]["score"]

def extract_features(s, duration):
    """
    Extract features matching the training phase.
    
    Args:
        s (dict): Session data dictionary.
        duration (float): Session duration in seconds.
        
    Returns:
        pd.DataFrame: DataFrame containing a single row of features.
    """
    total_events = s["total_events"]
    total_commands = s["total_commands"]
    login_failed = s["login_failed"]
    login_success = s["login_success"]
    
    # Avoid division by zero
    te_safe = total_events + 1
    tc_safe = total_commands + 1
    dur_safe = duration + 1

    features = {
        "total_events": [float(total_events)],
        "login_failed": [float(login_failed)],
        "login_success": [float(login_success)],
        "total_commands": [float(total_commands)],
        "failed_ratio": [float(login_failed / te_safe)],
        "command_ratio": [float(total_commands / te_safe)],
        "success_ratio": [float(login_success / te_safe)],
        "login_failure_density": [float(login_failed / tc_safe)],
        "session_duration": [float(duration)],
        "event_rate": [float(total_events / dur_safe)],
        "fail_rate_time": [float(login_failed / dur_safe)],
        "command_rate_time": [float(total_commands / dur_safe)],
        "failure_velocity": [float(login_failed / (duration + 0.1))],
        "burst_flag": [1 if (login_failed >= 3 and duration < 5) else 0]
    }
    
    # Define column order strictly as per training
    cols = [
        "total_events", "login_failed", "login_success", "total_commands",
        "failed_ratio", "command_ratio", "success_ratio", "login_failure_density",
        "session_duration", "event_rate", "fail_rate_time", "command_rate_time",
        "failure_velocity", "burst_flag"
    ]
    
    return pd.DataFrame(features, columns=cols)

# ======================
# DECISION LOGIC
# ======================

def check_early_warning(login_failed, duration, failure_velocity, ip_score):
    """
    LAYER 1: Early Warning (Heuristic + Reputation).
    Checks for fast failures, high velocity, or bad IP reputation.
    """
    warnings = []
    
    # 1. Fast Failures
    if login_failed >= 2 and duration < 3:
        warnings.append("Rapid Failures")
    
    # 2. High Velocity
    if failure_velocity > 3:
        warnings.append("High Velocity")
    
    # 3. Bad Reputation (Long Term Memory)
    if ip_score >= 20:
        warnings.append(f"Bad Reputation (Score: {ip_score})")
        
    return len(warnings) > 0, warnings

def compute_risk_level(prob):
    """
    LAYER 2: ML Risk Mapping (Smooth Escalation).
    Maps probability to discrete risk levels.
    """
    if prob < 0.2:
        return "SAFE"
    elif prob < 0.5:
        return "SUSPICIOUS"
    elif prob < 0.75:
        return "HIGH"
    else:
        return "CRITICAL"

def check_block_condition(prob, login_failed, duration, ip_score):
    """
    LAYER 3: Hard Block Logic (Aggressive + Reputation Aware).
    Determines if the session should be blocked immediately.
    """
    
    # 0. REPUTATION BASED BLOCK (Strict Policy)
    # If IP is already a known heavy offender (Score > 100), block essentially everything suspicious
    if ip_score > 100 and prob > 0.5:
         return True, "Reputation Blacklist Block"

    # If IP has bad reputation (Score > 50), lower the bar for blocking
    threshold_prob = 0.6 if ip_score > 50 else 0.8
    threshold_fail = 2 if ip_score > 50 else 3

    # 1. Confidence Attack Block
    if prob > threshold_prob and login_failed >= threshold_fail:
        return True, f"High Confidence Attack (Thresh: {threshold_prob})"
    
    # 2. Brute force volume
    if login_failed >= 10 and duration < 60:
        return True, "Volume Brute Force"
        
    return False, None

def log_alert(alert_data):
    """Logs alert details to the alert log file and console."""
    msg = alert_data.get("message", f"RISK: {alert_data.get('risk')}")
    
    log_entry = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg} | "
        f"Session: {alert_data['session']} | "
        f"Prob: {alert_data['prob']:.4f} | "
        f"IP: {alert_data['src_ip']} | "
        f"Failed: {alert_data['login_failed']} | "
        f"Duration: {alert_data['duration']:.2f}s"
    )

    # Console output
    logger.info(f"🚨 {msg}")
    if DEBUG:
        print(f"Session ID : {alert_data['session']}")
        print(f"Source IP  : {alert_data['src_ip']}")
        print(f"Probability: {alert_data['prob']:.4f}")
        print(f"Timeline   : {alert_data['duration']:.2f}s duration")

    # File output
    try:
        with open(ALERT_LOG_PATH, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        logger.error(f"Error writing to alert log: {e}")

def evaluate_session(session_id):
    """
    Core evaluation loop for a single session.
    Runs through feature extraction, model prediction, and the 3-layer decision engine.
    """
    s = sessions[session_id]
    ip = s.get("src_ip", "Unknown")

    if DEBUG:
        logger.debug(f"Eval Session {session_id}: events={s['total_events']} failed={s['login_failed']} success={s['login_success']}")
    
    # Skip if not enough events
    if s["total_events"] < MIN_EVENTS_TO_EVALUATE:
        return

    # Skip if already blocked
    if s.get("blocked"):
        return

    # Calculate Duration
    try:
        start_ts = datetime.fromisoformat(s["start"].replace("Z", "+00:00")).timestamp()
        end_ts = datetime.fromisoformat(s["end"].replace("Z", "+00:00")).timestamp()
        duration = max(0, end_ts - start_ts)
    except Exception as e:
        duration = 0

    # Prepare features
    try:
        df = extract_features(s, duration)
        prob = model.predict_proba(df)[0][1]
        
        # --- FEATURE EXTRACTION FOR LOGIC ---
        login_failed = s["login_failed"]
        failure_velocity = df["failure_velocity"].iloc[0]
        
        # --- IP REPUTATION CHECK ---
        ip_score = get_ip_score(ip)
        
        # LAYER 1: Early Warning (Now Reputation Aware)
        is_warning, warning_reasons = check_early_warning(login_failed, duration, failure_velocity, ip_score)
        
        # LAYER 2: Risk Scoring
        risk = compute_risk_level(prob)
        
        # LAYER 3: Block Decision (Now Reputation Aware)
        is_blocked, block_reason = check_block_condition(prob, login_failed, duration, ip_score)
        
        # --- STRESS TEST LOGGING ---
        first_event_ts = datetime.fromisoformat(s["start"].replace("Z", "+00:00")).timestamp()
        current_ts = datetime.now(timezone.utc).timestamp()
        latency = current_ts - first_event_ts
        
        eval_log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": session_id,
            "prob": round(prob, 4),
            "login_failed": login_failed,
            "total_events": s["total_events"],
            "duration": round(duration, 4),
            "latency": round(latency, 4),
            "risk": risk,
            "early_warning": is_warning,
            "blocked": is_blocked,
            "block_reason": block_reason if block_reason else "",
            "ip_score": ip_score  # Log Score
        }
        
        # write to CSV
        eval_csv_path = os.path.join(BASE_DIR, "evaluation.csv")
        file_exists = os.path.isfile(eval_csv_path)
        try:
            with open(eval_csv_path, "a") as f:
                if not file_exists:
                    f.write("timestamp,session,prob,login_failed,total_events,duration,latency,risk,early_warning,blocked,block_reason,ip_score\n")
                f.write(f"{eval_log_entry['timestamp']},{eval_log_entry['session']},{eval_log_entry['prob']},{eval_log_entry['login_failed']},{eval_log_entry['total_events']},{eval_log_entry['duration']},{eval_log_entry['latency']},{eval_log_entry['risk']},{eval_log_entry['early_warning']},{eval_log_entry['blocked']},{eval_log_entry['block_reason']},{eval_log_entry['ip_score']}\n")
        except Exception as err:
            logger.error(f"Error writing to evaluation CSV: {err}")
        # ---------------------------

        # FEEDBACK LOOP: Update Reputation based on Outcome
        outcome_for_reputation = "SAFE"
        if is_blocked:
            outcome_for_reputation = "BLOCKED"
        elif risk == "CRITICAL":
            outcome_for_reputation = "CRITICAL"
        elif risk == "HIGH":
            outcome_for_reputation = "HIGH"
        elif is_warning:
             outcome_for_reputation = "EARLY_WARNING"
        elif risk == "SUSPICIOUS":
             outcome_for_reputation = "SUSPICIOUS"
             
        new_score = update_ip_reputation(ip, outcome_for_reputation)

        # 1. BLOCK (Highest Priority)
        if is_blocked:
            log_alert({
                "risk": "BLOCKED",
                "session": session_id,
                "src_ip": ip,
                "prob": prob,
                "login_failed": login_failed,
                "duration": duration,
                "message": f"BLOCK TRIGGERED – {block_reason} [Rep: {ip_score}->{new_score}]"
            })
            s["blocked"] = True 
            s["flagged"] = True
            return

        # 2. CRITICAL / HIGH ALERT 
        if risk in ["CRITICAL", "HIGH"] and not s.get("flagged"):
            log_alert({
                "risk": risk,
                "session": session_id,
                "src_ip": ip,
                "prob": prob,
                "login_failed": login_failed,
                "duration": duration,
                "message": f"High Risk Activity ({risk}) [Rep: {ip_score}->{new_score}]"
            })
            s["flagged"] = True 
            return

        # 3. EARLY WARNING 
        if is_warning and not s.get("warned"):
            logger.warning(f"EARLY WARNING – {', '.join(warning_reasons)} | IP: {ip} | Rep: {ip_score}->{new_score}")
            s["warned"] = True 
            
    except Exception as e:
        logger.error(f"Prediction error for session {session_id}: {e}")

def cleanup_sessions():
    """Removes inactive sessions to prevent memory leaks."""
    global sessions, last_cleanup_time
    
    current_time = time.time()
    if current_time - last_cleanup_time < CLEANUP_INTERVAL:
        return

    logger.info("Running session cleanup...")
    expired_sessions = []
    
    for sid, data in sessions.items():
        # Determine last activity
        last_active = data.get("last_update_ts", 0)
        if current_time - last_active > SESSION_TIMEOUT:
            expired_sessions.append(sid)
    
    for sid in expired_sessions:
        del sessions[sid]
        
    last_cleanup_time = current_time
    logger.info(f"Cleanup finished. Removed {len(expired_sessions)} sessions. Active sessions: {len(sessions)}")

def process_entry(line):
    """Parses a log line and updates session state."""
    global sessions
    
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        logger.debug(f"Skipping malformed JSON line: {line.strip()}")
        return

    session = entry.get("session")
    timestamp = entry.get("timestamp")
    event = entry.get("eventid")
    src_ip = entry.get("src_ip")

    if not session or not timestamp:
        logger.debug(f"Skipping entry due to missing session or timestamp: {entry}")
        return

    # Initialize session if new
    if session not in sessions:
        sessions[session] = {
            "start": timestamp,
            "end": timestamp,
            "src_ip": src_ip if src_ip else "Unknown",
            "total_events": 0,
            "login_failed": 0,
            "login_success": 0,
            "total_commands": 0,
            "flagged": False,
            "last_update_ts": time.time()
        }
    
    # Update session stats
    s = sessions[session]
    s["end"] = timestamp
    s["total_events"] += 1
    s["last_update_ts"] = time.time()
    
    # Update IP if present in current log
    if src_ip:
        s["src_ip"] = src_ip
    elif s["src_ip"] == "Unknown":
        pass # Keep unknown until we see an IP

    if event == "cowrie.login.failed":
        s["login_failed"] += 1
    elif event == "cowrie.login.success":
        s["login_success"] += 1
    elif event == "cowrie.command.input":
        s["total_commands"] += 1

    # Evaluate
    evaluate_session(session)
    
    # Periodic Cleanup
    cleanup_sessions()

def follow(file):
    """Generator that yields new lines from a file."""
    file.seek(0, 2) # Go to the end
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.5)
            continue
        yield line

# ======================
# MAIN LOOP
# ======================

if __name__ == "__main__":
    print("""
    ========================================
       ML-HIDS Realtime Monitor v2.0
       (Hybrid Detection Engine Active)
    ========================================
    """)
    logger.info("Initializing Realtime Monitor...")
    load_model()
    load_reputation()
    
    if not os.path.exists(COWRIE_LOG_PATH):
        logger.warning(f"Waiting for log file: {COWRIE_LOG_PATH}")
        while not os.path.exists(COWRIE_LOG_PATH):
            time.sleep(2)
            
    logger.info(f"Monitoring log: {COWRIE_LOG_PATH}")
    logger.info(f"Alerts will be saved to: {ALERT_LOG_PATH}")
    logger.info("Press Ctrl+C to stop.")

    try:
        with open(COWRIE_LOG_PATH, "r") as f:
            for line in follow(f):
                process_entry(line)
    except KeyboardInterrupt:
        logger.info("Stopping monitor.")
        save_reputation()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")