from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.webapps_cmd import app
from pa_cli.exceptions import AuthError, NetworkError

runner = CliRunner()


def test_webapp_create():
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["create", "u.pythonanywhere.com", "--python", "python310"])

    assert result.exit_code == 0
    assert "created" in result.output.lower()


def test_webapp_config():
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, [
            "config", "u.pythonanywhere.com",
            "--source-dir", "/home/u/mysite",
            "--virtualenv", "/home/u/.virtualenvs/mysite",
        ])

    assert result.exit_code == 0


def test_webapp_static():
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, [
            "static", "u.pythonanywhere.com",
            "--url", "/static/",
            "--path", "/home/u/mysite/static",
        ])

    assert result.exit_code == 0


def test_webapp_reload():
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["reload", "u.pythonanywhere.com"])

    assert result.exit_code == 0


# --- hits command tests ---


def test_hits_command_logs_in_and_gets_hits():
    """hits command creates crawler, logs in, and displays hit statistics."""
    hits_data = {
        "hits_current_hour": 5,
        "hits_previous_hour": 10,
        "hits_current_day": 100,
        "hits_previous_day": 200,
        "hits_current_month": 3000,
        "hits_previous_month": 4000,
    }

    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_hits.return_value = hits_data
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["hits", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    mock_crawler.login.assert_called_once()
    mock_crawler.get_hits.assert_called_once_with("u.pythonanywhere.com")
    assert "5" in result.output
    assert "100" in result.output
    assert "3000" in result.output


def test_hits_command_exits_on_login_failure():
    """hits command exits with error when login returns False."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed: The user name or password is incorrect.")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["hits", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_hits_command_exits_on_login_exception():
    """hits command exits with error when login raises exception."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = NetworkError("Password not found")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["hits", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


# --- reload-crawler command tests ---


def test_reload_crawler_command_logs_in_and_reloads():
    """reload-crawler command creates crawler, logs in, and reloads web app."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.reload_webapp.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["reload-crawler", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    mock_crawler.login.assert_called_once()
    mock_crawler.reload_webapp.assert_called_once_with("u.pythonanywhere.com")
    assert "reloaded" in result.output.lower()


def test_reload_crawler_command_exits_on_login_failure():
    """reload-crawler command exits with error when login raises."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed: The user name or password is incorrect.")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["reload-crawler", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_reload_crawler_command_exits_on_reload_failure():
    """reload-crawler command exits with error when reload_webapp returns False."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.reload_webapp.return_value = False
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["reload-crawler", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Failed to reload" in result.output


def test_reload_crawler_command_exits_on_login_exception():
    """reload-crawler command exits with error when login raises exception."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = NetworkError("Password not found")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["reload-crawler", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


# --- delete command tests ---


def test_webapp_delete_with_force():
    """delete command deletes webapp with --force flag."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "u.pythonanywhere.com", "-f"])

    assert result.exit_code == 0
    assert "deleted" in result.output.lower()
    mock_client.delete.assert_called_once_with("u", "u.pythonanywhere.com")


def test_webapp_delete_cancelled():
    """delete command cancels when user says no."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "u.pythonanywhere.com"], input="n\n")

    assert "Cancelled" in result.output
    mock_client.delete.assert_not_called()


# --- enable command tests ---


def test_webapp_enable():
    """enable command enables webapp."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["enable", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    assert "enabled" in result.output.lower()
    mock_client.enable.assert_called_once_with("u", "u.pythonanywhere.com")


# --- disable command tests ---


def test_webapp_disable():
    """disable command disables webapp."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["disable", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    assert "disabled" in result.output.lower()
    mock_client.disable.assert_called_once_with("u", "u.pythonanywhere.com")
