from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from pa_cli.cli.always_on_cmd import app

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

        result = runner.invoke(app, ["create", "echo new"])

    assert result.exit_code == 0
    assert "Always-on task created" in result.output
    assert "ID=3" in result.output
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
