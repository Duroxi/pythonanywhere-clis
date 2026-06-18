from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from pa_cli.cli.status_cmd import app

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
    assert "网络错误" in result.output


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
    assert "网络错误" in result.output
