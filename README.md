# Adaptive Hybrid Intrusion Detection Framework (AHIDF)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-orange)

An advanced, machine learning-driven Intrusion Detection System (IDS) designed to detect and mitigate SSH brute-force attacks with granular precision. Unlike traditional threshold-based systems (like Fail2Ban), AHIDF uses a **3-Layer Hybrid Detection Engine** that combines heuristic velocity checks, machine learning probability scoring, and persistent IP reputation memory.

## 🚀 Key Features

*   **3-Layer Hybrid Detection Engine**:
    1.  **Layer 1: Early Warning (Heuristic)** - Detects "Fast Fail" anomalies and high-velocity attacks instantly without blocking.
    2.  **Layer 2: ML Risk Scoring (RandomForest)** - Assigns smooth risk probabilities (`SAFE`, `SUSPICIOUS`, `HIGH`, `CRITICAL`) using a trained model.
    3.  **Layer 3: Behavioral & Reputation Blocking** - Blocks attacks based on high confidence (ML > 0.8) or volumetric brute-force patterns.
*   **Behavioral Features**:
    *   **Failure Velocity**: Measures failures per second to distinguish "clumsy users" from scripts.
    *   **Burst Detection**: Identifies rapid-fire login attempts (< 5s duration).
*   **Persistent IP Reputation**: Long-term memory module that tracks offender history. Penalties escalate for repeat offenders, lowering the detection threshold for known bad IPs.
*   **False Positive Reduction**: Specifically tuned to ignore legitimate "fat-finger" errors (1-2 failed logins).

## 📂 Project Structure

```
ml_hids/
├── core/
│   └── feature_extractor.py    # Feature engineering logic (Velocity, Ratios, Time-based)
├── services/
│   ├── realtime_simulation.py  # MAIN ENGINE: Real-time log monitoring & decision logic
│   └── simulator.py            # Attack simulator (Brute force / Low noise injection)
├── scripts/
│   ├── train_model_enhanced.py # ML Training script (RandomForest + GridSearch)
│   └── generate_dataset_v2.py  # Synthetic dataset generator for training
├── models/
│   └── honeyport_model.pkl     # Pre-trained model (Exclude from repo, train locally)
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lhahah131/Adaptive-Hybrid-Intrusion-Detection-Framework.git
    cd Adaptive-Hybrid-Intrusion-Detection-Framework
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Generate Dataset & Train Model**:
    ```bash
    # Generate synthetic training data
    python3 ml_hids/scripts/generate_dataset_v2.py

    # Train the Hybrid Model
    python3 ml_hids/scripts/train_model_enhanced.py
    ```

## ⚡ Usage

### 1. Start the Real-time Monitor
This service tails the Cowrie honeypot logs (or custom SSH logs) and evaluates sessions in real-time.
```bash
python3 ml_hids/services/realtime_simulation.py
```
*Note: Ensure `COWRIE_LOG_PATH` in the script points to your actual log file.*

### 2. Simulate Attacks (Testing)
Run the escalation test to verify the 3-layer detection logic.
```bash
python3 ml_hids/services/escalation_test.py
```

## 📊 Detection Logic (Simplified)

| Signal | Condition | Action |
| :--- | :--- | :--- |
| **Normal** | 1-2 Fails, Low Velocity | `SAFE` (Score -1) |
| **Fast Fail** | 2 Fails in <3s | `EARLY WARNING` (Log Only) |
| **Suspicious** | ML Prob > 0.5 | `SUSPICIOUS` (Score +5) |
| **Attack** | ML Prob > 0.8 OR 10+ Fails/min | `BLOCK` (Score +50) |

## ⚠️ Disclaimer
This tool is a research prototype intended for educational purposes and authorized defensive security testing. The authors are not responsible for misuse or damage caused by this software.

## 📄 License
MIT License
