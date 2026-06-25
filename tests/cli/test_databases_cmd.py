import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.databases_cmd import app
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

runner = CliRunner()


def test_databases_mysql():
    """databases mysql shows database information."""
    with patch("pa_cli.cli.databases_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_mysql_info.return_value = [
            {"database_name": "testuser$mydb", "size": "10.5 MB"},
            {"database_name": "testuser$testdb", "size": "2.1 MB"},
        ]
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "MySQL Databases" in result.output
    assert "testuser$mydb" in result.output
    assert "10.5 MB" in result.output
    assert "testuser$testdb" in result.output
    assert "2.1 MB" in result.output


def test_databases_mysql_empty():
    """databases mysql shows message when no databases."""
    with patch("pa_cli.cli.databases_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_mysql_info.return_value = []
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "No MySQL databases found" in result.output


@pytest.mark.parametrize("error_class,expected_msg", [
    (NetworkError, "Network error"),
    (AuthError, "Auth error"),
    (NotFoundError, "Not found"),
    (APIError, "API error"),
])
def test_databases_mysql_error_handling(error_class, expected_msg):
    """databases mysql shows appropriate error messages."""
    with patch("pa_cli.cli.databases_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_mysql_info.side_effect = error_class("Test error")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert expected_msg in result.output
