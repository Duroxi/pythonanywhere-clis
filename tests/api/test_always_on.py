from unittest.mock import patch, MagicMock

from pa_cli.api.always_on import AlwaysOnClient


def test_list_always_on_tasks():
    """list returns list of tasks."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "command": "echo hello", "enabled": True},
        {"id": 2, "command": "echo world", "enabled": False},
    ]
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.list("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/always_on/", username="testuser")
    assert len(result) == 2
    assert result[0]["id"] == 1


def test_create_always_on_task():
    """create returns created task."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 3, "command": "echo new", "enabled": True}
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.create("testuser", "echo new")

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/always_on/",
        username="testuser",
        json={"command": "echo new", "enabled": True},
    )
    assert result["id"] == 3


def test_delete_always_on_task():
    """delete sends DELETE request."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.delete("testuser", 1)

    mock_req.assert_called_once_with("DELETE", "/api/v0/user/{username}/always_on/{id}/", username="testuser", id=1)
