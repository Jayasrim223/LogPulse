import time
import random
from datetime import datetime

METHODS = ["GET", "POST", "DELETE", "PUT"]

STATUS_CODES = [200, 200, 200, 404, 500, 401]

ENDPOINTS = [
    "/api/v1/login",
    "/api/v1/checkout",
    "/api/v1/products",
    "/api/v1/dashboard"
]

print("Generating mock server logs...")
print("Press Ctrl+C to stop.")

with open("server.log", "a") as f:
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip = f"192.168.1.{random.randint(1, 254)}"
            method = random.choice(METHODS)
            endpoint = random.choice(ENDPOINTS)
            status = random.choice(STATUS_CODES)

            log_line = (
                f"[{timestamp}] {ip} "
                f"{method} {endpoint} {status}\n"
            )

            f.write(log_line)
            f.flush()

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nLog generation stopped.")