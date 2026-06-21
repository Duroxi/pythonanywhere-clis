from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.webapps_cmd import app
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

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
    """enable command enables webapp via crawler."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.enable_webapp.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["enable", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    assert "enabled" in result.output.lower()
    mock_crawler.login.assert_called_once()
    mock_crawler.enable_webapp.assert_called_once_with("u.pythonanywhere.com")


# --- disable command tests ---


def test_webapp_disable():
    """disable command disables webapp via crawler."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.disable_webapp.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disable", "u.pythonanywhere.com"])

    assert result.exit_code == 0
    assert "disabled" in result.output.lower()
    mock_crawler.login.assert_called_once()
    mock_crawler.disable_webapp.assert_called_once_with("u.pythonanywhere.com")


# --- logs command tests ---


def test_webapp_logs():
    """logs command shows error logs by default."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.return_value = b"line1\nline2\nline3\n"
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs"])

    assert result.exit_code == 0
    assert "line1" in result.output
    assert "line2" in result.output
    mock_client.download.assert_called_once_with("u", "/var/log/u.pythonanywhere.com.error.log")


def test_webapp_logs_with_type():
    """logs command shows specified log type."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.return_value = b"access log content\n"
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs", "--type", "access"])

    assert result.exit_code == 0
    assert "access log content" in result.output
    mock_client.download.assert_called_once_with("u", "/var/log/u.pythonanywhere.com.access.log")


def test_webapp_logs_with_domain():
    """logs command shows logs for specified domain."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.return_value = b"log content\n"
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs", "myapp.pythonanywhere.com"])

    assert result.exit_code == 0
    mock_client.download.assert_called_once_with("u", "/var/log/myapp.pythonanywhere.com.error.log")


def test_webapp_logs_file_not_found():
    """logs command shows error when log file not found."""
    from pa_cli.exceptions import NotFoundError

    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs"])

    assert result.exit_code == 1
    assert "Log file not found" in result.output


# --- ssl command tests ---


def test_webapp_ssl():
    """ssl command shows SSL certificate info."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_ssl_info.return_value = {"cert_type": "pythonanywhere-subdomain"}
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ssl"])

    assert result.exit_code == 0
    assert "SSL Certificate Info" in result.output
    assert "pythonanywhere-subdomain" in result.output
    mock_client.get_ssl_info.assert_called_once_with("u", "u.pythonanywhere.com")


def test_webapp_ssl_with_domain():
    """ssl command shows SSL info for specified domain."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_ssl_info.return_value = {"cert_type": "lets-encrypt"}
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ssl", "myapp.pythonanywhere.com"])

    assert result.exit_code == 0
    assert "lets-encrypt" in result.output
    mock_client.get_ssl_info.assert_called_once_with("u", "myapp.pythonanywhere.com")


def test_webapp_config_no_options():
    """webapp config shows error when no options given."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["config", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "No configuration specified" in result.output


def test_webapp_enable_network_error():
    """webapp enable shows error on network failure."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = NetworkError("Connection failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["enable", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_webapp_logs_network_error():
    """webapp logs shows error on network failure."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_webapp_ssl_network_error():
    """webapp ssl shows error on network failure."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_ssl_info.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ssl"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_webapp_hits_auth_error():
    """webapp hits shows error on auth failure."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["hits", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_webapp_reload_crawler_network_error():
    """webapp reload-crawler shows error on network failure."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = NetworkError("Connection failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["reload-crawler", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_webapp_delete_auth_error():
    """webapp delete shows error on auth failure."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.delete.side_effect = AuthError("Invalid token")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "u.pythonanywhere.com", "-f"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_webapp_logs_auth_error():
    """webapp logs shows error on auth failure."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.side_effect = AuthError("Invalid token")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_webapp_ssl_auth_error():
    """webapp ssl shows error on auth failure."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_ssl_info.side_effect = AuthError("Invalid token")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ssl"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_webapp_enable_not_found():
    """webapp enable shows error when webapp not found."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.enable_webapp.side_effect = NotFoundError("Enable form not found")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["enable", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_webapp_disable_not_found():
    """webapp disable shows error when webapp not found."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.disable_webapp.side_effect = NotFoundError("Disable form not found")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disable", "u.pythonanywhere.com"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_webapp_logs_not_found():
    """webapp logs shows error when log file not found."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.download.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs"])

    assert result.exit_code == 1
    assert "Log file not found" in result.output


def test_webapp_ssl_not_found():
    """webapp ssl shows error when webapp not found."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_ssl_info.side_effect = NotFoundError("Not found")
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ssl"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_webapp_config_with_python_version():
    """webapp config passes python version correctly."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, [
            "config", "u.pythonanywhere.com",
            "--python-version", "3.11",
        ])

    assert result.exit_code == 0
    mock_client.update.assert_called_once()
    call_kwargs = mock_client.update.call_args[1]
    assert call_kwargs["python_version"] == "3.11"


def test_webapp_config_with_working_dir():
    """webapp config passes working directory correctly."""
    with patch("pa_cli.cli.webapps_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.webapps_cmd.WebappsClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, [
            "config", "u.pythonanywhere.com",
            "--working-dir", "/home/u/mysite",
        ])

    assert result.exit_code == 0
    mock_client.update.assert_called_once()
    call_kwargs = mock_client.update.call_args[1]
    assert call_kwargs["working_directory"] == "/home/u/mysite"


def test_webapp_delete_cancelled():
    """webapp delete cancels when user says no."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["delete", "u.pythonanywhere.com"], input="n\n")

    assert "Cancelled" in result.output
    mock_client.delete.assert_not_called()


def test_webapp_logs_with_lines():
    """webapp logs shows specified number of lines."""
    with patch("pa_cli.cli.webapps_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        log_content = "\n".join([f"line {i}" for i in range(100)])
        mock_client.download.return_value = log_content.encode()
        mock_get_client.return_value = ({"username": "u", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["logs", "--lines", "5"])

    assert result.exit_code == 0
    # Should only show last 5 lines
    lines = result.output.strip().split("\n")
    assert len(lines) == 5
