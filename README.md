# 📊 LogPulse - Server Log Analytics

**🚀 [Live Demo](https://logpulse-dtpk6ronsugyh35vtuc78t.streamlit.app/)**

LogPulse is a Data Analytics and DevOps project that analyzes server logs and displays key performance metrics through an interactive Streamlit dashboard.

## 🚀 Features

* Server log parsing using Python
* Data analysis using Pandas
* HTTP status code analysis
* Endpoint usage analysis
* HTTP method analysis
* Error analysis
* PostgreSQL database integration
* Interactive Streamlit dashboard
* Docker containerization
* GitHub Actions CI
* Cloud deployment

## 🏗️ Architecture

```text
Server Logs
     ↓
Python + Pandas
     ↓
PostgreSQL
     ↓
Streamlit Dashboard
     ↓
Docker
     ↓
GitHub Actions
     ↓
Cloud Deployment
```

## 🛠️ Technologies Used

* Python
* Pandas
* PostgreSQL
* SQL
* Streamlit
* Docker
* Git
* GitHub
* GitHub Actions

## 📊 Dashboard

The dashboard displays:

* Total Requests
* Successful Requests
* Success Rate
* Error Rate
* HTTP Status Breakdown
* Endpoint Usage
* HTTP Method Usage
* Error Analysis
* Log Data

## 🌐 Live Demo

👉 **[Open LogPulse Dashboard](https://logpulse-dtpk6ronsugyh35vtuc78t.streamlit.app/)**

## 📁 Project Structure

```text
logpulse/
├── .github/
│   └── workflows/
│       └── docker-build.yml
├── app/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── database.py
│   └── dashboard.py
├── demo_server.log
├── Dockerfile
├── load_to_db.py
├── mock_generator.py
├── requirements.txt
└── README.md
```
