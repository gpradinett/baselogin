# Test Coverage Report

This document summarizes the current test coverage of the project. The overall test suite has passed successfully, with a general coverage of **97%**.

## Coverage Details

| File                                  | Statements | Missed | Coverage |
| :------------------------------------ | :--------- | :----- | :------- |
| `app/__init__.py`                     | 0          | 0      | 100%     |
| `app/api/__init__.py`                 | 0          | 0      | 100%     |
| `app/api/deps.py`                     | 35         | 2      | 94%      |
| `app/api/main.py`                     | 6          | 0      | 100%     |
| `app/api/routes/__init__.py`          | 0          | 0      | 100%     |
| `app/api/routes/login.py`             | 19         | 0      | 100%     |
| `app/api/routes/password_reset.py`    | 40         | 1      | 98%      |
| `app/api/routes/users.py`             | 72         | 7      | 90%      |
| `app/core/__init__.py`                | 0          | 0      | 100%     |
| `app/core/config.py`                  | 49         | 2      | 96%      |
| `app/core/db.py`                      | 11         | 0      | 100%     |
| `app/core/security.py`                | 22         | 0      | 100%     |
| `app/crud.py`                         | 44         | 0      | 100%     |
| `app/main.py`                         | 19         | 0      | 100%     |
| `app/models.py`                       | 48         | 0      | 100%     |
| `app/utils.py`                        | 51         | 3      | 94%      |
| `tests/__init__.py`                   | 0          | 0      | 100%     |
| `tests/api/routes/__init__.py`        | 0          | 0      | 100%     |
| `tests/api/routes/test_login.py`      | 29         | 0      | 100%     |
| `tests/api/routes/test_password_reset.py` | 46         | 0      | 100%     |
| `tests/api/routes/test_users.py`      | 61         | 0      | 100%     |
| `tests/api/routes/test_users_coverage.py` | 24         | 0      | 100%     |
| `tests/api/test_deps.py`              | 69         | 2      | 97%      |
| `tests/conftest.py`                   | 45         | 1      | 98%      |
| `tests/factories.py`                  | 48         | 0      | 100%     |
| `tests/utils/__init__.py`             | 0          | 0      | 100%     |
| `tests/utils/test_email_service.py`   | 15         | 3      | 80%      |
| `tests/utils/test_user_utils.py`      | 28         | 0      | 100%     |
| `tests/utils/user.py`                 | 27         | 1      | 96%      |

## Explanation of Missed Lines (Potential Scenarios)

This section outlines potential reasons for the missed lines in files with less than 100% coverage. These are educated guesses and would require a detailed coverage report (e.g., `coverage html`) to confirm the exact lines.

*   **`app/api/deps.py` (2 missed lines):**
    *   Likely related to error handling paths in dependency injection functions (e.g., `get_current_active_user`, `get_current_active_superuser`) that are not triggered by current tests, such as specific `HTTPException` branches for inactive users or missing superuser privileges.
*   **`app/api/routes/password_reset.py` (1 missed line):**
    *   Could be an edge case in password reset logic, perhaps an `HTTPException` for an invalid token or a user not found scenario that isn't fully covered.
*   **`app/api/routes/users.py` (7 missed lines):**
    *   Given the recent changes, these might be related to:
        *   Specific error paths in `create_user` or `update_user` that are not yet hit (e.g., very specific email validation failures not covered by `UserCreate` model validation).
        *   Edge cases in `delete_user` or `delete_user_me` (e.g., attempting to delete a non-existent user with specific permissions).
        *   Uncovered branches in the `read_users` or `read_user_me` endpoints, although less likely for simple GET requests.
*   **`app/core/config.py` (2 missed lines):**
    *   Often, missed lines in config files are due to conditional logic (e.g., `if settings.DEBUG:` or `if not settings.TESTING:`) that is not executed in the test environment, or default values that are never explicitly overridden in tests.
*   **`app/utils.py` (3 missed lines):**
    *   This file contains utility functions. Missed lines could be in error handling for email sending (e.g., if `send_email` fails due to connection issues), or specific branches in other utility functions that are not fully exercised.
*   **`tests/api/test_deps.py` (2 missed lines):**
    *   These are tests for dependencies. Missed lines here might indicate that certain error conditions or specific user roles/states are not fully tested within the dependency functions themselves.
*   **`tests/conftest.py` (1 missed line):**
    *   `conftest.py` often contains fixtures. A missed line here could be an unused fixture, or a conditional branch within a fixture that is not met during test execution (e.g., a specific setup/teardown path).
*   **`tests/utils/test_email_service.py` (3 missed lines):**
    *   This is a test file for email services. Missed lines likely indicate that certain error conditions or specific scenarios for email sending (e.g., malformed email data, connection errors) are not fully tested.
*   **`tests/utils/user.py` (1 missed line):**
    *   This utility file for user-related operations might have a small edge case or an error path that is not triggered by the existing tests.

## Next Steps

To achieve 100% coverage and ensure maximum code quality, it is recommended to:
1.  Generate a detailed coverage report (e.g., `uv run pytest --cov --cov-report html`) to identify the exact lines that are not covered.
2.  Write additional tests to cover these specific lines and scenarios, focusing on edge cases, error handling, and different input combinations.
