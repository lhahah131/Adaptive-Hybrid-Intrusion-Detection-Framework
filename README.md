# Adaptive Hybrid Intrusion Detection Framework (AHIDF)

Adaptive Hybrid Intrusion Detection Framework (AHIDF) is a research-driven behavioral intrusion detection engine designed to detect SSH brute-force attacks using hybrid intelligence mechanisms.

Adaptive Hybrid Intrusion Detection Framework (AHIDF) adalah sistem deteksi intrusi berbasis perilaku (behavior-based IDS) yang dirancang untuk mendeteksi serangan brute-force SSH menggunakan pendekatan hybrid berbasis kecerdasan buatan.

Unlike traditional rule-based tools (e.g., Fail2Ban), AHIDF integrates:  
Berbeda dengan sistem berbasis threshold tradisional (seperti Fail2Ban), AHIDF menggabungkan:

*   Heuristic anomaly detection / Deteksi anomali heuristik (cepat & ringan)
*   Machine learning probability scoring / Skoring risiko berbasis Machine Learning
*   Persistent IP reputation memory / Memori reputasi IP jangka panjang
*   Multi-layer escalation logic / Mekanisme eskalasi bertingkat (multi-layer decision engine)

The system is built as a modular research framework and can be extended into a full endpoint threat engine.  
Framework ini dikembangkan sebagai alat riset keamanan siber yang modular dan dapat diperluas menjadi sistem deteksi ancaman endpoint yang lebih komprehensif.

## 🏗️ Architecture

AHIDF operates using a 3-Layer Hybrid Detection Model / AHIDF menggunakan model deteksi hybrid 3 lapis:

### 🔹 Layer 1 – Heuristic Early Warning / Early Warning (Heuristik Cepat)

Fast anomaly detection based on:  
Mendeteksi pola anomali awal berdasarkan:

*   Failure velocity / Kecepatan gagal login
*   Rapid burst behavior / Lonjakan login dalam waktu sangat singkat
*   Short-duration login attempts / Durasi sesi yang tidak wajar

⚠️ **Generates warning without blocking / Layer ini hanya memberikan peringatan (tanpa blokir) untuk menghindari false positive.**

### 🔹 Layer 2 – Machine Learning Risk Engine

RandomForest-based classifier trained on behavioral features / Menggunakan model RandomForest yang dilatih dengan fitur perilaku seperti:

*   Failed ratio
*   Failure velocity
*   Event rate
*   Time density / Time-based density
*   Burst flag
*   Session duration

Outputs smooth risk probability / Output berupa probabilitas risiko yang dipetakan menjadi:  
**SAFE → SUSPICIOUS → HIGH → CRITICAL**

### 🔹 Layer 3 – Reputation & Hard Block Engine

Decision logic triggers blocking if / Mekanisme pemblokiran aktif berdasarkan kondisi:

*   ML probability > 0.8 AND failed ≥ 3
*   OR 10+ failures in < 60 seconds / ATAU ≥ 10 gagal login dalam 60 detik
*   OR persistent offender score exceeded / ATAU IP dengan riwayat pelanggaran berulang

Supports / Fitur tamabahan:

*   IP history memory / Memori reputasi IP
*   Escalation scoring / Skor eskalasi pelanggaran
*   Risk decay mechanism / Mekanisme penurunan risiko (risk decay)

## 📊 Behavioral Features

| Feature | Purpose | Fitur | Tujuan |
| :--- | :--- | :--- | :--- |
| **Failure Velocity** | Detect script-based rapid attacks | **Failure Velocity** | Membedakan user biasa vs script otomatis |
| **Burst Flag** | Identify concentrated brute attempts | **Burst Flag** | Mendeteksi brute-force cepat dalam durasi singkat |
| **Failed Ratio** | Detect imbalance of login attempts | **Failed Ratio** | Mengukur dominasi login gagal |
| **Event Rate** | Detect abnormal session density | **Event Rate** | Mengidentifikasi sesi dengan kepadatan aktivitas tinggi |
| **Persistence Score** | Track repeat offenders | **Persistence Score** | Menghitung riwayat pelanggaran IP |

## 🎯 Design Goals

*   Minimize false positives (ignore 1–2 normal login mistakes) / Mengurangi false positive (1–2 kesalahan login tidak dianggap serangan)
*   Detect rapid automated brute-force / Mendeteksi serangan otomatis dengan respons cepat
*   Provide SOC-friendly risk scoring / Memberikan skor risiko yang informatif untuk analis SOC
*   Support adaptive thresholding / Mendukung adaptive threshold berbasis riwayat IP
*   Allow extensibility for malware & endpoint modules / Modular dan dapat diperluas menjadi Endpoint Threat Engine

## 📂 Project Structure

```
ml_hids/
├── core/
│   └── feature_extractor.py
├── services/
│   ├── realtime_simulation.py
│   └── simulator.py
├── scripts/
│   ├── train_model.py
│   └── generate_dataset.py
├── models/
│   └── honeyport_model.pkl (excluded)
├── requirements.txt
└── README.md
```

## 🛠 Installation

```bash
git clone https://github.com/yourusername/AHIDF.git
cd AHIDF
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Training the Model / Melatih Model

```bash
python3 ml_hids/scripts/generate_dataset.py
python3 ml_hids/scripts/train_model.py
```

## 🚀 Run Real-Time Engine / Menjalankan Engine Real-Time

```bash
python3 ml_hids/services/realtime_simulation.py
```
*Note: Ensure log path is configured correctly / Pastikan path log (misalnya Cowrie) sudah dikonfigurasi dengan benar.*

## 🧪 Testing Detection Escalation

```bash
python3 ml_hids/services/escalation_test.py
```

This validates / Digunakan untuk menguji:

*   Early warning detection
*   Probability escalation / Eskalasi probabilitas ML
*   Block decision logic / Keputusan pemblokiran
*   Reputation memory / Sistem reputasi IP

## 🔬 Research Focus

This framework is designed as:  
Framework ini dirancang sebagai:

*   A behavioral intrusion detection research tool / Alat penelitian deteksi intrusi berbasis perilaku
*   A modular AI security experimentation environment / Lingkungan eksperimen AI Security
*   A foundation for endpoint threat intelligence systems / Fondasi untuk pengembangan sistem endpoint threat detection

Future extensions may include / Pengembangan lanjutan yang memungkinkan:

*   Malware entropy scanning / Deteksi malware berbasis entropy & hash
*   Command sequence anomaly modeling / Analisis urutan perintah (command sequence modeling)
*   Adaptive thresholding via reinforcement learning / Adaptive threshold berbasis reinforcement learning
*   Model drift monitoring

## ⚠ Disclaimer

This tool is for authorized security research and defensive testing only. / Alat ini ditujukan untuk riset keamanan dan pengujian defensif yang sah. Segala bentuk penyalahgunaan berada di luar tanggung jawab pengembang.

## 📄 License

MIT License
