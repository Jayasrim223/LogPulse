\# 📊 LogPulse - Server Log Analytics



LogPulse is a Data Analytics and DevOps project that analyzes server logs and displays key performance metrics through an interactive Streamlit dashboard.



\## 🚀 Features



\- Server log parsing using Python

\- Data analysis using Pandas

\- HTTP status code analysis

\- Endpoint usage analysis

\- HTTP method analysis

\- Error analysis

\- PostgreSQL database integration

\- Interactive Streamlit dashboard

\- Docker containerization

\- GitHub Actions CI

\- Cloud deployment



\## 🏗️ Architecture



Server Logs

&#x20;  ↓

Python + Pandas

&#x20;  ↓

PostgreSQL

&#x20;  ↓

Streamlit Dashboard

&#x20;  ↓

Docker

&#x20;  ↓

GitHub Actions

&#x20;  ↓

Cloud Deployment



\## 🛠️ Technologies Used



\- Python

\- Pandas

\- PostgreSQL

\- SQL

\- Streamlit

\- Docker

\- Git

\- GitHub

\- GitHub Actions



\## 📊 Dashboard



The dashboard displays:



\- Total Requests

\- Successful Requests

\- Success Rate

\- Error Rate

\- HTTP Status Breakdown

\- Endpoint Usage

\- HTTP Method Usage

\- Error Analysis

\- Log Data



\## 🌐 Live Demo



https://logpulse-dtpk6ronsugyh35vtuc78t.streamlit.app/



\## 📁 Project Structure



```text

logpulse/

├── .github/

│   └── workflows/

│       └── docker-build.yml

├── app/

│   ├── \_\_init\_\_.py

│   ├── analyzer.py

│   ├── database.py

│   └── dashboard.py

├── demo\_server.log

├── Dockerfile

├── load\_to\_db.py

├── mock\_generator.py

├── requirements.txt

└── README.md

