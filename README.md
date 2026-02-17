# Adaptive Hybrid Intrusion Detection Framework (AHIDF)

**[English]**  
Adaptive Hybrid Intrusion Detection Framework (AHIDF) is a research-driven behavioral intrusion detection engine designed to detect SSH brute-force attacks using hybrid intelligence mechanisms.

**[Bahasa Indonesia]**  
Adaptive Hybrid Intrusion Detection Framework (AHIDF) adalah sistem deteksi intrusi berbasis perilaku (behavior-based IDS) yang dikembangkan melalui riset mendalam untuk mendeteksi serangan brute-force SSH menggunakan mekanisme kecerdasan hibrida (Hybrid Intelligence).

---

Unlike traditional rule-based tools (e.g., Fail2Ban), AHIDF integrates:  
*Berbeda dengan IDS tradisional berbasis aturan (seperti Fail2Ban), AHIDF menggabungkan:*

*   **Heuristic Anomaly Detection / Deteksi Heuristik Cepat:** 
    *   [EN] Fast anomaly detection based on velocity and burst behavior.
    *   [ID] Menangkap anomali kecepatan login dan lonjakan aktivitas secara instan.
*   **Machine Learning Risk Scoring / Skoring Risiko Machine Learning:** 
    *   [EN] Uses RandomForest probability to determine threat level.
    *   [ID] Menggunakan probabilitas statistik untuk menentukan tingkat ancaman secara akurat.
*   **Persistent IP Reputation / Memori Reputasi IP:** 
    *   [EN] Tracks offender history for stricter responses.
    *   [ID] Mengingat sejarah penyerang untuk memberikan respons yang semakin tegas pada residivis.
*   **Multi-layer Escalation / Eskalasi Bertingkat:** 
    *   [EN] Adaptive response based on risk level (Warning -> Critical).
    *   [ID] Respons adaptif berdasarkan tingkat risiko (Peringatan -> Kritis).

The system is built as a modular research framework and can be extended into a full endpoint threat engine.  
*Sistem ini dibangun sebagai kerangka kerja riset modular yang siap dikembangkan menjadi mesin pertahanan endpoint (Endpoint Threat Engine) skala penuh.*

---

## 🏗️ Architecture / Arsitektur

AHIDF operates using a **3-Layer Hybrid Detection Model** / AHIDF menggunakan **Model Deteksi Hibrida 3 Lapis**:

### 🔹 Layer 1 – Heuristic Early Warning / Peringatan Dini
*   **[EN]** Fast detection of "Fast Fail" anomalies, high velocity, and short durations. Generates log warnings only.
*   **[ID]** Deteksi cepat untuk kegagalan kilat, kecepatan tinggi, dan durasi singkat. Hanya menghasilkan peringatan log.

### 🔹 Layer 2 – Machine Learning Risk Engine / Mesin Risiko ML
*   **[EN]** Analyze behavioral features (Failed Ratio, Time Density, Event Rate) to output risk probabilities: **SAFE → SUSPICIOUS → HIGH → CRITICAL**.
*   **[ID]** Menganalisis fitur perilaku (Rasio Gagal, Kepadatan Waktu, Laju Kejadian) untuk menghasilkan probabilitas risiko: **AMAN → MENCURIGAKAN → TINGGI → KRITIS**.

### 🔹 Layer 3 – Reputation & Hard Block / Reputasi & Blokir Tegas
*   **[EN]** Blocking triggers if: ML Prob > 0.8 AND Failed ≥ 3, OR Volume Attack (10+ fails/min), OR Bad Reputation Score.
*   **[ID]** Pemblokiran dipicu jika: Probabilitas ML > 0.8 DAN Gagal ≥ 3, ATAU Serangan Volume (10+ gagal/menit), ATAU Skor Reputasi Buruk.

---

## 📊 Behavioral Features / Fitur Perilaku

| Feature | Purpose (English) | Tujuan (Indonesia) |
| :--- | :--- | :--- |
| **Failure Velocity** | Detect script-based rapid attacks | Membedakan user biasa vs script otomatis |
| **Burst Flag** | Identify concentrated brute attempts | Mendeteksi brute-force cepat dalam durasi singkat |
| **Failed Ratio** | Detect imbalance of login attempts | Mengukur dominasi login gagal |
| **Event Rate** | Detect abnormal session density | Mengidentifikasi sesi dengan kepadatan aktivitas tinggi |
| **Persistence Score** | Track repeat offenders | Menghitung riwayat pelanggaran IP |

---

## 📂 Project Structure / Struktur Proyek

```
ml_hids/
├── core/                   # Core Logic / Logika Inti
│   └── feature_extractor.py 
├── services/               # Runtime Services / Layanan
│   ├── realtime_simulation.py # MAIN ENGINE
│   └── simulator.py         # Attack Simulator
├── scripts/                # Utilities / Alat Bantu
│   ├── train_model.py       # ML Training
│   └── generate_dataset.py  # Data Generator
├── models/
│   └── honeyport_model.pkl  # ML Model File
├── requirements.txt
└── README.md
```

---

## 🛠 Installation / Instalasi

**1. Clone & Setup Environment**
```bash
git clone https://github.com/yourusername/AHIDF.git
cd AHIDF
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Train Model / Latih Model**
```bash
# Generate dummy data / Buat data latih
python3 ml_hids/scripts/generate_dataset.py

# Train ML model / Latih model
python3 ml_hids/scripts/train_model.py
```

**3. Run Engine / Jalankan Sistem**
```bash
# Start Real-time Monitor
python3 ml_hids/services/realtime_simulation.py
```

**4. Test Simulation / Uji Simulasi**
```bash
# Run attack simulation / Jalankan simulasi serangan
python3 ml_hids/services/escalation_test.py
```

---

## ⚠ Disclaimer / Penafian

**[EN]** This tool is for authorized security research and defensive testing only. The developers are not responsible for misuse.  
**[ID]** Alat ini ditujukan khusus untuk riset keamanan dan pengujian pertahanan yang sah. Pengembang tidak bertanggung jawab atas penyalahgunaan alat ini.

## 📄 License

MIT License
