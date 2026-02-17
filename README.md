Adaptive Hybrid Intrusion Detection Framework (AHIDF)
🧠 Overview

Adaptive Hybrid Intrusion Detection Framework (AHIDF) is a research-driven behavioral intrusion detection engine designed to detect SSH brute-force attacks using hybrid intelligence mechanisms.

Unlike traditional rule-based tools (e.g., Fail2Ban), AHIDF integrates:

Heuristic anomaly detection

Machine learning probability scoring

Persistent IP reputation memory

Multi-layer escalation logic

The system is built as a modular research framework and can be extended into a full endpoint threat engine.
Adaptive Hybrid Intrusion Detection Framework (AHIDF) adalah sistem deteksi intrusi berbasis perilaku (behavior-based IDS) yang dirancang untuk mendeteksi serangan brute-force SSH menggunakan pendekatan hybrid berbasis kecerdasan buatan.

Berbeda dengan sistem berbasis threshold tradisional (seperti Fail2Ban), AHIDF menggabungkan:

Deteksi anomali heuristik (cepat & ringan)

Skoring risiko berbasis Machine Learning

Memori reputasi IP jangka panjang

Mekanisme eskalasi bertingkat (multi-layer decision engine)

Framework ini dikembangkan sebagai alat riset keamanan siber yang modular dan dapat diperluas menjadi sistem deteksi ancaman endpoint yang lebih komprehensif.

🏗️ Architecture

AHIDF operates using a 3-Layer Hybrid Detection Model:

🔹 Layer 1 – Heuristic Early Warning

Fast anomaly detection based on:

Failure velocity

Rapid burst behavior

Short-duration login attempts

⚠️ Generates warning without blocking.

🔹 Layer 2 – Machine Learning Risk Engine

RandomForest-based classifier trained on behavioral features:

Failed ratio

Failure velocity

Event rate

Time density

Burst flag

Session duration

Outputs smooth risk probability:
SAFE → SUSPICIOUS → HIGH → CRITICAL

🔹 Layer 3 – Reputation & Hard Block Engine

Decision logic triggers blocking if:

ML probability > 0.8 AND failed ≥ 3

OR 10+ failures in < 60 seconds

OR persistent offender score exceeded

Supports:

IP history memory

Escalation scoring

Risk decay mechanism
AHIDF menggunakan model deteksi hybrid 3 lapis:

🔹 Layer 1 – Early Warning (Heuristik Cepat)

Mendeteksi pola anomali awal berdasarkan:

Failure velocity (kecepatan gagal login)

Burst behavior (lonjakan login dalam waktu sangat singkat)

Durasi sesi yang tidak wajar

⚠️ Layer ini hanya memberikan peringatan (tanpa blokir) untuk menghindari false positive.

🔹 Layer 2 – Machine Learning Risk Engine

Menggunakan model RandomForest yang dilatih dengan fitur perilaku seperti:

Failed ratio

Failure velocity

Event rate

Time-based density

Burst flag

Session duration

Output berupa probabilitas risiko yang dipetakan menjadi:

SAFE → SUSPICIOUS → HIGH → CRITICAL

🔹 Layer 3 – Reputation & Hard Block Engine

Mekanisme pemblokiran aktif berdasarkan kondisi:

Probabilitas ML > 0.8 DAN gagal login ≥ 3

ATAU ≥ 10 gagal login dalam 60 detik

ATAU IP dengan riwayat pelanggaran berulang

Fitur tambahan:

Memori reputasi IP

Skor eskalasi pelanggaran

Mekanisme penurunan risiko (risk decay)

📊 Behavioral Features
Feature	Purpose
Failure Velocity	Detect script-based rapid attacks
Burst Flag	Identify concentrated brute attempts
Failed Ratio	Detect imbalance of login attempts
Event Rate	Detect abnormal session density
Persistence Score	Track repeat offenders

Fitur	Tujuan
Failure Velocity	Membedakan user biasa vs script otomatis
Burst Flag	Mendeteksi brute-force cepat dalam durasi singkat
Failed Ratio	Mengukur dominasi login gagal
Event Rate	Mengidentifikasi sesi dengan kepadatan aktivitas tinggi
Persistence Score	Menghitung riwayat pelanggaran IP

🎯 Design Goals

Minimize false positives (ignore 1–2 normal login mistakes)

Detect rapid automated brute-force

Provide SOC-friendly risk scoring

Support adaptive thresholding

Allow extensibility for malware & endpoint modules
Mengurangi false positive (1–2 kesalahan login tidak dianggap serangan)

Mendeteksi serangan otomatis dengan respons cepat

Memberikan skor risiko yang informatif untuk analis SOC

Mendukung adaptive threshold berbasis riwayat IP

Modular dan dapat diperluas menjadi Endpoint Threat Engine

📂 Project Structure
ml_hids/
├── core/
│   └── feature_extractor.py
├── services/
│   ├── realtime_simulation.py
│   └── simulator.py
├── scripts/
│   ├── train_model_enhanced.py
│   └── generate_dataset_v2.py
├── models/
│   └── honeyport_model.pkl (excluded)
├── requirements.txt
└── README.md

🛠 Installation
git clone https://github.com/yourusername/AHIDF.git
cd AHIDF
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

⚙️ Training the Model/Melatih Model
python3 ml_hids/scripts/generate_dataset_v2.py
python3 ml_hids/scripts/train_model_enhanced.py

🚀 Run Real-Time Engine/Menjalankan Engine Real-Time
python3 ml_hids/services/realtime_simulation.py

Ensure log path is configured correctly.
Pastikan path log (misalnya Cowrie) sudah dikonfigurasi dengan benar.

🧪 Testing Detection Escalation
python3 ml_hids/services/escalation_test.py

This validates:

Early warning

Probability escalation

Block decision logic

Reputation memory

Digunakan untuk menguji:

Early warning detection

Eskalasi probabilitas ML

Keputusan pemblokiran

Sistem reputasi IP

🔬 Research Focus

This framework is designed as:

A behavioral intrusion detection research tool

A modular AI security experimentation environment

A foundation for endpoint threat intelligence systems

Future extensions may include:

Malware entropy scanning

Command sequence anomaly modeling

Adaptive thresholding via reinforcement learning

Model drift monitoring
Framework ini dirancang sebagai:

Alat penelitian deteksi intrusi berbasis perilaku

Lingkungan eksperimen AI Security

Fondasi untuk pengembangan sistem endpoint threat detection

Pengembangan lanjutan yang memungkinkan:

Deteksi malware berbasis entropy & hash

Analisis urutan perintah (command sequence modeling)

Adaptive threshold berbasis reinforcement learning

Model drift monitoring

⚠ Disclaimer

This tool is for authorized security research and defensive testing only.
Alat ini ditujukan untuk riset keamanan dan pengujian defensif yang sah. Segala bentuk penyalahgunaan berada di luar tanggung jawab pengembang.

📄 License

MIT License
