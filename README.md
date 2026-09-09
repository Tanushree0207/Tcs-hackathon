# AI-Powered Automated Bug Report Summarizer and Triage Dashboard

**Phase 1: Modular Backend Foundation**

A modular, lightweight REST API backend built with Python, Flask, SQLite, and Pydantic. It provides the core API contracts, input validation, database persistence, and defensive security required for the automated bug report triage platform before connecting the live AI models and frontend interfaces.

---

## Architecture Overview

In full production, the platform operates as follows:

```
Frontend (React/Vite)
       ↓
Flask REST API
       ↓
Input Validation (Pydantic)
       ↓
PII Anonymization (Tokenization/Regex)
       ↓
AI Service (Grok / xAI API)
       ↓
Structured Output & Pydantic Validation
       ↓
SQLite Persistence
       ↓
JSON Response
       ↓
Frontend + Triage Dashboard
```

### Phase 1 Scope & Team Ownership

To enable four developers to work simultaneously without blocking or git merge conflicts:

- **Backend Developer A (Completed in Phase 1):**
  - `app.py` (Flask server, health check, security headers, error handlers)
  - `routes/` (`summarize.py`, `reports.py`, `dashboard.py`)
  - `config.py` (Environment & application configuration)
  - `utils/security.py` (Defensive HTTP headers, safe error masking)

- **Backend Developer B (Owns for Phase 2):**
  - `services/ai_service.py` (Connecting the Grok API)
  - `prompts/summarization_prompt.py` (System and user prompts)
  - `database/db.py` (Database optimizations & schema migrations)
  - `utils/anonymizer.py` (PII regex scrubbing)
  - `schemas/ai_output.py` (AI output schema refinement)

- **Frontend Developers:**
  - Consume stable REST API contracts (`/api/health`, `/api/summarize`, `/api/reports`, `/api/dashboard/stats`).

---

## Project Structure

```
Tcs-hackathon/
│
├── app.py                      # Flask application factory and entrypoint
├── config.py                   # Environment configuration loader
├── requirements.txt            # Minimal Phase 1 Python dependencies
├── .env.example                # Example environment variables template
├── .gitignore                  # Git ignore rules for venv, env, and db files
├── README.md                   # Complete documentation
│
├── routes/                     # API route blueprints
│   ├── __init__.py
│   ├── summarize.py            # POST /api/summarize
│   ├── reports.py              # GET /api/reports, GET /api/reports/<id>
│   └── dashboard.py            # GET /api/dashboard/stats
│
├── services/                   # Business logic and external service integrations
│   ├── __init__.py
│   └── ai_service.py           # Phase 1: Mock AI triage response
│
├── database/                   # SQLite database storage layer
│   ├── __init__.py
│   └── db.py                   # Parameterized SQLite queries & table creation
│
├── schemas/                    # Pydantic data validation schemas
│   ├── __init__.py
│   ├── bug_report.py           # Inbound BugReportRequest schema
│   └── ai_output.py            # Outbound AIAnalysisOutput schema
│
├── utils/                      # Modular utilities
│   ├── __init__.py
│   ├── anonymizer.py           # PII redaction stub for Phase 2
│   └── security.py             # Security headers, sanitization, safe error responses
│
└── prompts/                    # LLM Prompt templates
    ├── __init__.py
    └── summarization_prompt.py # Grok prompt templates for Phase 2
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- `pip` package manager

### 2. Create and Activate a Virtual Environment

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

On Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```
*(No real secret keys are required to run Phase 1).*

---

## Running the Flask Backend

Start the development server:
```bash
python app.py
```
By default, the server runs on `http://127.0.0.1:5001` (port 5001 is used to prevent collisions with macOS AirPlay Receiver on port 5000; this can be customized via `PORT` in `.env`).

---

## API Endpoints & Usage

### 1. Health Check
Checks if the backend is running and operational.

- **URL:** `GET /api/health`
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5001/api/health
  ```
- **Response:** `200 OK`
  ```json
  {
    "status": "ok"
  }
  ```

---

### 2. Submit Bug Report for Summarization
Submits a bug report, validates input, executes mock AI triage, stores the record in SQLite, and returns the analysis.

- **URL:** `POST /api/summarize`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "title": "Login button not working",
    "description": "When I enter valid credentials, clicking login does nothing.",
    "severity": "High"
  }
  ```
- **Example Request:**
  ```bash
  curl -X POST http://127.0.0.1:5001/api/summarize \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Login button not working",
      "description": "When I enter valid credentials, clicking login does nothing.",
      "severity": "High"
    }'
  ```
