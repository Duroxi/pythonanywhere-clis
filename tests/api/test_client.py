import requests
from unittest.mock import patch, MagicMock

import pytest

from pa_cli.api.client import BaseClient


def test_base_client_sets_auth_header():
    client = BaseClient(token="test-token", host="www.pythonanywhere.com")
    assert client.session.headers["Authorization"] == "Token test-token"


def test_base_client_builds_url():
    client = BaseClient(token="t", host="www.pythonanywhere.com")
    url = client._build_url("/api/v0/user/{username}/files/", username="testuser")
    assert url == "https://www.pythonanywhere.com/api/v0/user/testuser/files/"


def test_base_client_raises_on_api_error():
    client = BaseClient(token="t", host="www.pythonanywhere.com")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {"detail": "Forbidden"}
    mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)

    with patch.object(client.session, "request", return_value=mock_response):
        try:
            client._request("GET", "/api/v0/user/{username}/cpu/", username="testuser")
            assert False, "Should have raised"
        except Exception as e:
            assert "403" in str(e) or "Forbidden" in str(e)


def test_base_client_raises_on_404():
    """BaseClient raises NotFoundError on 404 response."""
    from pa_cli.api.client import BaseClient
    from pa_cli.exceptions import NotFoundError

    client = BaseClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(NotFoundError):
            client._request("GET", "/api/v0/user/{username}/test/", username="u")


def test_base_client_raises_on_connection_error():
    """BaseClient raises NetworkError on ConnectionError."""
    from pa_cli.api.client import BaseClient
    from pa_cli.exceptions import NetworkError
    import requests

    client = BaseClient(token="t", host="www.pythonanywhere.com")

    with patch.object(client.session, "request", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(NetworkError):
            client._request("GET", "/api/v0/user/{username}/test/", username="u")


def test_base_client_raises_on_timeout():
    """BaseClient raises NetworkError on Timeout."""
    from pa_cli.api.client import BaseClient
    from pa_cli.exceptions import NetworkError
    import requests

    client = BaseClient(token="t", host="www.pythonanywhere.com")

    with patch.object(client.session, "request", side_effect=requests.Timeout("timeout")):
        with pytest.raises(NetworkError):
            client._request("GET", "/api/v0/user/{username}/test/", username="u")


def test_base_client_raises_api_error_on_http_error():
    """BaseClient raises APIError on HTTP error."""
    from pa_cli.api.client import BaseClient
    from pa_cli.exceptions import APIError
    import requests

    client = BaseClient(token="t", host="www.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_resp.json.return_value = {"detail": "Internal server error"}

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(APIError, match="Internal server error"):
            client._request("GET", "/api/v0/user/{username}/test/", username="u")


def test_base_client_builds_url():
    """_build_url constructs correct URL."""
    from pa_cli.api.client import BaseClient

    client = BaseClient(token="t", host="www.pythonanywhere.com")
    url = client._build_url("/api/v0/user/{username}/test/", username="testuser")
    assert url == "https://www.pythonanywhere.com/api/v0/user/testuser/test/"


def test_base_client_sets_host():
    """BaseClient stores host correctly."""
    from pa_cli.api.client import BaseClient

    client = BaseClient(token="t", host="eu.pythonanywhere.com")
    assert client.host == "eu.pythonanywhere.com"
    assert client.base_url == "https://eu.pythonanywhere.com"


def test_base_client_default_host():
    """BaseClient uses default host when not specified."""
    from pa_cli.api.client import BaseClient

    client = BaseClient(token="t")
    assert client.host == "www.pythonanywhere.com"
