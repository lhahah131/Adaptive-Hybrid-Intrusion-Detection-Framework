import paramiko
import random
import time
import socket
import json
import uuid
import os
from datetime import datetime, timezone

TARGET_HOST = "localhost"
TARGET_PORT = 2222
COWRIE_LOG_PATH = "/home/adi/cowrie/var/log/cowrie/cowrie.json"

USERNAMES = ["root", "admin", "test", "user"]
PASSWORDS = ["123456", "password", "admin", "root", "letmein"]

# Check if port is open
def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

USE_SSH = is_port_open(TARGET_HOST, TARGET_PORT)

if not USE_SSH:
    print(f"⚠️  Port {TARGET_PORT} is closed. Switching to LOG INJECTION mode.")
    print(f"    Writing directly to {COWRIE_LOG_PATH}")

def generate_session_id():
    return uuid.uuid4().hex[:12]

def log_event(event_type, session_id, **kwargs):
    if not os.path.exists(COWRIE_LOG_PATH):
        return
        
    entry = {
        "eventid": event_type,
        "session": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "src_ip": "127.0.0.1",
        "sensor": "simulator",
        "message": "simulated event"
    }
    entry.update(kwargs)
    
    with open(COWRIE_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def attempt(username, password, delay=1, commands=None, session_id=None):
    if USE_SSH:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(TARGET_HOST, port=TARGET_PORT,
                        username=username,
                        password=password,
                        timeout=3)

            if commands:
                for cmd in commands:
                    ssh.exec_command(cmd)
                    time.sleep(delay)

            ssh.close()
        except:
            pass
    else:
        # LOG INJECTION MODE
        if not session_id:
            session_id = generate_session_id()
            
        # 1. New connection / Session setup (implicit in logs usually, but let's emulate login)
        log_event("cowrie.session.connect", session_id, protocol="ssh")
        time.sleep(0.1)
        
        # 2. Login attempt
        if password in ["admin", "123456"] and username in ["root", "admin"]: 
            # Simulate success for specific creds (just for variety)
            log_event("cowrie.login.success", session_id, username=username, password=password)
            
            # 3. Commands if successful
            if commands:
                for cmd in commands:
                    log_event("cowrie.command.input", session_id, input=cmd)
                    time.sleep(delay)
        else:
            # Simulate failure
            log_event("cowrie.login.failed", session_id, username=username, password=password)
            
        # 4. Close
        time.sleep(0.1)
        log_event("cowrie.session.closed", session_id, duration=0.5)

def fast_bot():
    print("--- Running Fast Bot (Brute Force) ---")
    session_id = generate_session_id() # Re-use session for brute force to simulate single attacker? 
   
    
    for _ in range(20):
        # Brute force attacks often close connection after fail.
        attempt(random.choice(USERNAMES),
                random.choice(PASSWORDS),
                delay=0.1) 
        time.sleep(0.1)

def normal_brute():
    print("--- Running Normal Brute Force ---")
    for _ in range(15):
        attempt("root",
                random.choice(PASSWORDS),
                delay=0.5)
        time.sleep(0.5)

def manual_attacker():
    print("--- Running Manual Attacker Simulation ---")
    commands = ["ls", "pwd", "whoami", "cat /etc/passwd"]
    # Manual attacker needs a successful login to run commands.
    # We force success in simulation for "admin"/"admin"
    attempt("admin", "admin", delay=1, commands=commands)

if __name__ == "__main__":
    print("Simulasi berjalan...")
    fast_bot()
    normal_brute()
    manual_attacker()
    print("Simulasi selesai.")