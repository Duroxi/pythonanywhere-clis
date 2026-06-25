from unittest.mock import patch, MagicMock

from pa_cli.api.databases import DatabasesClient


def test_get_mysql_info():
    """get_mysql_info returns database information."""
    client = DatabasesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"database_name": "testuser$mydb", "size": "10.5 MB"},
        {"database_name": "testuser$testdb", "size": "2.1 MB"},
    ]
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get_mysql_info("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/databases/mysql/", username="testuser")
    assert len(result) == 2
    assert result[0]["database_name"] == "testuser$mydb"
    assert result[1]["size"] == "2.1 MB"


def test_get_mysql_info_empty():
    """get_mysql_info returns empty list when no databases."""
    client = DatabasesClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get_mysql_info("testuser")

    mock_req.assert_called_once_with("GET", "/api/v0/user/{username}/databases/mysql/", username="testuser")
    assert result == []
