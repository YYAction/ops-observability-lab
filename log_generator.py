"""
Every few seconds, append a log line to simulate a running service.
"""
import time
import random
import datetime
import os

LOG_DIR = os.environ.get("LOG_DIR", "./sample-logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

LINES = [
    "INFO  service health check passed",
    "INFO  request processed successfully",
    "INFO  user session created",
    "WARNING  response time exceeded 2000ms",
    "ERROR  database connection timeout",
    "ERROR  deadlock detected in transaction",
    "ERROR  service offline - connection refused",
    "INFO  scheduled task completed",
    "INFO  cache refreshed",
    "WARNING  disk usage above 80%",
]
WEIGHTS = [20, 20, 15, 5, 3, 1, 1, 10, 10, 5]

os.makedirs(LOG_DIR, exist_ok=True)

while True:
    line = random.choices(LINES, weights=WEIGHTS, k=1)[0]
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {line}\n")
    time.sleep(random.uniform(1, 5))
