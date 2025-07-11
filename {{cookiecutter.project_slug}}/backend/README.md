# {{cookiecutter.project_name}} Backend

This is the backend for the {{cookiecutter.project_name}} application, built with FastAPI, SQLModel, and Alembic. It provides a robust and scalable API for user management, authentication (including Google OAuth), and client management.

## 🚀 Features

*   **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **SQLModel**: A library for interacting with SQL databases from Python code, with Python objects. It's designed to be easy to use and to provide a great developer experience.
*   **Alembic**: Database migrations tool for SQLAlchemy (used by SQLModel).
*   **User Management**: CRUD operations for users, including password hashing and reset functionalities.
*   **Authentication**: JWT-based authentication, including Google OAuth integration.
*   **Client Management**: API for managing application clients.
*   **Layered Architecture**: Clear separation of concerns with API, Service, and Repository (CRUD) layers.
*   **Comprehensive Testing**: Includes unit and integration tests with Pytest.

## 🛠️ Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone {{cookiecutter.repository_url}}
    cd {{cookiecutter.project_slug}}/backend
    ```

2.  **Install `uv` (if you don't have it):**
    `uv` is a fast Python package installer and resolver.
    ```bash
    pip install uv
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r app/requirements.txt
    ```

4.  **Database Configuration:**
    Ensure your PostgreSQL database is running and accessible. Update the database connection string in `app/core/config.py` (or your environment variables) if necessary.

5.  **Run Database Migrations:**
    ```bash
    alembic upgrade head
    ```

## ▶️ Running the Application

To run the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API documentation will be available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## ✅ Running Tests

To run the tests and check code coverage:

```bash
uv run pytest --cov
```

## ⚠️ Important Notes

*   **`alembic/` and `.python-version`**: These directories/files are currently excluded from Git tracking as per local development preferences. For team collaboration, it's generally recommended to include them in version control.
*   **`datetime.utcnow()` Deprecation**: The project currently uses `datetime.utcnow()` which is deprecated. It will be updated to `datetime.now(datetime.UTC)` in future iterations.
