from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from pa_cli.cli.status_cmd import app
from pa_cli.exceptions import AuthError, NotFoundError

runner = CliRunner()


def test_status_cpu():
    """status cpu shows CPU usage."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_cpu_usage.return_value = {
            "daily_cpu_total_usage_seconds": 120.5,
            "daily_cpu_limit_seconds": 3600.0,
            "next_reset_time": "2026-06-16T00:00:00Z",
        }
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["cpu"])

    assert result.exit_code == 0
    assert "CPU Usage" in result.output
    assert "120.5" in result.output
    assert "3600.0" in result.output


def test_status_cpu_network_error():
    """status cpu shows error on network failure."""
    from pa_cli.exceptions import NetworkError

    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_cpu_usage.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["cpu"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_status_cpu_auth_error():
    """status cpu shows error on auth failure."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_cpu_usage.side_effect = AuthError("Invalid token")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["cpu"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_status_cpu_not_found():
    """status cpu shows error when resource not found."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_cpu_usage.side_effect = NotFoundError("Not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["cpu"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_status_cpu_missing_fields():
    """status cpu handles missing fields in response."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_cpu_usage.return_value = {}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["cpu"])

    assert result.exit_code == 0
    assert "N/A" in result.output


def test_status_disk():
    """status disk shows disk usage."""
    with patch("pa_cli.cli.status_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.status_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_disk_usage.return_value = {
            "used": "20.1 MB",
            "quota": "512.0 MB",
            "percent": "4%",
        }
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disk"])

    assert result.exit_code == 0
    assert "Disk Usage" in result.output
    assert "20.1 MB" in result.output
    assert "512.0 MB" in result.output
    assert "4%" in result.output


def test_status_disk_network_error():
    """status disk shows error on network failure."""
    from pa_cli.exceptions import NetworkError

    with patch("pa_cli.cli.status_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.status_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = NetworkError("Connection failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disk"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_status_disk_auth_error():
    """status disk shows error on auth failure."""
    with patch("pa_cli.cli.status_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.status_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disk"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_status_disk_not_found():
    """status disk shows error when resource not found."""
    with patch("pa_cli.cli.status_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.status_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_disk_usage.side_effect = NotFoundError("Not found")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disk"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_status_disk_missing_fields():
    """status disk handles missing fields in response."""
    with patch("pa_cli.cli.status_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.status_cmd.AccountCrawler") as mock_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_disk_usage.return_value = {}
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["disk"])

    assert result.exit_code == 0
    assert "N/A" in result.output


def test_status_system_image_get():
    """status system-image shows current system image."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_system_image.return_value = {
            "system_image": "ubuntu-20.04",
            "available_system_images": ["ubuntu-20.04", "ubuntu-22.04"],
        }
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image"])

    assert result.exit_code == 0
    assert "Current system image: ubuntu-20.04" in result.output
    assert "ubuntu-20.04, ubuntu-22.04" in result.output


def test_status_system_image_set():
    """status system-image sets system image."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image", "ubuntu-22.04"])

    assert result.exit_code == 0
    assert "System image set to ubuntu-22.04" in result.output
    mock_client.set_system_image.assert_called_once_with("testuser", "ubuntu-22.04")


def test_status_system_image_network_error():
    """status system-image shows error on network failure."""
    from pa_cli.exceptions import NetworkError

    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_system_image.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_status_system_image_auth_error():
    """status system-image shows error on auth failure."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_system_image.side_effect = AuthError("Invalid token")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image"])

    assert result.exit_code == 1
    assert "Auth error" in result.output


def test_status_system_image_not_found():
    """status system-image shows error when resource not found."""
    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_system_image.side_effect = NotFoundError("Not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image"])

    assert result.exit_code == 1
    assert "Not found" in result.output


def test_status_system_image_api_error():
    """status system-image shows error on API failure."""
    from pa_cli.exceptions import APIError

    with patch("pa_cli.cli.status_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_system_image.side_effect = APIError("API error")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["system-image"])

    assert result.exit_code == 1
    assert "API error" in result.output
