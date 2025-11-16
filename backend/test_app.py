import types
import sys
import sqlite3
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def app_test_env(monkeypatch):
    """
    Set up a controlled environment for importing the app module:
    - Mock backend.cal.greet_user
    - Mock sqlite3.connect to return a mocked connection and cursor
    - Ensure a fresh import of app for each test
    """
    # Mock backend.cal.greet_user
    backend_mod = types.ModuleType("backend")
    cal_mod = types.ModuleType("backend.cal")
    greet_mock = MagicMock(name="greet_user")
    cal_mod.greet_user = greet_mock
    monkeypatch.setitem(sys.modules, "backend", backend_mod)
    monkeypatch.setitem(sys.modules, "backend.cal", cal_mod)

    # Mock sqlite connection and cursor
    cursor = MagicMock(name="cursor")
    conn = MagicMock(name="conn")
    conn.cursor.return_value = cursor

    def execute_side_effect(query, params=None):
        return cursor

    cursor.execute.side_effect = execute_side_effect
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.rowcount = 0

    # Patch sqlite3.connect
    monkeypatch.setattr(sqlite3, "connect", lambda db: conn)

    # Force fresh import of app
    if "app" in sys.modules:
        del sys.modules["app"]

    return {
        "greet_user": greet_mock,
        "cursor": cursor,
        "conn": conn,
    }


@pytest.mark.parametrize(
    "user,pw,rows",
    [
        ("alice", "secret", [("alice", "secret")]),
        ("bob", "pass", []),
    ],
)
def test_login_happy_path_calls_greet_and_executes_query(app_test_env, user, pw, rows):
    """Test login returns rows and calls greet_user with expected arguments."""
    from app import login

    app_test_env["greet_user"].reset_mock()
    app_test_env["cursor"].reset_mock()
    app_test_env["cursor"].fetchall.return_value = rows

    result = login(user, pw)

    expected_query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{pw}'"
    app_test_env["cursor"].execute.assert_called_once_with(expected_query)
    app_test_env["greet_user"].assert_called_once_with(user, "15")
    assert result == rows


def test_login_sql_injection_query_is_built_unsafely(app_test_env):
    """Test login builds a raw SQL string with unescaped user input (unsafe)."""
    from app import login

    user = "admin' --"
    pw = "irrelevant"
    rows = [("admin", "ignored")]
    app_test_env["cursor"].fetchall.return_value = rows

    result = login(user, pw)

    expected_query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{pw}'"
    app_test_env["cursor"].execute.assert_called_once_with(expected_query)
    app_test_env["greet_user"].assert_called_once_with(user, "15")
    assert result == rows


def test_register_success(app_test_env):
    """Test register inserts a new user and commits on success."""
    from app import register

    user, pw = "new_user", "new_pass"
    app_test_env["cursor"].execute.side_effect = lambda q, params=None: app_test_env["cursor"]

    result = register(user, pw)

    app_test_env["cursor"].execute.assert_called_once_with(
        "INSERT INTO users (username, password) VALUES (?, ?)", (user, pw)
    )
    app_test_env["conn"].commit.assert_called_once()
    assert result == "User registered successfully"


def test_register_duplicate_username(app_test_env):
    """Test register returns error message when username already exists."""
    from app import register

    user, pw = "existing_user", "any"
    app_test_env["cursor"].execute.side_effect = sqlite3.IntegrityError

    result = register(user, pw)

    app_test_env["conn"].commit.assert_not_called()
    assert result == "Username already exists"


def test_update_password_success(app_test_env):
    """Test update_password updates and commits when old password matches."""
    from app import update_password

    user, old_pw, new_pw = "alice", "old", "new"
    app_test_env["cursor"].fetchone.return_value = ("alice", "old")

    result = update_password(user, old_pw, new_pw)

    # First select, then update
    app_test_env["cursor"].execute.assert_any_call(
        "SELECT * FROM users WHERE username = ? AND password = ?", (user, old_pw)
    )
    app_test_env["cursor"].execute.assert_any_call(
        "UPDATE users SET password = ? WHERE username = ?", (new_pw, user)
    )
    app_test_env["conn"].commit.assert_called_once()
    assert result == "Password updated successfully"


def test_update_password_incorrect_old(app_test_env):
    """Test update_password returns error when old password does not match."""
    from app import update_password

    user, old_pw, new_pw = "bob", "wrong_old", "newpw"
    app_test_env["cursor"].fetchone.return_value = None

    result = update_password(user, old_pw, new_pw)

    app_test_env["cursor"].execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = ? AND password = ?", (user, old_pw)
    )
    app_test_env["conn"].commit.assert_not_called()
    assert result == "Incorrect old password"


def test_delete_user_success(app_test_env):
    """Test delete_user deletes and commits when a row is affected."""
    from app import delete_user

    user, pw = "charlie", "pw"
    app_test_env["cursor"].rowcount = 1

    result = delete_user(user, pw)

    app_test_env["cursor"].execute.assert_called_once_with(
        "DELETE FROM users WHERE username = ? AND password = ?", (user, pw)
    )
    app_test_env["conn"].commit.assert_called_once()
    assert result == "User deleted successfully"


def test_delete_user_not_found(app_test_env):
    """Test delete_user returns not found message when no row is deleted."""
    from app import delete_user

    user, pw = "delta", "pw"
    app_test_env["cursor"].rowcount = 0

    result = delete_user(user, pw)

    app_test_env["cursor"].execute.assert_called_once_with(
        "DELETE FROM users WHERE username = ? AND password = ?", (user, pw)
    )
    app_test_env["conn"].commit.assert_not_called()
    assert result == "User not found or incorrect password"