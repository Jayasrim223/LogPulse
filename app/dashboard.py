import streamlit as st
import pandas as pd
import re
from pathlib import Path

st.set_page_config(
    page_title="LogPulse Dashboard",
    page_icon="📊",
    layout="wide"
)

LOG_PATTERN = re.compile(
    r"\[(.*?)\]\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)"
)

records = []

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "demo_server.log"

with open(LOG_FILE, "r") as file:

    for line in file:
        match = LOG_PATTERN.match(line.strip())

        if match:
            timestamp, ip, method, endpoint, status = match.groups()

            records.append({
                "timestamp": timestamp,
                "ip": ip,
                "method": method,
                "endpoint": endpoint,
                "status": int(status)
            })

df = pd.DataFrame(records)

df["timestamp"] = pd.to_datetime(df["timestamp"])

st.title("📊 LogPulse - Server Log Analytics")
st.write("Data Analytics Dashboard for Server Logs")

total_requests = len(df)
successful_requests = len(df[df["status"] == 200])
failed_requests = len(df[df["status"] != 200])

success_rate = successful_requests / total_requests * 100
error_rate = failed_requests / total_requests * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Requests", total_requests)
col2.metric("Successful Requests", successful_requests)
col3.metric("Success Rate", f"{success_rate:.2f}%")
col4.metric("Error Rate", f"{error_rate:.2f}%")

st.divider()

st.subheader("HTTP Status Breakdown")
st.bar_chart(df["status"].value_counts().sort_index())

st.subheader("Endpoint Usage")
st.bar_chart(df["endpoint"].value_counts())

st.subheader("HTTP Method Usage")
st.bar_chart(df["method"].value_counts())

st.subheader("Error Analysis")
errors = df[df["status"] != 200]

st.bar_chart(errors["status"].value_counts().sort_index())

st.subheader("Log Data")
st.dataframe(df, use_container_width=True)