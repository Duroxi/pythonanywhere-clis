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


def test_update_always_on_task():
    """update sends PATCH request."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.update("testuser", 1, command="echo updated", enabled=False)

    mock_req.assert_called_once_with(
        "PATCH",
        "/api/v0/user/{username}/always_on/{id}/",
        username="testuser",
        id=1,
        json={"command": "echo updated", "enabled": False},
    )


def test_update_always_on_task_partial():
    """update with partial data sends PATCH request."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.update("testuser", 1, description="new description")

    mock_req.assert_called_once_with(
        "PATCH",
        "/api/v0/user/{username}/always_on/{id}/",
        username="testuser",
        id=1,
        json={"description": "new description"},
    )


def test_restart_always_on_task():
    """restart sends POST request to restart endpoint."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.restart("testuser", 1)

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/always_on/{id}/restart/",
        username="testuser",
        id=1,
        json={},
    )


def test_restart_always_on_task_with_params():
    """restart with params sends POST request with data."""
    client = AlwaysOnClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.restart("testuser", 1, command="echo restarted")

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/always_on/{id}/restart/",
        username="testuser",
        id=1,
        json={"command": "echo restarted"},
    )
