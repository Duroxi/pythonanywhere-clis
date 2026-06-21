from unittest.mock import patch, MagicMock

from pa_cli.api.consoles import ConsolesClient


def test_create_console():
    client = ConsolesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 42, "executable": "bash"}
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        result = client.create("testuser")

    assert result["id"] == 42


def test_send_input():
    client = ConsolesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.send_input("testuser", 42, "ls\n")

    mock_req.assert_called_once()


def test_get_output():
    client = ConsolesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"output": "file1.txt\nfile2.txt\n"}
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        result = client.get_output("testuser", 42)

    assert "file1.txt" in result["output"]


def test_kill_console():
    client = ConsolesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        client.kill("testuser", 42)


def test_list_consoles():
    """list returns list of consoles."""
    client = ConsolesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "name": "bash"},
        {"id": 2, "name": "python3.10"},
    ]
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.list("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/consoles/", username="testuser")
    assert len(result) == 2
    assert result[0]["id"] == 1
