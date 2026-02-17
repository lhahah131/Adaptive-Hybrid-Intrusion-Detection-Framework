import sys
import os
import time
import uuid

# Add services directory to path to import simulator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulator import log_event, USERNAMES, PASSWORDS

def attempt_login(session_id):
    # Log Injection for failure
    log_event("cowrie.login.failed", session_id, username="hacker", password="wrongpassword")

print("=== CONTROLLED ESCALATION TEST STARTED ===")
print("Mode: LOG INJECTION (Port 2222 closed)")

# Escalation levels
levels = [1, 2, 3, 4, 5, 6, 8, 10]

for level in levels:
    print(f"\n--- Escalation Level: {level} failed logins ---")
    
    # New session per level
    session_id = uuid.uuid4().hex[:12]
    timestamp = time.time()
    
    # Connect
    log_event("cowrie.session.connect", session_id, protocol="ssh")
    time.sleep(0.1)

    for i in range(level):
        attempt_login(session_id)
        # Fast burst: < 0.2s delay to trigger burst_flag
        time.sleep(0.1)  

    # Close
    duration = time.time() - timestamp
    log_event("cowrie.session.closed", session_id, duration=round(duration, 2))

    print(f"Session {session_id} completed. Duration: {duration:.2f}s")
    print("Waiting 2 seconds for model evaluation...")
    time.sleep(2)

print("\n=== TEST COMPLETED ===")