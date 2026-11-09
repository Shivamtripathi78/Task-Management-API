# Task Management API

A RESTful API built using Python, Flask, and SQLite to manage tasks through HTTP requests.

## Features
- Create, read, update, and delete tasks.
- Update task status.
- Filter tasks by status.
- JSON-based API responses.
- SQLite database for persistent storage.
- HTTP status codes and input validation.

## Technologies
- Python
- Flask
- SQLite
- REST API
- JSON

## Installation

```bash
git clone https://github.com/Shivamtripathi78/Task-Management-API.git
cd Task-Management-API

python -m venv .venv
python -m pip install -r requirements.txt
python app.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | Get all tasks |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/<id>` | Get a task |
| PUT | `/api/tasks/<id>` | Update a task |
| PATCH | `/api/tasks/<id>/status` | Update task status |
| DELETE | `/api/tasks/<id>` | Delete a task |
| GET | `/api/health` | Check API health |
