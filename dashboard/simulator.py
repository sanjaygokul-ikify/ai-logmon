"""
simulator.py — Demo log generator for the AI LogMon dashboard.

Runs in a background thread and inserts realistic fake log entries
into the database every 1–3 seconds. This lets the dashboard work
out of the box without needing a real AI system connected.
"""

import random
import threading
import time

from db import insert_log, insert_error

# ---------------------------------------------------------------------------
# Simulated log sources and messages
# ---------------------------------------------------------------------------

SOURCES = ["ai-model", "data-pipeline", "api-server", "auth-service"]

# Messages grouped by log level
MESSAGES = {
    "INFO": [
        "Request processed successfully",
        "Model inference completed in 142ms",
        "Data batch uploaded — 1,024 records",
        "Health check passed",
        "Cache refreshed for prediction endpoint",
        "New session started for user #4821",
        "Scheduled job completed: data sync",
        "API response served in 38ms",
    ],
    "WARNING": [
        "Response latency above threshold (>500ms)",
        "Memory usage at 82% — consider scaling",
        "Retrying failed API call (attempt 2/3)",
        "Deprecated endpoint called: /v1/predict",
        "Rate limit approaching for client 10.0.3.7",
        "Disk usage at 78% on data volume",
    ],
    "ERROR": [
        "Connection refused: database unreachable",
        "Model prediction failed — input shape mismatch",
        "Timeout waiting for upstream service",
        "Out of memory during batch processing",
        "Authentication token expired for service account",
        "Failed to write checkpoint — permission denied",
    ],
    "DEBUG": [
        "Loaded model weights from /models/v3.2.bin",
        "Feature vector shape: (1, 512)",
        "Cache hit for key: user_prefs_4821",
        "Garbage collection freed 128MB",
    ],
}

# Error severity mapping — more severe messages get higher severity
ERROR_SEVERITIES = ["low", "medium", "high", "critical"]


def _pick_level():
    """Choose a random log level with realistic distribution."""
    return random.choices(
        population=["INFO", "WARNING", "DEBUG", "ERROR"],
        weights=[50, 25, 15, 10],  # Percentage-like weights
        k=1,
    )[0]


def _generate_one_log():
    """Generate and insert a single random log entry."""
    level = _pick_level()
    source = random.choice(SOURCES)
    message = random.choice(MESSAGES[level])

    # Insert into the logs table
    insert_log(level, source, message)

    # If it's an ERROR, also insert into the errors table
    if level == "ERROR":
        severity = random.choice(ERROR_SEVERITIES)
        insert_error(source, message, severity)


def run_simulator():
    """
    Continuously generate log entries in a loop.

    This function is meant to be run inside a daemon thread so it
    automatically stops when the main program exits.
    """
    while True:
        _generate_one_log()
        # Sleep 1–3 seconds between entries
        time.sleep(random.uniform(1.0, 3.0))


def start_simulator():
    """Start the log simulator in a background daemon thread."""
    thread = threading.Thread(target=run_simulator, daemon=True)
    thread.start()
    print(" * Log simulator started (generating demo data)")
    return thread
