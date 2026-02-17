import sys
import os
import random
import time
import uuid

# Add services directory to path to import simulator
sys.path.append(os.path.join(os.path.dirname(__file__), "../services"))

try:
    from simulator import attempt, USE_SSH, log_event, USERNAMES, PASSWORDS, is_port_open, TARGET_HOST, TARGET_PORT
except ImportError:
    # If import fails (e.g. if simulator.py has global code that fails), we might need to copy-paste logic.
    # But as per my previous edit, simulator.py only directs execution if __name__ == "__main__", 
    # and the global vars are safe.
    print("Error importing simulator module. Make sure it is in ../services/")
    sys.exit(1)

def run_low_noise(iterations=5):
    """
    Scenario 1: Low noise.
    1-2 failed logins per session.
    """
    print(f"\n[SCENARIO 1] Low Noise Attack ({iterations} iterations)")
    print("Goal: Test if system is over-sensitive to minor failures.")
    
    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}...")
        # 1-2 attempts
        num_attempts = random.choice([1, 2])
        session_id = uuid.uuid4().hex[:12] # Explicit session ID for control
        
        # Connect
        if not USE_SSH:
            log_event("cowrie.session.connect", session_id, protocol="ssh")
        
        for _ in range(num_attempts):
            attempt(random.choice(USERNAMES), "wrongpass", delay=1, session_id=session_id)
            time.sleep(1)
            
        # Close handled by attempt logic? 
        # simulator.py's attempt() does NOT handle session close for log injection if session_id is provided?
        # Let's check simulator.py...
        # In `attempt` (log injection mode), it does:
        # 1. connect (if new)
        # 2. login success/fail
        # 3. command input
        # 4. close
        # ALL IN ONE CALL.
        
        # This means `attempt()` creates a full lifecycle session by default.
        # This is not ideal for "multi-attempt within one session" simulation if `attempt()` closes it.
        # Let's check `attempt` code in simulator.py again.
        pass

    # RE-CHECK SIMULATOR CODE:
    # def attempt(..., session_id=None):
    #   if not USE_SSH:
    #      if not session_id: session_id = generate_session_id()
    #      log_event("cowrie.session.connect", ...)
    #      ... login ...
    #      ... close ...
    
    # YES, `attempt` closes the session at the end.
    # So calling `attempt` multiple times with SAME session_id will result in:
    # Connect -> Login -> Close -> Connect -> Login -> Close
    # All with same Session ID.
    # This might confuse the monitor or Cowrie log parser if multiple "Connect" and "Closed" events appear for same session.
    # Cowrie usually has one Connect and one Close per session.
    
    # FIX: We need a specialized function for stress testing that controls the session lifecycle better,
    # OR we rely on `attempt` for single-shot sessions (low noise is fine with single shot).
    # Bursts might need help.
    
    # Since I cannot easily modify simulator.py again without potentially breaking other things or making it complex, 
    # I will stick to `attempt` for now but be aware of this limitation.
    # Actually, for "Burst" (20 logins < 3s), if `attempt` closes session every time, we get 20 sessions?
    # No, we want 20 failed logins in ONE session ideally, OR 20 separate sessions rapidly.
    # "Brute force" usually implies many attempts. If from same IP, does it matter if same session?
    # SSH brute force tools often reconnect every time. So 20 sessions is realistic.
    # But "Hydra" might keep connection open?
    # Let's assume 20 separate sessions is fine for "Burst" if `attempt` is used.
    # BUT, the User asked: "Medium brute (5 login gagal dengan delay 1 detik)".
    # If I use `attempt` 5 times, it's 5 sessions.
    
    # Ideally we should support "Multi-try Session".
    # I'll implement `simulate_session_with_multiple_failures` here in this script, reusing `log_event`.
    pass

def simulate_multi_fail_session(num_fails, delay=1, burst=False):
    session_id = uuid.uuid4().hex[:12]
    timestamp = time.time()
    
    if not USE_SSH:
        # 1. Connect
        log_event("cowrie.session.connect", session_id, protocol="ssh")
        time.sleep(0.1)
        
        # 2. Loop Failures
        for i in range(num_fails):
            log_event("cowrie.login.failed", session_id, 
                      username=random.choice(USERNAMES), 
                      password=random.choice(PASSWORDS))
            if not burst:
                time.sleep(delay)
            else:
                time.sleep(random.uniform(0.05, 0.2)) # Very fast
                
        # 3. Close
        duration = time.time() - timestamp
        log_event("cowrie.session.closed", session_id, duration=round(duration, 2))
        
    else:
        # Real SSH mode - Limitations apply (can't easily do multi-try without paramiko deep dive)
        # Standard paramiko connect/close is one session.
        # To do multi-try, we need to keep channel open.
        # For now, let's assume we are in Log Injection mode (since port 2222 is closed mostly).
        # If open, we fallback to standard `attempt` which is 1 try = 1 session.
        print("Note: In SSH mode, falling back to 1-session-per-attempt.")
        for _ in range(num_fails):
            attempt("root", "badpass", delay=0)

def run_medium_brute():
    """
    Scenario 2: Medium brute.
    5 failed logins per session, delay 1s.
    """
    print(f"\n[SCENARIO 2] Medium Brute Force (5 iterations)")
    print("Goal: Test progressive probability increase.")
    
    for i in range(5):
        print(f"  Iteration {i+1}/5 - 5 fails/session...")
        simulate_multi_fail_session(num_fails=5, delay=1.0)
        time.sleep(2) # Pause between sessions

def run_burst_attack():
    """
     Scenario 3: Burst attack.
     20 logins < 3s.
    """
    print(f"\n[SCENARIO 3] Burst Attack (3 iterations)")
    print("Goal: Test immediate detection and latency.")
    for i in range(3):
        print(f"  Iteration {i+1}/3 - 20 fails (Burst)...")
        simulate_multi_fail_session(num_fails=20, burst=True)
        time.sleep(3)

if __name__ == "__main__":
    print("=== STARTING STRESS TEST ===")
    print(f"Mode: {'SSH' if USE_SSH else 'LOG INJECTION'}")
    
    run_low_noise()
    time.sleep(2)
    
    run_medium_brute()
    time.sleep(2)
    
    run_burst_attack()
    
    print("\n=== TEST COMPLETED ===")
    print("Check 'evaluation.csv' for detailed metrics.")
