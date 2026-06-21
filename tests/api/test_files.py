from unittest.mock import patch, MagicMock

import pytest

from pa_cli.api.files import FilesClient
from pa_cli.exceptions import APIError, NotFoundError


def test_upload_file():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.raise_for_status = MagicMock()

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        result = client.upload(
            username="testuser",
            remote_path="/home/testuser/index.html",
            content=b"<h1>Hello</h1>",
        )

    mock_post.assert_called_once()
    assert result == 201


def test_upload_directory():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        result = client.upload(
            username="testuser",
            remote_path="/home/testuser/mysite/",
            content=b"<h1>Hello</h1>",
        )

    assert result == 200


# --- list tests ---


def test_list_returns_json_dict():
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    expected = {"index.html": {"type": "file", "url": "/api/v0/user/testuser/files/path/home/testuser/index.html"}}

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = expected

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.list(username="testuser", remote_path="/home/testuser/")

    mock_get.assert_called_once_with(
        "https://www.pythonanywhere.com/api/v0/user/testuser/files/path/home/testuser/"
    )
    assert result == expected


def test_list_raises_on_http_error():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    mock_response.raise_for_status.side_effect = Exception("404")

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(NotFoundError, match="Not found"):
            client.list(username="testuser", remote_path="/home/testuser/missing/")


# --- download tests ---


def test_download_returns_bytes():
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    file_content = b"hello world"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.content = file_content

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.download(username="testuser", remote_path="/home/testuser/file.txt")

    mock_get.assert_called_once_with(
        "https://www.pythonanywhere.com/api/v0/user/testuser/files/path/home/testuser/file.txt"
    )
    assert result == file_content


def test_download_raises_on_http_error():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_response.raise_for_status.side_effect = Exception("403")

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(APIError, match="Download failed"):
            client.download(username="testuser", remote_path="/home/testuser/secret.txt")


# --- delete tests ---


def test_delete_makes_delete_request():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.raise_for_status = MagicMock()

    with patch.object(client.session, "delete", return_value=mock_response) as mock_delete:
        client.delete(username="testuser", remote_path="/home/testuser/file.txt")

    mock_delete.assert_called_once_with(
        "https://www.pythonanywhere.com/api/v0/user/testuser/files/path/home/testuser/file.txt"
    )


def test_delete_raises_on_http_error():
    client = FilesClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    mock_response.raise_for_status.side_effect = Exception("404")

    with patch.object(client.session, "delete", return_value=mock_response):
        with pytest.raises(NotFoundError, match="Not found"):
            client.delete(username="testuser", remote_path="/home/testuser/missing.txt")


def test_share_file():
    """share returns share URL."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"url": "/user/testuser/shares/abc123/"}

    with patch.object(client, "_request", return_value=mock_response) as mock_req:
        result = client.share("testuser", "/home/testuser/test.txt")

    assert result == "/user/testuser/shares/abc123/"
    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/files/sharing/",
        username="testuser",
        json={"path": "/home/testuser/test.txt"},
    )


def test_unshare_file():
    """unshare sends DELETE request."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_response) as mock_req:
        client.unshare("testuser", "/home/testuser/test.txt")

    mock_req.assert_called_once_with(
        "DELETE",
        "/api/v0/user/{username}/files/sharing/",
        username="testuser",
        params={"path": "/home/testuser/test.txt"},
    )


def test_get_share_status():
    """get_share_status returns share URL."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"url": "/user/testuser/shares/abc123/"}

    with patch.object(client, "_request", return_value=mock_response) as mock_req:
        result = client.get_share_status("testuser", "/home/testuser/test.txt")

    assert result == "/user/testuser/shares/abc123/"
    mock_req.assert_called_once_with(
        "GET",
        "/api/v0/user/{username}/files/sharing/",
        username="testuser",
        params={"path": "/home/testuser/test.txt"},
    )


def test_list_files():
    """list returns dict of files."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "app.py": {"type": "file", "url": "..."},
        "static": {"type": "directory", "url": "..."},
    }

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.list("testuser", "/home/testuser/")

    assert "app.py" in result
    assert "static" in result


def test_download_file():
    """download returns file content."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.content = b"file content"

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.download("testuser", "/home/testuser/app.py")

    assert result == b"file content"


def test_delete_file():
    """delete sends DELETE request."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(client.session, "delete", return_value=mock_response) as mock_delete:
        client.delete("testuser", "/home/testuser/old.txt")

    mock_delete.assert_called_once()


def test_upload_file():
    """upload sends POST request and returns status code."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        result = client.upload("testuser", "/home/testuser/app.py", b"content")

    assert result == 200
    mock_post.assert_called_once()


def test_list_files_empty():
    """list returns empty dict for empty directory."""
    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {}

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.list("testuser", "/home/testuser/empty/")

    assert result == {}


def test_download_file_not_found():
    """download raises NotFoundError for missing file."""
    from pa_cli.exceptions import NotFoundError

    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(NotFoundError):
            client.download("testuser", "/home/testuser/missing.txt")


def test_upload_file_not_found():
    """upload raises NotFoundError for invalid path."""
    from pa_cli.exceptions import NotFoundError

    client = FilesClient(token="t", host="www.pythonanywhere.com")
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch.object(client.session, "post", return_value=mock_response):
        with pytest.raises(NotFoundError):
            client.upload("testuser", "/invalid/path", b"content")
