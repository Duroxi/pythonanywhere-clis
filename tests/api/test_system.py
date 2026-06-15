from unittest.mock import patch, MagicMock

from pa_cli.api.system import SystemClient


def test_get_cpu_usage():
    """get_cpu_usage returns CPU stats."""
    client = SystemClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "daily_cpu_total_usage_seconds": 120.5,
        "daily_cpu_limit_seconds": 3600.0,
        "next_reset_time": "2026-06-16T00:00:00Z",
    }
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get_cpu_usage("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/cpu/", username="testuser")
    assert result["daily_cpu_total_usage_seconds"] == 120.5
    assert result["daily_cpu_limit_seconds"] == 3600.0
    assert "next_reset_time" in result
