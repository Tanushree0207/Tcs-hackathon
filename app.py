"""
Main Application Entrypoint
===========================
AI-Powered Automated Bug Report Summarizer and Triage Dashboard.
Phase 1: Modular Backend Foundation.
"""

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from config import Config
from database.db import init_db
from routes.summarize import summarize_bp
from routes.reports import reports_bp
from routes.dashboard import dashboard_bp
from utils.security import apply_security_headers, format_error_response


def create_app(config_class=Config) -> Flask:
    """Application factory for the Flask backend."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite database tables
    with app.app_context():
        init_db(app.config.get("DATABASE_PATH"))

    # Register Route Blueprints
    app.register_blueprint(summarize_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)

    # --------------------------------------------------------------------------
    # Health Endpoint
    # --------------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        GET /api/health
        Basic liveness/health probe.
        """
        return jsonify({"status": "ok"}), 200

    # --------------------------------------------------------------------------
    # Security Middleware & Restricted CORS
    # --------------------------------------------------------------------------
    ALLOWED_ORIGINS = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }

    @app.after_request
    def add_security_headers(response):
        """Apply defensive HTTP security headers and restricted CORS."""
        response = apply_security_headers(response)

        # Restricted CORS: only allow approved local development origins, never '*'
        origin = request.headers.get("Origin")
        if origin and origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response

    # --------------------------------------------------------------------------
    # Global Safe JSON Error Handlers (Prevents Python Stack Trace Exposure)
    # --------------------------------------------------------------------------
    @app.errorhandler(400)
    def handle_bad_request(e):
        return format_error_response(
            message=getattr(e, "description", "Bad Request"),
            error_type="Bad Request",
            status_code=400,
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        return format_error_response(
            message=getattr(e, "description", "Requested resource was not found."),
            error_type="Not Found",
            status_code=404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return format_error_response(
            message=f"HTTP method {request.method} is not allowed on this endpoint.",
            error_type="Method Not Allowed",
            status_code=405,
        )

    @app.errorhandler(413)
    def handle_payload_too_large(e):
        return format_error_response(
            message="Request payload exceeds the maximum allowed size (1 MB).",
            error_type="Payload Too Large",
            status_code=413,
        )

    @app.errorhandler(500)
    def handle_internal_server_error(e):
        return format_error_response(
            message="An internal server error occurred. Please try again later.",
            error_type="Internal Server Error",
            status_code=500,
        )

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        # Translate generic HTTP exceptions to safe JSON
        if isinstance(e, HTTPException):
            return format_error_response(
                message=e.description,
                error_type=e.name,
                status_code=e.code,
            )
        # Never leak raw stack trace for unhandled runtime exceptions
        return format_error_response(
            message="An unexpected error occurred processing your request.",
            error_type="Internal Server Error",
            status_code=500,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )
