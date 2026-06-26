"""
app.py — Flask entry point for the AI LogMon dashboard.

Run this file to start the dashboard:
    python dashboard/app.py

The server will be available at http://localhost:5000
"""

import sys
import os

# Add the project root to sys.path so we can import from src/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from flask import Flask
from loguru import logger

from db import init_db, insert_log, insert_error
from routes import dashboard_bp
from simulator import start_simulator


# -----------------------------------------------------------------------
# Loguru sink — captures logs from LogCollector and writes to our DB
# -----------------------------------------------------------------------

def loguru_sink(message):
    """
    Custom loguru sink that writes every log message into the
    dashboard's SQLite database. This captures output from
    LogCollector (and any other code using loguru).
    """
    record = message.record
    level = record["level"].name       # e.g. "INFO", "ERROR"
    source = record["module"]          # e.g. "log_collector"
    text = record["message"]           # the actual log message

    insert_log(level, source, text)

    # Also track errors in the errors table
    if level == "ERROR":
        insert_error(source, text, "medium")


def create_app():
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__)

    # Initialize the database (creates tables if needed)
    init_db()

    # Register the dashboard routes Blueprint
    app.register_blueprint(dashboard_bp)

    # Add our DB sink to loguru so we capture LogCollector's output
    logger.add(loguru_sink, format="{message}")

    # Start the LogCollector and ErrorReporter from src/
    from log_collector import LogCollector
    from error_reporter import ErrorReporter

    collector = LogCollector()
    collector.start()

    reporter = ErrorReporter()
    reporter.start()

    # Start the background log simulator (demo data)
    start_simulator()

    return app


# ---------------------------------------------------------------------------
# Run the development server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    print(" * Dashboard running at http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
