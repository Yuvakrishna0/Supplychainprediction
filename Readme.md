[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuva-krishna/supplychain-early-warning/blob/main/notebooks/training_pipeline.ipynb)
# 🌍 Supply Chain Disruption Early Warning System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51-ff4b4b)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Cloud-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Author:** Yuva Krishna  
**Institution:** Saveetha Engineering College  
**Course:** B.E. IoT — Final Year Project  

---

## 🧭 Overview

This project — **PredictChain** — is an AI-driven **early warning system** that predicts potential **supply chain disruptions** by analyzing real-time data from multiple sources such as:
- **Shipping metrics**
- **Global event databases (GDELT)**
- **Sentiment and tone indicators**

It provides early alerts and interactive visualizations for stakeholders to anticipate risks and take preventive measures.

---

## 🚀 Live Resources

| Resource | Link | Description |
|-----------|------|-------------|
| 🎓 **Google Colab Notebook** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuva-krishna/supplychain-early-warning/blob/main/notebooks/training_pipeline.ipynb) | Run the full data ingestion, feature engineering & training pipeline |
| 🖥️ **Dashboard (Hugging Face)** | [View Streamlit App](https://huggingface.co/spaces/yuva-krishna/SupplyChainDashboard) | Visualize predicted risk levels |
| 📊 **Model Tracking (DagsHub)** | [MLflow Dashboard](https://dagshub.com/yuva-krishna/supplychainprediction.mlflow) | Explore model metrics & artifacts |
| 💾 **Database (Neon PostgreSQL)** | [Neon Console](https://neon.tech) | Cloud-hosted Postgres storing predictions |

---

## 🧩 Architecture

```text
                ┌────────────────────────┐
                │   Google Colab (Free)   │
                │------------------------ │
                │ Data Ingestion + Model  │
                │ Training + Logging      │
                └────────────┬────────────┘
                             │
                             ▼
          ┌────────────────────────────┐
          │ Neon PostgreSQL (Database) │
          │  - features_supply_risk    │
          │  - scores_daily            │
          └────────────┬───────────────┘
                       │
                       ▼
      ┌────────────────────────────────────┐
      │  Hugging Face Spaces (Streamlit)   │
      │  - Dashboard Visualization         │
      └────────────────────────────────────┘
                       │
                       ▼
         ┌──────────────────────────┐
         │ DagsHub (MLflow Tracker) │
         │  - Model Metrics/Artifacts│
         └──────────────────────────┘
