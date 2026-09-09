import json
import sqlite3
from typing import Any, Dict, List, Optional
from config import Config


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    target_path = db_path or Config.DATABASE_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the SQLite database schema with required tables."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bug_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        original_severity TEXT NOT NULL,
        generated_summary TEXT,
        generated_severity TEXT,
        priority TEXT,
        impact TEXT,
        steps_to_reproduce TEXT,
        affected_component TEXT,
        entities TEXT,
        confidence REAL,
        processing_status TEXT DEFAULT 'completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db_connection(db_path) as conn:
        conn.execute(create_table_sql)
        conn.commit()


def insert_bug_report(report_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    """
    Insert a bug report and its analysis into SQLite using parameterized queries.
    Returns the newly generated primary key id.
    """
    insert_sql = """
    INSERT INTO bug_reports (
        title,
        description,
        original_severity,
        generated_summary,
        generated_severity,
        priority,
        impact,
        steps_to_reproduce,
        affected_component,
        entities,
        confidence,
        processing_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    # Serialize list fields to JSON strings safely
    steps_to_reproduce = report_data.get("steps_to_reproduce")
    if isinstance(steps_to_reproduce, (list, tuple)):
        steps_json = json.dumps(steps_to_reproduce)
    else:
        steps_json = json.dumps([])

    entities = report_data.get("entities")
    if isinstance(entities, (list, tuple)):
        entities_json = json.dumps(entities)
    else:
        entities_json = json.dumps([])

    params = (
        report_data["title"],
        report_data["description"],
        report_data["original_severity"],
        report_data.get("generated_summary") or report_data.get("summary"),
        report_data.get("generated_severity") or report_data.get("severity"),
        report_data.get("priority"),
        report_data.get("impact"),
        steps_json,
        report_data.get("affected_component"),
        entities_json,
        report_data.get("confidence", 0.0),
        report_data.get("processing_status", "completed"),
    )

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(insert_sql, params)
        conn.commit()
        return cursor.lastrowid


def _parse_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Helper to convert a sqlite3.Row into a clean dictionary with parsed JSON fields."""
    data = dict(row)

    # Deserialize JSON strings to Python lists
    if "steps_to_reproduce" in data and isinstance(data["steps_to_reproduce"], str):
        try:
            data["steps_to_reproduce"] = json.loads(data["steps_to_reproduce"])
        except (json.JSONDecodeError, TypeError):
            data["steps_to_reproduce"] = []

    if "entities" in data and isinstance(data["entities"], str):
        try:
            data["entities"] = json.loads(data["entities"])
        except (json.JSONDecodeError, TypeError):
            data["entities"] = []

    return data


def get_bug_report_by_id(report_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single bug report by its ID using parameterized query."""
    query = "SELECT * FROM bug_reports WHERE id = ?;"
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (report_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return _parse_row(row)


def get_all_bug_reports(limit: int = 100, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all bug reports ordered by latest first using parameterized query."""
    query = "SELECT * FROM bug_reports ORDER BY id DESC LIMIT ?;"
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return [_parse_row(row) for row in rows]


def get_dashboard_stats(db_path: Optional[str] = None) -> Dict[str, int]:
    """
    Compute aggregate triage metrics from SQLite using parameterized queries.
    Matches the exact schema required for GET /api/dashboard/stats:
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
    stats = {
        "total_reports": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "successful": 0,
        "failed": 0,
    }

    queries = {
        "total_reports": "SELECT COUNT(*) FROM bug_reports;",
        "critical": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE LOWER(COALESCE(generated_severity, original_severity)) = 'critical';
        """,
        "high": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE LOWER(COALESCE(generated_severity, original_severity)) = 'high';
        """,
        "medium": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE LOWER(COALESCE(generated_severity, original_severity)) = 'medium';
        """,
        "low": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE LOWER(COALESCE(generated_severity, original_severity)) = 'low';
        """,
        "successful": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE processing_status = 'completed';
        """,
        "failed": """
            SELECT COUNT(*) FROM bug_reports 
            WHERE processing_status = 'failed';
        """,
    }

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for key, sql in queries.items():
            cursor.execute(sql)
            result = cursor.fetchone()
            stats[key] = result[0] if result else 0

    return stats
