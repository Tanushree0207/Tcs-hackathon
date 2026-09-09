"""
Summarize Route Module
======================
Handles the /api/summarize endpoint for bug report submission and AI triage.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.bug_report import BugReportRequest
from schemas.ai_output import AIAnalysisOutput
from services.ai_service import generate_mock_summary
from database.db import insert_bug_report
from utils.anonymizer import anonymize_text
from utils.security import format_error_response, sanitize_text

summarize_bp = Blueprint("summarize", __name__)


@summarize_bp.route("/api/summarize", methods=["POST"])
def summarize():
    """
    POST /api/summarize
    Submit a bug report for automated triage and summarization.

    Phase 1:
        1. Validates payload using Pydantic BugReportRequest.
        2. Sanitizes input and passes through PII anonymizer stub.
        3. Calls mock AI service (services.ai_service.generate_mock_summary).
        4. Persists the report and triage outcome into SQLite.
        5. Returns the structured triage response.
    """
    if not request.is_json:
        return format_error_response(
            message="Request body must be valid JSON with Content-Type: application/json.",
            error_type="Unsupported Media Type",
            status_code=415,
        )

    raw_json = request.get_json(silent=True)
    if raw_json is None:
        return format_error_response(
            message="Malformed or empty JSON payload.",
            error_type="Bad Request",
            status_code=400,
        )

    # 1. Pydantic validation
    try:
        validated_request = BugReportRequest(**raw_json)
    except ValidationError as err:
        errors = []
        for error in err.errors():
            loc = " -> ".join(str(p) for p in error["loc"])
            errors.append({"field": loc, "issue": error["msg"]})
        return format_error_response(
            message="Validation error in submitted bug report.",
            error_type="Validation Error",
            status_code=400,
            details=errors,
        )

    # 2. Input sanitization & PII anonymization stub
    clean_title = sanitize_text(validated_request.title)
    clean_description = sanitize_text(validated_request.description)
    anonymized_desc = anonymize_text(clean_description)

    # 3. AI Service (Phase 1: Mock response)
    mock_ai_result = generate_mock_summary(
        title=clean_title,
        description=anonymized_desc,
        severity=validated_request.severity,
    )

    # 4. SQLite persistence
    db_payload = {
        "title": clean_title,
        "description": clean_description,
        "original_severity": validated_request.severity,
        "summary": mock_ai_result["summary"],
        "severity": mock_ai_result["severity"],
        "priority": mock_ai_result["priority"],
        "impact": mock_ai_result["impact"],
        "steps_to_reproduce": mock_ai_result["steps_to_reproduce"],
        "affected_component": mock_ai_result["affected_component"],
        "entities": mock_ai_result["entities"],
        "confidence": mock_ai_result["confidence"],
        "processing_status": mock_ai_result.get("processing_status", "completed"),
    }

    try:
        report_id = insert_bug_report(db_payload)
    except Exception:
        # Prevent stack trace leakage on database error
        return format_error_response(
            message="Failed to persist bug report to database.",
            error_type="Internal Server Error",
            status_code=500,
        )

    # 5. Build and validate response against AIAnalysisOutput schema
    response_data = {
        "id": report_id,
        "summary": mock_ai_result["summary"],
        "severity": mock_ai_result["severity"],
        "priority": mock_ai_result["priority"],
        "impact": mock_ai_result["impact"],
        "steps_to_reproduce": mock_ai_result["steps_to_reproduce"],
        "affected_component": mock_ai_result["affected_component"],
        "entities": mock_ai_result["entities"],
        "confidence": mock_ai_result["confidence"],
    }

    # Validate output schema consistency
    validated_output = AIAnalysisOutput(**response_data)

    return jsonify(validated_output.model_dump(exclude_none=True, exclude={"processing_status"})), 201
