"""
Security Utilities Module
=========================
Provides security helpers including HTTP response security headers,
safe JSON error formatters (masking tracebacks), and input sanitization.
"""

from typing import Any, Dict, Tuple
from flask import Response, jsonify


def apply_security_headers(response: Response) -> Response:
    """
    Append standard defensive HTTP security headers to all outbound responses.
    Prevents MIME-sniffing, clickjacking, and basic XSS attacks.
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def format_error_response(
    message: str,
    error_type: str = "Bad Request",
    status_code: int = 400,
    details: Any = None,
) -> Tuple[Response, int]:
    """
    Generate a consistent, safe JSON error response.
    Never exposes internal Python stack traces or sensitive system details.
    """
    payload: Dict[str, Any] = {
        "error": error_type,
        "message": message,
    }
    if details is not None:
        payload["details"] = details

    return jsonify(payload), status_code


def sanitize_text(text: str) -> str:
    """
    Basic input sanitation: strips null bytes and invisible control characters
    to prevent byte-level injection or terminal corruptions.
    """
    if not isinstance(text, str):
        return ""
    # Remove null bytes and unprintable ASCII control characters except standard whitespace
    cleaned = "".join(ch for ch in text if ch == "\n" or ch == "\r" or ch == "\t" or ord(ch) >= 32)
    return cleaned.strip()
