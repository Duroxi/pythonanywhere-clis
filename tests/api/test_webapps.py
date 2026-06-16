from unittest.mock import patch, MagicMock

from pa_cli.api.webapps import WebappsClient


def test_create_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        client.create("testuser", "testuser.pythonanywhere.com", "python310")


def test_update_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        client.update(
            "testuser",
            "testuser.pythonanywhere.com",
            source_directory="/home/testuser/mysite",
            virtualenv_path="/home/testuser/.virtualenvs/mysite",
        )


def test_add_static_file():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        client.add_static_file(
            "testuser",
            "testuser.pythonanywhere.com",
            url="/static/",
            path="/home/testuser/mysite/static",
        )


def test_reload_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp):
        client.reload("testuser", "testuser.pythonanywhere.com")


def test_delete_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.delete("testuser", "testuser.pythonanywhere.com")

    mock_req.assert_called_once_with(
        "DELETE",
        "/api/v0/user/{username}/webapps/{domain_name}/",
        username="testuser",
        domain_name="testuser.pythonanywhere.com",
    )


def test_enable_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.enable("testuser", "testuser.pythonanywhere.com")

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/webapps/{domain_name}/enable/",
        username="testuser",
        domain_name="testuser.pythonanywhere.com",
    )


def test_disable_webapp():
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.disable("testuser", "testuser.pythonanywhere.com")

    mock_req.assert_called_once_with(
        "POST",
        "/api/v0/user/{username}/webapps/{domain_name}/disable/",
        username="testuser",
        domain_name="testuser.pythonanywhere.com",
    )
