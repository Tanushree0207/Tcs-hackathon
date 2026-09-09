"""
AI Service Module
=================
TEMPORARY MOCK FOR PHASE 1:
This module provides a deterministic mock response adhering to the AI triage contract.
DO NOT call external AI APIs in this phase.

In Phase 2, Backend Developer B will implement the real Grok (xAI) API integration
with structured JSON generation and prompt templating.
"""

from typing import Any, Dict


def generate_mock_summary(title: str, description: str, severity: str) -> Dict[str, Any]:
    """
    Generate a mock AI triage analysis matching the exact Phase 1 specification.

    Parameters:
        title (str): Title of the reported bug.
        description (str): Detailed text description of the bug.
        severity (str): Original reported severity.

    Returns:
        dict: Triage output containing summary, priority, impact, steps, etc.
    """
    # --------------------------------------------------------------------------
    # NOTE: TEMPORARY MOCK RESPONSE (PHASE 1)
    # This matches the sample contract provided in the specification.
    # Replace with Grok client in Phase 2.
    # --------------------------------------------------------------------------
    return {
        "summary": "Login button does not respond after valid credentials are entered.",
        "severity": severity,
        "priority": "P1" if severity in ("Critical", "High") else "P2",
        "impact": "Users are unable to log in.",
        "steps_to_reproduce": [
            "Open the login page",
            "Enter valid credentials",
            "Click Login",
        ],
        "affected_component": "Authentication",
        "entities": [
            "Login button",
            "Login page",
        ],
        "confidence": 0.95,
        "processing_status": "completed",
    }
