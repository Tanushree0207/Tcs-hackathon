"""
PII Anonymization Module
========================
This module handles scrubbing Personally Identifiable Information (PII)
such as emails, IP addresses, phone numbers, and credentials from user reports
before sending them to the external AI service.

NOTE FOR PHASE 1:
This is a modular foundation stub. In Phase 2, Backend Developer B will
implement regex/tokenization filters to sanitize sensitive user data.
"""


def anonymize_text(text: str) -> str:
    """
    Sanitize text to strip or redact PII.

    Parameters:
        text (str): Raw input text from the bug report.

    Returns:
        str: Scrubbed text safe for AI processing.
    """
    if not text:
        return ""

    # Stub for Phase 1: returns text as-is.
    # Phase 2 will implement pattern-based redaction:
    # e.g., re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', text)
    return text.strip()
