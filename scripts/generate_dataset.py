import pandas as pd
import random
import numpy as np

def generate_data(n_samples=1000):
    data = []
    
    # 1. Normal User (Standard)
    # Login success, maybe 1 typo, does some work (duration 10s+)
    for _ in range(int(n_samples * 0.4)):
        login_failed = 0 if random.random() > 0.3 else 1
        login_success = 1
        total_commands = random.randint(1, 15)
        # Duration: correlated with commands. 5s per command + overhead
        duration = random.randint(5, 30) + (total_commands * random.randint(2, 10))
        
        # Events: connect + (fail) + success + commands + close
        total_events = 2 + login_failed + login_success + total_commands
        
        data.append({
            "total_events": total_events,
            "login_failed": login_failed,
            "login_success": login_success,
            "total_commands": total_commands,
            "session_duration": duration,
            "label": 0
        })

    # 2. Normal User (Clumsy/Fast/Grey Area)
    # Fails 1-2 times, then maybe gives up or succeeds. Short duration.
    for _ in range(int(n_samples * 0.2)):
        login_failed = random.randint(1, 2)
        login_success = 0 if random.random() > 0.5 else 1
        total_commands = 0
        if login_success:
            total_commands = random.randint(0, 2)
            
        # Fast duration: 2s per attempt
        duration = (login_failed + login_success) * random.uniform(1.0, 3.0) + (total_commands * 2)
        
        total_events = 2 + login_failed + login_success + total_commands
        
        data.append({
            "total_events": total_events,
            "login_failed": login_failed,
            "login_success": login_success,
            "total_commands": total_commands,
            "session_duration": duration,
            "label": 0
        })

    # 3. Attack (Burst Brute Force)
    # Many failures, short duration per session (or per burst if aggregated)
    # Assuming session aggregation: many fails, very fast.
    for _ in range(int(n_samples * 0.25)):
        login_failed = random.randint(3, 15) # Escalation: 3 is low attack, 15 is high
        login_success = 0 # Attackers rarely succeed in honeypot unless we simulate it
        total_commands = 0
        
        # Very fast: < 0.5s per attempt for scripts
        duration = login_failed * random.uniform(0.1, 0.5)
        
        total_events = 2 + login_failed + login_success + total_commands
        
        data.append({
            "total_events": total_events,
            "login_failed": login_failed,
            "login_success": login_success,
            "total_commands": total_commands,
            "session_duration": duration,
            "label": 1
        })
        
    # 4. Attack (Slow/Manual Brute Force)
    # Fails, but slower.
    for _ in range(int(n_samples * 0.15)):
        login_failed = random.randint(3, 10)
        login_success = 0
        total_commands = 0
        
        # Slower: 2-5s per attempt
        duration = login_failed * random.uniform(2.0, 5.0)
        
        total_events = 2 + login_failed + login_success + total_commands
        
        data.append({
            "total_events": total_events,
            "login_failed": login_failed,
            "login_success": login_success,
            "total_commands": total_commands,
            "session_duration": duration,
            "label": 1
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_data(2000)
    
    # Save to processed using absolute path
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, "data", "processed", "dataset.csv")
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Enhanced dataset generated at {output_path}")
    print(df["label"].value_counts())
    print(df.groupby("label")[["login_failed", "session_duration"]].mean())
