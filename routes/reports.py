"""
Reports Route Module
====================
Provides endpoints for retrieving persisted bug reports.
"""

from flask import Blueprint, jsonify
from database.db import get_all_bug_reports, get_bug_report_by_id
from utils.security import format_error_response

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports", methods=["GET"])
def list_reports():
    """
    GET /api/reports
    Retrieve all bug reports ordered by latest first.
    Returns an empty array if no reports have been filed yet.
    """
    try:
        reports = get_all_bug_reports()
        return jsonify({"reports": reports, "count": len(reports)}), 200
    except Exception:
        return format_error_response(
            message="Failed to retrieve bug reports.",
            error_type="Internal Server Error",
            status_code=500,
        )


@reports_bp.route("/api/reports/<int:report_id>", methods=["GET"])
def get_report(report_id: int):
    """
    GET /api/reports/<id>
    Retrieve a specific bug report by its integer ID.
    Returns 404 if the report does not exist.
    """
    try:
        report = get_bug_report_by_id(report_id)
        if report is None:
            return format_error_response(
                message=f"Bug report with ID {report_id} was not found.",
                error_type="Not Found",
                status_code=404,
            )
        return jsonify(report), 200
    except Exception:
        return format_error_response(
            message="Failed to retrieve bug report.",
            error_type="Internal Server Error",
            status_code=500,
        )
