"""
Dashboard Route Module
======================
Provides aggregate triage metrics for the frontend dashboard.
"""

from flask import Blueprint, jsonify
from database.db import get_dashboard_stats
from utils.security import format_error_response

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/stats", methods=["GET"])
def get_stats():
    """
    GET /api/dashboard/stats
    Returns current aggregate triage statistics queried directly from SQLite.
    Output format:
    {
        "total_reports": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "successful": 0,
        "failed": 0
    }
    """
    try:
        stats = get_dashboard_stats()
        return jsonify(stats), 200
    except Exception:
        return format_error_response(
            message="Failed to retrieve dashboard statistics.",
            error_type="Internal Server Error",
            status_code=500,
        )
