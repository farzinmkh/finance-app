# Personal Finance Manager

A personal finance management application built with Python, FastAPI, and SQLAlchemy.
Built as a real-world learning project following Clean Architecture principles.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Database ORM | SQLAlchemy 2.x |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL (future) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Configuration | pydantic-settings |
| Testing | pytest + httpx |
| Server | uvicorn |

---

## Project Setup

### Prerequisites

- Python 3.12+
- Git

### 1. Clone the repository

```bash
git clone <repository-url>
cd finance_app
```

### 2. Create a virtual environment

A virtual environment isolates this project's dependencies from your system Python.
You only need to create it once.

```bash
python3 -m venv .venv
```

Activate it (you must do this every time you open a new terminal):

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

You will see `(.venv)` at the start of your terminal prompt when it is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and review the values. For local development, the defaults work.
**Never commit the `.env` file** — it is listed in `.gitignore`.

For production, generate a real secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialise the database

When database models are added, Alembic manages schema migrations.

```bash
# Apply all migrations to bring the database up to date
alembic upgrade head
```

> **Note:** In the current foundation phase, there are no models yet.
> Alembic migrations will be added as each feature is implemented.

---

## Running the Application

From the project root (with your virtual environment activated):

```bash
uvicorn main:app --reload
```

`--reload` automatically restarts the server when you save a file.
Use this during development only.

The application will be available at:

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/health` | Health check endpoint |
| `http://127.0.0.1:8000/docs` | Swagger UI — interactive API docs |
| `http://127.0.0.1:8000/redoc` | ReDoc — alternative API docs |

---

## Running Tests

From the project root (with your virtual environment activated):

```bash
# Run all tests
pytest

# Run with verbose output (shows each test name)
pytest -v

# Run only a specific test file
pytest tests/api/test_health.py

# Run only a specific test function
pytest tests/api/test_health.py::test_health_check_returns_http_200

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only API tests
pytest tests/api/
```

---

## Project Structure

```
finance_app/
│
├── domain/                     ← Business logic. No external dependencies.
│   ├── entities/               ← Core business objects (User, Account, etc.)
│   ├── repositories/           ← Abstract interfaces (contracts) for data access
│   └── exceptions.py           ← Domain-level exceptions (business rule violations)
│
├── application/                ← Use cases. Orchestrates domain objects.
│   └── use_cases/              ← One file per user-facing action
│       ├── auth/
│       ├── accounts/
│       ├── categories/
│       ├── transactions/
│       └── transfers/
│
├── infrastructure/             ← Concrete implementations of external concerns.
│   ├── database/
│   │   ├── models.py           ← SQLAlchemy ORM table definitions
│   │   ├── session.py          ← Database engine and session management
│   │   └── repositories/      ← SQLAlchemy implementations of domain interfaces
│   └── security/
│       ├── password.py         ← bcrypt password hashing (added with auth)
│       └── jwt.py              ← JWT token creation/validation (added with auth)
│
├── presentation/               ← HTTP boundary. Routes, schemas, error mapping.
│   ├── api/
│   │   ├── routers/            ← FastAPI route definitions (one file per domain area)
│   │   ├── schemas/            ← Pydantic request/response schemas
│   │   ├── dependencies.py     ← Shared FastAPI dependencies (get_current_user, etc.)
│   │   └── error_handlers.py   ← Maps domain exceptions to HTTP responses
│   └── frontend/
│       ├── static/             ← CSS and JavaScript files
│       └── templates/          ← HTML pages
│
├── tests/
│   ├── unit/                   ← Fast tests. No database. Uses fake repositories.
│   │   ├── domain/             ← Tests for entity business logic
│   │   └── use_cases/          ← Tests for use cases with in-memory fakes
│   ├── integration/            ← Tests against real in-memory SQLite database
│   └── api/                    ← End-to-end HTTP tests using TestClient
│
├── alembic/                    ← Database migration scripts
│   ├── versions/               ← Individual migration files (auto-generated)
│   └── env.py                  ← Alembic integration with our app config
│
├── config.py                   ← Application configuration (reads from .env)
├── main.py                     ← FastAPI application entry point
├── alembic.ini                 ← Alembic configuration
├── pytest.ini                  ← Test runner configuration
├── requirements.txt            ← Python dependencies
├── .env.example                ← Environment variable template (safe to commit)
└── .gitignore                  ← Files excluded from version control
```

---

## Architecture Overview

This project follows a pragmatic Clean Architecture:

```
Presentation  →  Application  →  Domain  ←  Infrastructure
```

**Dependency rule:** Each layer only imports from layers to its right.
The Domain layer imports nothing external.

| Layer | What it contains | What it MUST NOT contain |
|---|---|---|
| Domain | Entities, repository interfaces, exceptions | FastAPI, SQLAlchemy, HTTP concepts |
| Application | Use cases, input/output data structures | HTTP, SQL, framework imports |
| Infrastructure | SQLAlchemy models, bcrypt, JWT, SQL queries | Business logic |
| Presentation | FastAPI routes, Pydantic schemas, error mapping | Business logic, direct SQL |

---

## Financial Data Rules

This application handles real money. These rules are non-negotiable:

1. **No floats for money.** Always use `decimal.Decimal` in Python and `NUMERIC(19,4)` in the database.
2. **Transfers are atomic.** Both legs of a transfer succeed together or fail together.
3. **Balances are maintained.** Every transaction creation, update, and deletion updates `account.current_balance` in the same database transaction.
4. **Authorization on every query.** Every database read that returns user data includes `WHERE user_id = :current_user_id`.
5. **Foreign keys are enforced.** SQLite requires `PRAGMA foreign_keys=ON` per connection. This is configured in `infrastructure/database/session.py`.

---

## Implementation Status

| Feature | Status |
|---|---|
| Project foundation | ✅ Complete |
| User authentication | 🔜 Next |
| Account management | 🔜 Planned |
| Categories | 🔜 Planned |
| Transactions | 🔜 Planned |
| Transfers | 🔜 Planned |
| Budgets | 🔜 Planned |
| Dashboard | 🔜 Planned |
| Data export | 🔜 Planned |
