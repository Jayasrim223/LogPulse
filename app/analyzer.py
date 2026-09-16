import pandas as pd
import re

LOG_PATTERN = re.compile(
    r"\[(.*?)\]\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)"
)


def load_logs(file_path="server.log"):
    records = []

    with open(file_path, "r") as file:
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

    # Convert timestamp from text to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def analyze_logs(df):

    total_requests = len(df)

    successful_requests = len(df[df["status"] == 200])

    failed_requests = len(df[df["status"] != 200])

    error_rate = (failed_requests / total_requests) * 100

    success_rate = (successful_requests / total_requests) * 100

    most_used_endpoint = df["endpoint"].value_counts().idxmax()

    most_common_status = df["status"].value_counts().idxmax()

    print("\n========== LOGPULSE ANALYTICS ==========")

    print(f"Total Requests      : {total_requests}")
    print(f"Successful Requests : {successful_requests}")
    print(f"Failed Requests     : {failed_requests}")
    print(f"Success Rate        : {success_rate:.2f}%")
    print(f"Error Rate          : {error_rate:.2f}%")
    print(f"Most Used Endpoint  : {most_used_endpoint}")
    print(f"Most Common Status  : {most_common_status}")

    print("\n========== STATUS BREAKDOWN ==========")
    print(df["status"].value_counts())

    print("\n========== ENDPOINT BREAKDOWN ==========")
    print(df["endpoint"].value_counts())

    print("\n========== METHOD BREAKDOWN ==========")
    print(df["method"].value_counts())

    print("\n========== ERROR ANALYSIS ==========")

    errors = df[df["status"] != 200]

    print(errors["status"].value_counts())

    print("\n========== REQUESTS BY TIME ==========")

    df["minute"] = df["timestamp"].dt.floor("min")

    print(df["minute"].value_counts().sort_index())


if __name__ == "__main__":

    df = load_logs()

    analyze_logs(df)