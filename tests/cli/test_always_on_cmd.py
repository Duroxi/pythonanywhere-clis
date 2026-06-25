import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.always_on_cmd import app
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

runner = CliRunner()


def test_always_on_list():
    """always-on list shows all tasks."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = [
            {"id": 1, "command": "echo hello", "enabled": True},
            {"id": 2, "command": "echo world", "enabled": False},
        ]
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "ID: 1" in result.output
    assert "echo hello" in result.output
    assert "enabled" in result.output


def test_always_on_list_empty():
    """always-on list shows message when no tasks."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = []
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No always-on tasks found" in result.output


def test_always_on_create():
    """always-on create creates a new task."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.create.return_value = {"id": 3, "command": "echo new"}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["create", "echo hello"])

    assert result.exit_code == 0
    assert "Always-on task created" in result.output
    mock_client.create.assert_called_once()


def test_always_on_delete_with_force():
    """always-on delete deletes task with --force flag."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "1", "-f"])

    assert result.exit_code == 0
    assert "Always-on task 1 deleted" in result.output
    mock_client.delete.assert_called_once_with("testuser", 1)


def test_always_on_delete_cancelled():
    """always-on delete cancels when user says no."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "1"], input="n\n")

    assert "Cancelled" in result.output
    mock_client.delete.assert_not_called()


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
    ("update", ["1", "-c", "echo updated"], "update", NetworkError, "Network error"),
    ("update", ["1", "-c", "echo updated"], "update", AuthError, "Auth error"),
    ("update", ["1", "-c", "echo updated"], "update", NotFoundError, "Task not found"),
    ("update", ["1", "-c", "echo updated"], "update", APIError, "API error"),
    ("restart", ["1"], "restart", NetworkError, "Network error"),
    ("restart", ["1"], "restart", AuthError, "Auth error"),
    ("restart", ["1"], "restart", NotFoundError, "Task not found"),
    ("restart", ["1"], "restart", APIError, "API error"),
])
def test_always_on_error_handling(command, args, mock_method, error_class, expected_msg):
    """always-on commands show appropriate error messages."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        getattr(mock_client, mock_method).side_effect = error_class("Test error")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, [command] + args)

    assert result.exit_code == 1
    assert expected_msg in result.output


def test_always_on_update_command():
    """always-on update updates task command."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["update", "1", "-c", "echo updated"])

    assert result.exit_code == 0
    assert "Always-on task 1 updated" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, command="echo updated")


def test_always_on_update_description():
    """always-on update updates task description."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["update", "1", "-d", "new description"])

    assert result.exit_code == 0
    assert "Always-on task 1 updated" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, description="new description")


def test_always_on_update_enabled():
    """always-on update enables task."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["update", "1", "-e"])

    assert result.exit_code == 0
    assert "Always-on task 1 updated" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, enabled=True)


def test_always_on_update_disabled():
    """always-on update disables task."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["update", "1", "-E"])

    assert result.exit_code == 0
    assert "Always-on task 1 updated" in result.output
    mock_client.update.assert_called_once_with("testuser", 1, enabled=False)


def test_always_on_update_no_options():
    """always-on update shows error when no options specified."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["update", "1"])

    assert result.exit_code == 1
    assert "No update specified" in result.output


def test_always_on_restart():
    """always-on restart restarts task."""
    with patch("pa_cli.cli.always_on_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["restart", "1"])

    assert result.exit_code == 0
    assert "Always-on task 1 restarted" in result.output
    mock_client.restart.assert_called_once_with("testuser", 1)
