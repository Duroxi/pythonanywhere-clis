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
        result = runner.invoke(app, [])

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
        result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert "网络错误" in result.output
