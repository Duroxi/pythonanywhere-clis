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


def test_get_ssl_info():
    """get_ssl_info returns SSL certificate information."""
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"cert_type": "pythonanywhere-subdomain"}
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get_ssl_info("testuser", "testuser.pythonanywhere.com")

    mock_req.assert_called_once_with(
        "GET",
        "/api/v0/user/{username}/webapps/{domain_name}/ssl/",
        username="testuser",
        domain_name="testuser.pythonanywhere.com",
    )
    assert result["cert_type"] == "pythonanywhere-subdomain"


def test_get_default_python3_version():
    """get_default_python3_version returns version info."""
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "version": "python310",
        "available_versions": ["python38", "python39", "python310", "python311"],
    }
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        result = client.get_default_python3_version("testuser")

    mock_req.assert_called_once_with(
        "GET",
        "/api/v0/user/{username}/default_python3_version/",
        username="testuser",
    )
    assert result["version"] == "python310"
    assert len(result["available_versions"]) == 4


def test_set_default_python3_version():
    """set_default_python3_version sends PATCH request."""
    client = WebappsClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    with patch.object(client, "_request", return_value=mock_resp) as mock_req:
        client.set_default_python3_version("testuser", "python311")

    mock_req.assert_called_once_with(
        "PATCH",
        "/api/v0/user/{username}/default_python3_version/",
        username="testuser",
        json={"version": "python311"},
    )