- **Response:** `201 Created`
  ```json
  {
    "id": 1,
    "summary": "Login button does not respond after valid credentials are entered.",
    "severity": "High",
    "priority": "P1",
    "impact": "Users are unable to log in.",
    "steps_to_reproduce": [
      "Open the login page",
      "Enter valid credentials",
      "Click Login"
    ],
    "affected_component": "Authentication",
    "entities": [
      "Login button",
      "Login page"
    ],
    "confidence": 0.95
  }
  ```

---

### 3. Dashboard Statistics
Returns aggregated metrics of all processed bug reports for the dashboard widgets.

- **URL:** `GET /api/dashboard/stats`
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5001/api/dashboard/stats
  ```
- **Response:** `200 OK`
  ```json
  {
    "total_reports": 1,
    "critical": 0,
    "high": 1,
    "medium": 0,
    "low": 0,
    "successful": 1,
    "failed": 0
  }
  ```

---

### 4. List All Bug Reports
Retrieves all filed bug reports ordered by latest first.

- **URL:** `GET /api/reports`
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5001/api/reports
  ```
- **Response:** `200 OK`
  ```json
  {
    "count": 1,
    "reports": [
      {
        "id": 1,
        "title": "Login button not working",
        "description": "When I enter valid credentials, clicking login does nothing.",
        "original_severity": "High",
        "generated_summary": "Login button does not respond after valid credentials are entered.",
        "generated_severity": "High",
        "priority": "P1",
        "impact": "Users are unable to log in.",
        "steps_to_reproduce": [
          "Open the login page",
          "Enter valid credentials",
          "Click Login"
        ],
        "affected_component": "Authentication",
        "entities": [
          "Login button",
          "Login page"
        ],
        "confidence": 0.95,
        "processing_status": "completed",
        "created_at": "2026-09-09 14:18:00"
      }
    ]
  }
  ```

---

### 5. Get Single Bug Report by ID
Retrieves details of a specific bug report.

- **URL:** `GET /api/reports/<id>`
- **Example Request:**
  ```bash
  curl -X GET http://127.0.0.1:5001/api/reports/1
  ```
- **Response (Found):** `200 OK`
  Returns the report object shown above.
- **Response (Not Found):** `404 Not Found`
  ```json
  {
    "error": "Not Found",
    "message": "Bug report with ID 999 was not found."
  }
  ```

---

## How the Mock AI Response Works

In `services/ai_service.py`, the `generate_mock_summary()` function returns a structured mock object conforming to `schemas/ai_output.py`. 

- In Phase 1, this enables frontend developers to immediately design and test UI components (summary cards, reproduction checklists, severity chips, and entity tags) against a realistic, stable payload without incurring API costs, latency, or dependency on external LLM services.
- In Phase 2, Backend Developer B will replace the internal body of `generate_mock_summary()` with an HTTP client call to Grok (xAI API), using the templates in `prompts/summarization_prompt.py`. The route handler (`routes/summarize.py`) and schema contract will remain identical.

---

## Security Considerations

1. **No Hardcoded Secrets:** Configuration and API keys are strictly read from `.env` via `python-dotenv`.
2. **Git Hygiene:** Sensitive files (`.env`, `*.db`, `venv/`, `__pycache__/`) are ignored via `.gitignore`. An `.env.example` template is provided.
3. **Pydantic Validation & Length Limits:** Inbound fields are type-checked and capped (title: 3-200 chars, description: 5-5000 chars, severity: strictly Critical, High, Medium, or Low).
4. **DoS Protection:** Max payload size is bounded to 1 MB (`MAX_CONTENT_LENGTH = 1048576`).
5. **No Traceback Leaks:** Custom error handlers catch 400, 404, 405, 413, and 500 errors, returning sanitized JSON payloads rather than default HTML stack traces.
6. **SQL Injection Protection:** All database queries in `database/db.py` use parameterized placeholders (`?`).
7. **HTTP Security Headers:** Defensive response headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Content-Security-Policy: default-src 'self'`) are automatically injected into every response.
8. **Restricted CORS:** Unrestricted wildcard origins (`*`) are disallowed; only authorized local frontend ports (`http://localhost:3000`, `http://localhost:5173`) are supported.

---

## Out of Scope (Intentionally NOT Implemented in Phase 1)

The following items are deferred to Phase 2:
- **Grok / xAI API Integration:** Live model calls, API key authorization, and rate limit retries.
- **Automated PII Masking:** Regex and entity recognition filters in `utils/anonymizer.py`.
- **Frontend User Interface:** React/Vite dashboard and submission forms.
- **User Authentication:** Login, user roles, and JWT sessions.
- **Heavyweight Infrastructure:** Docker containers, Kubernetes, Redis, Celery tasks, and message brokers.
