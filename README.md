# 🛡️ SentinelFraud Credit Risk Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**A hybrid AI-powered credit risk assessment engine combining rule-based scoring with machine learning predictions**
[Project](https://github.com/Anushre2005/SentinelFraud-Credit-Risk-Engine/blob/main/TECHNICAL_DOCUMENTATION.md) • [Installation](#-installation) • [API Reference](#-api-reference) • [Architecture](#-architecture)

</div>

---

## 📋 Overview

SentinelFraud Credit Risk Engine is a sophisticated credit assessment platform that leverages both traditional rule-based scoring and machine learning to provide accurate, explainable credit risk evaluations. The system is designed to be regulator-ready with full transparency in scoring decisions.

### 🎯 Key Highlights

- **Hybrid Scoring Model**: Combines rule-based scoring with ML predictions for robust assessments
- **Real-time Analysis**: Instant credit risk evaluation via REST API
- **Interactive Dashboard**: Beautiful dark-themed UI with data visualizations
- **Explainable AI**: Clear breakdown of all scoring factors
- **Personalized Recommendations**: Smart tips to improve credit scores

---

## ✨ Features

### 🔍 Credit Assessment
- Multi-factor risk evaluation
- ML-powered fraud detection
- Network trust analysis
- Address stability scoring

### 📊 Visualizations
- **Score Breakdown Chart**: Doughnut chart showing score composition
- **Risk Factors Radar**: Compare user profile against ideal benchmarks
- **Interactive Progress Bars**: Visual representation of each scoring component

### 💡 Smart Recommendations
- Personalized improvement tips based on weak areas
- Priority-ranked action items (High/Medium/Low)
- 90-day action plan for credit improvement
- Different strategies for Low/Medium/High risk profiles

### 🏗️ Technical Features
- RESTful API with FastAPI
- CORS-enabled for frontend integration
- Auto-generated API documentation (Swagger/OpenAPI)
- Modular architecture for easy extension

---

## 🚀 Demo

### Dashboard Preview
The frontend provides a sleek, modern interface with:

- **Dark Theme**: Easy on the eyes with glassmorphism effects
- **Animated Score Circle**: Visual representation of credit score
- **Risk Band Indicator**: Color-coded risk levels (Green/Yellow/Red)
- **Detailed Analysis Cards**: Comprehensive breakdown of all factors

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Anushre2005/SentinelFraud-Credit-Risk-Engine.git
cd SentinelFraud-Credit-Risk-Engine
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn app.main:app --reload
```

5. **Access the application**
- **Frontend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 📡 API Reference

### Credit Assessment Endpoint

```http
POST /credit/assess
```

#### Request Body

```json
{
  "user_id": "U_001",
  "age": 34,
  "occupation": "salaried",
  "monthly_income": 4500.00,
  "transaction_count_30d": 35,
  "avg_transaction_amount": 120.50,
  "location_risk_score": 0.12,
  "device_change_frequency": 1,
  "previous_fraud_flag": 0,
  "account_age_months": 48,
  "chargeback_count": 0
}
```

#### Response

```json
{
  "assessment_id": "CR-U_001-20260115001143",
  "timestamp": "2026-01-15T00:11:43.919561",
  "applicant": {
    "user_id": "U_001",
    "age": 34,
    "occupation": "salaried",
    "account_age_months": 48
  },
  "rule_scoring": {
    "base_score": 244,
    "ctc_adjustment": 0,
    "address_adjustment": 0,
    "total_adjustment": 0,
    "final_rule_score": 244
  },
  "ml_scoring": {
    "high_risk_probability": 0.0028,
    "ml_score": 2,
    "model_auc": 0.686
  },
  "decision": {
    "final_credit_score": 98,
    "risk_band": "Low",
    "reason_codes": []
  }
}
```

---

## 🏛️ Architecture

```
sentinelfraud-credit-engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── api/
│   │   └── credit.py        # Credit assessment endpoints
│   ├── scoring/
│   │   └── ...              # Scoring logic and ML models
│   ├── artifacts/
│   │   └── credit_model.joblib  # Trained ML model
│   ├── audit/
│   │   └── ...              # Decision logging
│   └── utils/
│       └── ...              # Helper utilities
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # CSS styles (dark theme)
│   └── script.js            # JavaScript logic & Chart.js
├── scripts/
│   └── ...                  # Utility scripts
├── requirements.txt         # Python dependencies
├── sample_request.json      # Example API request
└── README.md
```

---

## 🧠 Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Rule-Based Score** | Primary | Demographic and behavioral rule evaluation |
| **ML Risk Score** | Secondary | Machine learning fraud probability |
| **Network Trust (CTC)** | Modifier | Community trust circle analysis |
| **Address Stability** | Modifier | Residential stability assessment |

### Risk Bands

| Score Range | Risk Band | Color |
|-------------|-----------|-------|
| 0-300 | High Risk | 🔴 Red |
| 301-600 | Medium Risk | 🟡 Yellow |
| 601-1000 | Low Risk | 🟢 Green |

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python, FastAPI, Uvicorn |
| **ML** | Scikit-learn, Joblib |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Charts** | Chart.js |
| **Styling** | Custom CSS with Glassmorphism |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Anushre**

- GitHub: [@Anushre2005](https://github.com/Anushre2005)

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

Made with ❤️ for the GenAI Hackathon 2025

</div>
