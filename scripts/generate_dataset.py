import pandas as pd
import random

data = []

# Normal user
for _ in range(80):
    data.append({
        "total_events": random.randint(1,10),
        "login_failed": random.randint(0,4),
        "login_success": random.choice([0,1]),
        "total_commands": random.randint(1,6),
        "label": 0
    })

# Suspicious / attack simulation
for _ in range(40):
    data.append({
        "total_events": random.randint(5,15),
        "login_failed": random.randint(2,8),
        "login_success": random.choice([0,1]),
        "total_commands": random.randint(0,8),
        "label": 1
    })

df = pd.DataFrame(data)
df.to_csv("../data/processed/features.csv", index=False)
print("Dataset baru dibuat!")