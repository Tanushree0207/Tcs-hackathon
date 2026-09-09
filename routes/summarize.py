"""
Summarize Route Module
======================
Handles the /api/summarize endpoint for bug report submission and AI triage.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.bug_report import BugReportRequest
from schemas.ai_output import AIAnalysisOutput
from services.ai_service import generate_summary
from database.db import insert_bug_report
from utils.anonymizer import anonymize_text
from utils.security import format_error_response, sanitize_text

summarize_bp = Blueprint("summarize", __name__)


@summarize_bp.route("/api/summarize", methods=["POST"])
def summarize():
    """
    POST /api/summarize
    Submit a bug report for automated triage and summarization.

    Steps:
        1. Validate payload using Pydantic BugReportRequest.
        2. Sanitize input and anonymize the description.
        3. Call the Groq AI service.
        4. Persist the report and AI triage outcome into SQLite.
        5. Return the structured triage response.
    """

    # 1. Check that the request contains JSON
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

    # 2. Pydantic validation
    try:
        validated_request = BugReportRequest(**raw_json)

    except ValidationError as err:
        errors = []

        for error in err.errors():
            loc = " -> ".join(str(p) for p in error["loc"])

            errors.append({
                "field": loc,
                "issue": error["msg"]
            })

        return format_error_response(
            message="Validation error in submitted bug report.",
            error_type="Validation Error",
            status_code=400,
            details=errors,
        )

    # 3. Input sanitization and PII anonymization
    clean_title = sanitize_text(validated_request.title)

    clean_description = sanitize_text(
        validated_request.description
    )

    anonymized_desc = anonymize_text(
        clean_description
    )

    # 4. AI Service - Groq
    try:
        ai_result = generate_summary(
            title=clean_title,
            description=anonymized_desc,
            severity=validated_request.severity,
        )

    except Exception:
        # Do not expose API errors or stack traces to the client
        return format_error_response(
            message="AI summarization service failed.",
            error_type="AI Service Error",
            status_code=502,
        )

    # 5. SQLite persistence
    db_payload = {
        "title": clean_title,
        "description": clean_description,
        "original_severity": validated_request.severity,
        "summary": ai_result["summary"],
        "severity": ai_result["severity"],
        "priority": ai_result["priority"],
        "impact": ai_result["impact"],
        "steps_to_reproduce": ai_result["steps_to_reproduce"],
        "affected_component": ai_result["affected_component"],
        "entities": ai_result["entities"],
        "confidence": ai_result["confidence"],
        "processing_status": ai_result.get(
            "processing_status",
            "completed"
        ),
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

    # 6. Build response
    response_data = {
        "id": report_id,
        "summary": ai_result["summary"],
        "severity": ai_result["severity"],
        "priority": ai_result["priority"],
        "impact": ai_result["impact"],
        "steps_to_reproduce": ai_result["steps_to_reproduce"],
        "affected_component": ai_result["affected_component"],
        "entities": ai_result["entities"],
        "confidence": ai_result["confidence"],
    }

    # 7. Validate AI output against Pydantic schema
    validated_output = AIAnalysisOutput(
        **response_data
    )

    return jsonify(
        validated_output.model_dump(
            exclude_none=True,
            exclude={"processing_status"}
        )
    ), 201