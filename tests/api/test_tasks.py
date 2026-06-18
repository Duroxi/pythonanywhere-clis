from unittest.mock import patch, MagicMock

from pa_cli.api.tasks import TasksClient


def test_list_tasks():
    """list returns list of tasks."""
    client = TasksClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "command": "echo hello", "interval": "daily", "enabled": True},
        {"id": 2, "command": "echo world", "interval": "hourly", "enabled": False},
    ]
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.list("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/schedule/", username="testuser")
    assert len(result) == 2
    assert result[0]["id"] == 1


def test_get_task():
    """get returns task details."""
    client = TasksClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 1, "command": "echo hello", "interval": "daily", "enabled": True}
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get("testuser", 1)

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/schedule/{id}/", username="testuser", id=1)
    assert result["id"] == 1


def test_create_task():
    """create returns created task."""
    client = TasksClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 3, "command": "echo new", "interval": "daily", "enabled": True}
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.create("testuser", "echo new", interval="daily", hour=0, minute=0)

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/schedule/",
        username="testuser",
        json={
            "command": "echo new",
            "interval": "daily",
            "hour": 0,
            "minute": 0,
            "enabled": True,
            "description": "",
        },
    )
    assert result["id"] == 3


def test_update_task():
    """update sends PATCH request."""
    client = TasksClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 1, "enabled": False}
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.update("testuser", 1, enabled=False)

    mock_req.assert_called_once_with(
        "PATCH",
        "/api/v0/user/{username}/schedule/{id}/",
        username="testuser",
        id=1,
        json={"enabled": False},
    )
    assert result["enabled"] is False


def test_delete_task():
    """delete sends DELETE request."""
    client = TasksClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.delete("testuser", 1)

    mock_req.assert_called_once_with("DELETE", "/api/v0/user/{username}/schedule/{id}/", username="testuser", id=1)
