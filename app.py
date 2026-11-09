from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

DATABASE = Path(__file__).parent / "data" / "tasks.db"

VALID_STATUSES = ["Pending", "In Progress", "Completed"]


# ---------------- DATABASE ----------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def task_to_dict(task):
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"]
    }


# ---------------- HEALTH CHECK ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to Task Management API",
        "version": "1.0",
        "endpoints": {
            "GET /api/tasks": "Get all tasks",
            "POST /api/tasks": "Create a task",
            "GET /api/tasks/<id>": "Get a task",
            "PUT /api/tasks/<id>": "Update a task",
            "PATCH /api/tasks/<id>/status": "Update task status",
            "DELETE /api/tasks/<id>": "Delete a task"
        }
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# ---------------- GET ALL TASKS ----------------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")

    with get_db_connection() as connection:
        if status:
            if status not in VALID_STATUSES:
                return jsonify({
                    "error": "Invalid status",
                    "valid_statuses": VALID_STATUSES
                }), 400

            tasks = connection.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY id DESC",
                (status,)
            ).fetchall()
        else:
            tasks = connection.execute(
                "SELECT * FROM tasks ORDER BY id DESC"
            ).fetchall()

    return jsonify({
        "count": len(tasks),
        "tasks": [task_to_dict(task) for task in tasks]
    }), 200


# ---------------- CREATE TASK ----------------

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "Pending")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Task title is required"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid status",
            "valid_statuses": VALID_STATUSES
        }), 400

    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, status)
            VALUES (?, ?, ?)
            """,
            (title.strip(), description.strip(), status)
        )

        task_id = cursor.lastrowid

        task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

    return jsonify({
        "message": "Task created successfully",
        "task": task_to_dict(task)
    }), 201


# ---------------- GET TASK BY ID ----------------

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with get_db_connection() as connection:
        task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task_to_dict(task)), 200


# ---------------- UPDATE TASK ----------------

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "Pending")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Task title is required"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid status",
            "valid_statuses": VALID_STATUSES
        }), 400

    with get_db_connection() as connection:
        existing_task = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing_task is None:
            return jsonify({"error": "Task not found"}), 404

        connection.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?
            WHERE id = ?
            """,
            (title.strip(), description.strip(), status, task_id)
        )

        updated_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

    return jsonify({
        "message": "Task updated successfully",
        "task": task_to_dict(updated_task)
    }), 200


# ---------------- UPDATE TASK STATUS ----------------

@app.route("/api/tasks/<int:task_id>/status", methods=["PATCH"])
def update_status(task_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid status",
            "valid_statuses": VALID_STATUSES
        }), 400

    with get_db_connection() as connection:
        existing_task = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing_task is None:
            return jsonify({"error": "Task not found"}), 404

        connection.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )

        updated_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

    return jsonify({
        "message": "Task status updated successfully",
        "task": task_to_dict(updated_task)
    }), 200


# ---------------- DELETE TASK ----------------

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_db_connection() as connection:
        existing_task = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing_task is None:
            return jsonify({"error": "Task not found"}), 404

        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

    return jsonify({
        "message": "Task deleted successfully"
    }), 200


# ---------------- ERROR HANDLERS ----------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "HTTP method not allowed"}), 405


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, port=5000)