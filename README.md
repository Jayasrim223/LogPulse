# LogPulse - Server Log Analytics

**Live Demo:** https://logpulse-dtpk6ronsugyh35vtuc78t.streamlit.app/

LogPulse is a Python-based server log analytics and error detection project. It parses application/server logs, analyzes HTTP requests and errors, and presents the results through an interactive Streamlit dashboard.

The project also includes PostgreSQL integration, Docker containerization, automated testing with pytest, and a GitHub Actions CI pipeline.

## Features

* Server log parsing using Python
* Data analysis using Pandas
* HTTP status code analysis
* Endpoint usage analysis
* HTTP method analysis
* Error detection and summary
* PostgreSQL database integration
* Interactive Streamlit dashboard
* Docker containerization
* Automated testing with pytest
* GitHub Actions CI
* Cloud deployment

## Architecture

```text
                    server.log
                        |
                        v
                Python + Pandas
                        |
             +----------+----------+
             |                     |
             v                     v
      Error Detection       PostgreSQL
             |               Database
             |                     |
             +----------+----------+
                        |
                        v
              Streamlit Dashboard
                        |
                        v
                     Docker
                        |
                        v
                 GitHub Actions
```

## Technologies Used

* Python
* Pandas
* PostgreSQL
* SQL
* Streamlit
* Docker
* Git
* GitHub
* GitHub Actions
* Pytest

## Dashboard

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

## Error Detection

LogPulse identifies unsuccessful HTTP requests and provides an error summary, including:

* Total errors
* Client errors (4xx)
* Server errors (5xx)
* HTTP status breakdown

## Testing

The project includes automated tests using pytest.

The tests verify:

* Log file loading
* Log data structure
* Error detection
* Error summary results

GitHub Actions automatically runs the tests whenever changes are pushed to the `main` branch.

## Docker

LogPulse can be run as a Docker container.

```bash
docker build -t logpulse .
docker run -p 8501:8501 logpulse
```

Then open:

```text
http://localhost:8501
```

## Live Demo

**Open LogPulse Dashboard:**

https://logpulse-dtpk6ronsugyh35vtuc78t.streamlit.app/

## Project Structure

```text
logpulse/
├── .github/
│   └── workflows/
│       └── docker-build.yml
├── app/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── database.py
│   ├── dashboard.py
│   └── error_detector.py
├── server.log
├── Dockerfile
├── load_to_db.py
├── mock_generator.py
├── requirements.txt
├── test_db.py
├── test_logpulse.py
└── README.md
```

## CI Pipeline

The GitHub Actions workflow performs the following steps:

```text
Push to GitHub
      |
      v
Checkout Code
      |
      v
Setup Python
      |
      v
Install Dependencies
      |
      v
Run Pytest
      |
      v
Build Docker Image
```

## Project Goal

The goal of LogPulse is to make server log analysis easier by automatically converting raw log entries into structured analytics, error information, and visual insights through a dashboard.

