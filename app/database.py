import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="logpulse",
        user="postgres",
        password="LogPulse@123",
        port="5432"
    )


def insert_logs(df):
    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO logs (timestamp, ip, method, endpoint, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                row["timestamp"],
                row["ip"],
                row["method"],
                row["endpoint"],
                row["status"]
            )
        )

    connection.commit()
    cursor.close()
    connection.close()

    print(f"{len(df)} logs inserted into PostgreSQL.")