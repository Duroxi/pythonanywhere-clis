import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.tasks_cmd import app
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

runner = CliRunner()


def test_tasks_list():
    """tasks list shows all tasks."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = [
            {"id": 1, "command": "echo hello", "interval": "daily", "enabled": True},
            {"id": 2, "command": "echo world", "interval": "hourly", "enabled": False},
        ]
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "ID: 1" in result.output
    assert "echo hello" in result.output
    assert "daily" in result.output
    assert "enabled" in result.output


def test_tasks_list_empty():
    """tasks list shows message when no tasks."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = []
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No scheduled tasks found" in result.output


def test_tasks_create():
    """tasks create creates a new task."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.create.return_value = {"id": 3, "command": "echo new"}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["create", "echo hello"])

    assert result.exit_code == 0
    assert "Task created" in result.output
    mock_client.create.assert_called_once()


def test_tasks_delete_with_force():
    """tasks delete deletes task with --force flag."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "1", "-f"])

    assert result.exit_code == 0
    assert "Task 1 deleted" in result.output
    mock_client.delete.assert_called_once_with("testuser", 1)


def test_tasks_delete_cancelled():
    """tasks delete cancels when user says no."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "1"], input="n\n")

    assert "Cancelled" in result.output
    mock_client.delete.assert_not_called()


def test_tasks_enable():
    """tasks enable enables a task."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["enable", "1"])

    assert result.exit_code == 0
    assert "Task 1 enabled" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, enabled=True)


def test_tasks_disable():
    """tasks disable disables a task."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["disable", "1"])

    assert result.exit_code == 0
    assert "Task 1 disabled" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, enabled=False)


# --- Error handling tests (parametrized) ---

@pytest.mark.parametrize("command,args,mock_method,error_class,expected_msg", [
    ("list", [], "list", NetworkError, "Network error"),
    ("list", [], "list", AuthError, "Auth error"),
    ("list", [], "list", APIError, "API error"),
    ("create", ["echo hello"], "create", NetworkError, "Network error"),
    ("create", ["echo hello"], "create", AuthError, "Auth error"),
    ("create", ["echo hello"], "create", APIError, "API error"),
    ("delete", ["1", "-f"], "delete", NetworkError, "Network error"),
    ("delete", ["1", "-f"], "delete", AuthError, "Auth error"),
    ("delete", ["1", "-f"], "delete", NotFoundError, "Task not found"),
    ("delete", ["1", "-f"], "delete", APIError, "API error"),
    ("enable", ["1"], "update", NetworkError, "Network error"),
    ("enable", ["1"], "update", AuthError, "Auth error"),
    ("enable", ["1"], "update", NotFoundError, "Task not found"),
    ("enable", ["1"], "update", APIError, "API error"),
    ("disable", ["1"], "update", NetworkError, "Network error"),
    ("disable", ["1"], "update", AuthError, "Auth error"),
    ("disable", ["1"], "update", NotFoundError, "Task not found"),
    ("disable", ["1"], "update", APIError, "API error"),
])
def test_tasks_error_handling(command, args, mock_method, error_class, expected_msg):
    """tasks commands show appropriate error messages."""
    with patch("pa_cli.cli.tasks_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        getattr(mock_client, mock_method).side_effect = error_class("Test error")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, [command] + args)

    assert result.exit_code == 1
    assert expected_msg in result.output
