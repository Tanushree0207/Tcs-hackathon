"""
Prompts Module
==============
This module houses system and user prompt templates for bug report summarization and triage.

NOTE FOR PHASE 1:
This is a foundational placeholder. Backend Developer B will calibrate and refine
these prompt templates for the Grok (xAI) API in Phase 2.
"""

SUMMARIZATION_SYSTEM_PROMPT = """You are an expert QA and Software Engineering triage assistant.
Your task is to analyze user-submitted bug reports and output structured JSON adhering to the target schema.
Extract:
1. summary: A clear, concise one-sentence description of the issue.
2. severity: The technical severity (Critical, High, Medium, Low).
3. priority: Triage priority (P1, P2, P3, P4).
4. impact: The operational or user impact.
5. steps_to_reproduce: Ordered array of reproduction steps.
6. affected_component: The probable software module or subsystem affected.
7. entities: Key UI components, API endpoints, or services mentioned.
8. confidence: Float between 0.0 and 1.0 indicating triage confidence.
"""

SUMMARIZATION_USER_PROMPT_TEMPLATE = """Analyze the following bug report:

Title: {title}
Reported Severity: {severity}
Description:
{description}

Output your analysis strictly in valid JSON matching the requested fields.
"""
