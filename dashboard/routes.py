"""
routes.py — API endpoints for the AI LogMon dashboard.

Uses a Flask Blueprint so that routes are modular and can be
registered with the main Flask app in app.py.
"""

from flask import Blueprint, jsonify, request, render_template

from db import get_logs, get_errors, get_stats

# Create a Blueprint named "dashboard"
dashboard_bp = Blueprint("dashboard", __name__)


# -----------------------------------------------------------------------
# Page route
# -----------------------------------------------------------------------

@dashboard_bp.route("/")
def index():
    """Serve the main dashboard page."""
    return render_template("index.html")


# -----------------------------------------------------------------------
# API routes — all return JSON
# -----------------------------------------------------------------------

@dashboard_bp.route("/api/logs")
def api_logs():
    """
    Return recent log entries as JSON.

    Query parameters:
        level  — filter by log level (e.g. ?level=ERROR). Optional.
        limit  — max rows to return (default 100). Optional.
    """
    level = request.args.get("level", None)
    limit = request.args.get("limit", 100, type=int)
    logs = get_logs(limit=limit, level=level)
    return jsonify(logs)


@dashboard_bp.route("/api/errors")
def api_errors():
    """
    Return recent error entries as JSON.

    Query parameters:
        limit — max rows to return (default 50). Optional.
    """
    limit = request.args.get("limit", 50, type=int)
    errors = get_errors(limit=limit)
    return jsonify(errors)


@dashboard_bp.route("/api/stats")
def api_stats():
    """
    Return aggregate statistics as JSON.

    Response format:
    {
        "total_logs": 1234,
        "total_errors": 56,
        "info": 600,
        "warning": 300,
        "error": 134,
        "debug": 200
    }
    """
    stats = get_stats()
    return jsonify(stats)


@dashboard_bp.route("/api/health")
def api_health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok"})
