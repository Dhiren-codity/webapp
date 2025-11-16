import sys
import types
import pytest
import sqlite3
from unittest.mock import Mock


@pytest.fixture
def setup_app(monkeypatch):
    """Set up a mocked environment for importing the app module."""
    # Create a mocked backend.cal.greet_user before importing app
    backend_mod = types.ModuleType("backend")
    cal_mod = types.ModuleType("backend.cal")
    greet_mock = Mock(name="greet_user")
    cal_mod.greet_user = greet_mock
    sys.modules["backend"] = backend_mod
    sys.modules["backend.cal"] = cal_mod

    # Mock sqlite3 connection and cursor
    conn_mock = Mock(name="conn")
    cursor_mock = Mock(name="cursor")
    conn_mock.cursor.return_value = cursor_mock
    cursor_mock.rowcount = 0

    monkeypatch.setattr(sqlite3, "connect", Mock(return_value=conn_mock))

    # Ensure app is re-imported fresh per test
    sys.modules.pop("app", None)

    return {"greet": greet_mock, "conn": conn_mock, "cursor": cursor_mock}


@pytest.mark.parametrize(
    "user,pw,expected_rows",
    [
        ("alice", "secret", [("row1",)]),
        ("bob' OR '1'='1", "x' OR '1'='1", [("all", "rows")]),
    ],
)
def test_login_executes_query_and_calls_greet(setup_app, user, pw, expected_rows):
    """Test that login builds the correct SQL query, calls greet_user, and returns fetched rows."""
    from app import login

    cursor = setup_app["cursor"]
    greet = setup_app["greet"]

    cursor.execute.return_value.fetchall.return_value = expected_rows

    result = login(user, pw)
    expected_query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{pw}'"

    assert result == expected_rows
    cursor.execute.assert_called_once_with(expected_query)
    greet.assert_called_once_with(user, "15")


def test_register_success_commits_and_returns_message(setup_app):
    """Test register successfully inserts a user and commits the transaction."""
    from app import register

    conn = setup_app["conn"]
    cursor = setup_app["cursor"]

    # No exception on execute -> success
    cursor.execute.side_effect = None

    msg = register("new_user", "new_password")
    assert msg == "User registered successfully"

    cursor.execute.assert_called_once_with(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("new_user", "new_password"),
    )
    conn.commit.assert_called_once()


def test_register_duplicate_username_returns_message_no_commit(setup_app):
    """Test register handles sqlite3.IntegrityError when username already exists."""
    from app import register

    conn = setup_app["conn"]
    cursor = setup_app["cursor"]

    cursor.execute.side_effect = sqlite3.IntegrityError("duplicate")

    msg = register("existing_user", "pw")
    assert msg == "Username already exists"

    # Ensure commit was not called due to error
    conn.commit.assert_not_called()


def test_update_password_success_updates_and_commits(setup_app):
    """Test update_password updates the password when old credentials are valid."""
    from app import update_password

    conn = setup_app["conn"]
    cursor = setup_app["cursor"]

    # Simulate user found
    cursor.fetchone.return_value = ("user_row",)

    msg = update_password("user1", "oldpw", "newpw")
    assert msg == "Password updated successfully"

    # Expect SELECT then UPDATE
    assert cursor.execute.call_count == 2
    select_call = cursor.execute.call_args_list[0]
    update_call = cursor.execute.call_args_list[1]

    assert select_call.args[0] == "SELECT * FROM users WHERE username = ? AND password = ?"
    assert select_call.args[1] == ("user1", "oldpw")

    assert update_call.args[0] == "UPDATE users SET password = ? WHERE username = ?"
    assert update_call.args[1] == ("newpw", "user1")

    conn.commit.assert_called_once()


def test_update_password_incorrect_old_password_returns_message(setup_app):
    """Test update_password returns error message when old password is incorrect."""
    from app import update_password

    conn = setup_app["conn"]
    cursor = setup_app["cursor"]

    # Simulate user not found / incorrect old password
    cursor.fetchone.return_value = None

    msg = update_password("user1", "wrong_old", "newpw")
    assert msg == "Incorrect old password"

    conn.commit.assert_not_called()


@pytest.mark.parametrize(
    "rowcount,expected_msg,committed",
    [
        (1, "User deleted successfully", True),
        (0, "User not found or incorrect password", False),
    ],
)
def test_delete_user_handles_rowcount_and_commit(setup_app, rowcount, expected_msg, committed):
    """Test delete_user behavior for both success (rowcount > 0) and failure cases."""
    from app import delete_user

    conn = setup_app["conn"]
    cursor = setup_app["cursor"]

    # Set the rowcount result to simulate delete outcomes
    cursor.rowcount = rowcount

    msg = delete_user("userX", "pwX")
    assert msg == expected_msg

    cursor.execute.assert_called_once_with(
        "DELETE FROM users WHERE username = ? AND password = ?",
        ("userX", "pwX"),
    )

    if committed:
        conn.commit.assert_called_once()
    else:
        conn.commit.assert_not_called()