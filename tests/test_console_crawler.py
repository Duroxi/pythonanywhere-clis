import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from pa_cli.crawler.console_crawler import ConsoleCrawler


LOGIN_PAGE_HTML = '<html><body><form><input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token"></form></body></html>'


def _mock_get_response(html=LOGIN_PAGE_HTML):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def _mock_post_response(url):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    type(resp).url = PropertyMock(return_value=url)
    return resp


def test_login_success_redirects_away_from_login_page():
    """Login succeeds when response URL does not contain /login/."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response("https://www.pythonanywhere.com/user/testuser/")) as mock_post:

        result = crawler.login("testuser", "testpass")

        assert result is True
        mock_get.assert_called_once_with("https://www.pythonanywhere.com/login/")
        mock_post.assert_called_once()
        posted_data = mock_post.call_args[1]["data"]
        assert posted_data["csrfmiddlewaretoken"] == "test-csrf-token"
        assert posted_data["auth-username"] == "testuser"
        assert posted_data["auth-password"] == "testpass"
        assert posted_data["login_view-current_step"] == "auth"


def test_login_failure_stays_on_login_page():
    """Login fails when response URL still contains /login/."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_post_response("https://www.pythonanywhere.com/login/")):

        result = crawler.login("baduser", "badpass")

        assert result is False


def test_login_uses_session_for_cookie_management():
    """Login uses requests.Session to maintain cookies."""
    crawler = ConsoleCrawler()
    assert isinstance(crawler.session, requests.Session)


def test_login_sets_user_agent_header():
    """Login sends User-Agent header set on the session."""
    crawler = ConsoleCrawler()
    assert "User-Agent" in crawler.session.headers


def test_login_uses_dynamic_referer():
    """Login sets Referer dynamically based on base_url, not hardcoded."""
    crawler = ConsoleCrawler(host="custom.pythonanywhere.com")

    with patch.object(crawler.session, "get", return_value=_mock_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response("https://custom.pythonanywhere.com/user/testuser/")):

        crawler.login("testuser", "testpass")

        get_call_url = mock_get.call_args[0][0]
        assert "custom.pythonanywhere.com" in get_call_url


def test_login_custom_host():
    """ConsoleCrawler accepts custom host parameter."""
    crawler = ConsoleCrawler(host="eu.pythonanywhere.com")
    assert crawler.base_url == "https://eu.pythonanywhere.com"


def test_login_default_host():
    """ConsoleCrawler defaults to www.pythonanywhere.com."""
    crawler = ConsoleCrawler()
    assert crawler.base_url == "https://www.pythonanywhere.com"


def test_login_raises_on_network_error():
    """Login raises Exception with context on network failure."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch login page"):
            crawler.login("testuser", "testpass")


def test_login_raises_on_missing_csrf():
    """Login raises Exception when CSRF token is not found on page."""
    crawler = ConsoleCrawler()
    html_without_csrf = '<html><body><form></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_without_csrf)):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.login("testuser", "testpass")


def test_login_raises_on_post_network_error():
    """Login raises Exception with context when POST fails."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Login request failed"):
            crawler.login("testuser", "testpass")


# --- list tests ---


def test_list_returns_list():
    """list returns the list of console objects from the API."""
    crawler = ConsoleCrawler()
    mock_consoles = [
        {"id": 1, "name": "bash", "console_url": "https://www.pythonanywhere.com/user/testuser/consoles/1/"},
        {"id": 2, "name": "python3.10", "console_url": "https://www.pythonanywhere.com/user/testuser/consoles/2/"},
    ]
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_consoles
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get:
        result = crawler.list("testuser")

    assert result == mock_consoles
    mock_get.assert_called_once_with("https://www.pythonanywhere.com/api/v0/user/testuser/consoles/")


def test_list_empty():
    """list returns empty list when user has no consoles."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp):
        result = crawler.list("testuser")

    assert result == []


def test_list_raises_on_network_error():
    """list raises Exception on network failure."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to list consoles"):
            crawler.list("testuser")


def test_list_uses_dynamic_host():
    """list uses the correct base_url for custom host."""
    crawler = ConsoleCrawler(host="eu.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get:
        crawler.list("testuser")

    mock_get.assert_called_once_with("https://eu.pythonanywhere.com/api/v0/user/testuser/consoles/")


# --- create tests ---


def test_create_returns_console_object():
    """create returns the created console object from the API."""
    crawler = ConsoleCrawler()
    mock_console = {
        "id": 12345,
        "console_url": "https://www.pythonanywhere.com/user/testuser/consoles/12345/",
        "console_frame_url": "https://www.pythonanywhere.com/user/testuser/consoles/12345/frame/",
    }
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_console
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "test-csrf-token")

    with patch.object(crawler.session, "post", return_value=mock_resp) as mock_post:
        result = crawler.create("testuser")

    assert result == mock_console
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://www.pythonanywhere.com/api/v0/user/testuser/consoles/"
    assert call_args[1]["json"] == {"executable": "bash"}
    assert call_args[1]["headers"]["X-CSRFToken"] == "test-csrf-token"
    assert "testuser/consoles" in call_args[1]["headers"]["Referer"]


def test_create_with_custom_executable():
    """create passes custom executable to the API."""
    crawler = ConsoleCrawler()
    mock_console = {"id": 99, "console_url": "https://example.com/consoles/99/"}
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_console
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "csrf-value")

    with patch.object(crawler.session, "post", return_value=mock_resp) as mock_post:
        result = crawler.create("testuser", executable="python3.10")

    call_args = mock_post.call_args
    assert call_args[1]["json"] == {"executable": "python3.10"}
    assert result == mock_console


def test_create_raises_on_network_error():
    """create raises Exception on network failure."""
    crawler = ConsoleCrawler()
    crawler.session.cookies.set("csrftoken", "test-csrf-token")

    with patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to create console"):
            crawler.create("testuser")


def test_create_raises_on_missing_csrf():
    """create raises Exception when CSRF token is missing from cookies."""
    crawler = ConsoleCrawler()

    with pytest.raises(Exception, match="CSRF token not found"):
        crawler.create("testuser")


def test_create_uses_dynamic_host():
    """create uses the correct base_url for custom host."""
    crawler = ConsoleCrawler(host="eu.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 1, "console_url": "https://example.com/"}
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "csrf")

    with patch.object(crawler.session, "post", return_value=mock_resp) as mock_post:
        crawler.create("testuser")

    call_args = mock_post.call_args
    assert "eu.pythonanywhere.com" in call_args[0][0]
    assert "eu.pythonanywhere.com" in call_args[1]["headers"]["Referer"]


# --- activate tests ---

FRAME_PAGE_HTML = '''<html><body>
<script type="text/javascript">
    $(function () {
        Anywhere.LoadConsole("consoles-10.pythonanywhere.com", "gt047kc6a1zfwqpyixl0k5of2858qycv", "46955916", "", false);
    });
</script>
</body></html>'''


def test_activate_connects_via_websocket():
    """activate fetches frame page, parses WebSocket info, and connects."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.text = FRAME_PAGE_HTML
    mock_resp.raise_for_status = MagicMock()

    mock_ws = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get, \
         patch("pa_cli.crawler.console_crawler.websocket") as mock_ws_mod:
        mock_ws_mod.create_connection.return_value = mock_ws
        crawler.activate("testuser", 46955916)

    mock_get.assert_called_once_with(
        "https://www.pythonanywhere.com/user/testuser/consoles/46955916/frame/"
    )
    mock_ws_mod.create_connection.assert_called_once_with(
        "wss://consoles-10.pythonanywhere.com/sj/websocket"
    )
    mock_ws.send.assert_any_call("\x1b[gt047kc6a1zfwqpyixl0k5of2858qycv;46955916;;a")
    mock_ws.send.assert_any_call("\x1b[8;24;80t")
    mock_ws.close.assert_called_once()


def test_activate_raises_on_network_error():
    """activate raises Exception on network failure when fetching frame page."""
    crawler = ConsoleCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch console frame page"):
            crawler.activate("testuser", 12345)


def test_activate_raises_on_missing_websocket_info():
    """activate raises Exception when WebSocket info cannot be parsed from frame page."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.text = "<html><body>No LoadConsole here</body></html>"
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp):
        with pytest.raises(Exception, match="Could not parse WebSocket info"):
            crawler.activate("testuser", 12345)


def test_activate_raises_on_websocket_error():
    """activate raises Exception when WebSocket connection fails."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.text = FRAME_PAGE_HTML
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp), \
         patch("pa_cli.crawler.console_crawler.websocket") as mock_ws_mod:
        mock_ws_mod.create_connection.side_effect = Exception("Connection refused")
        with pytest.raises(Exception, match="WebSocket connection failed"):
            crawler.activate("testuser", 12345)


def test_activate_closes_websocket_on_error():
    """activate closes WebSocket connection even if send fails."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.text = FRAME_PAGE_HTML
    mock_resp.raise_for_status = MagicMock()

    mock_ws = MagicMock()
    mock_ws.send.side_effect = Exception("Send failed")

    with patch.object(crawler.session, "get", return_value=mock_resp), \
         patch("pa_cli.crawler.console_crawler.websocket") as mock_ws_mod:
        mock_ws_mod.create_connection.return_value = mock_ws
        with pytest.raises(Exception, match="WebSocket connection failed"):
            crawler.activate("testuser", 46955916)

    mock_ws.close.assert_called_once()


def test_activate_uses_dynamic_host():
    """activate uses the correct base_url for custom host."""
    crawler = ConsoleCrawler(host="eu.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.text = FRAME_PAGE_HTML
    mock_resp.raise_for_status = MagicMock()

    mock_ws = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get, \
         patch("pa_cli.crawler.console_crawler.websocket") as mock_ws_mod:
        mock_ws_mod.create_connection.return_value = mock_ws
        crawler.activate("testuser", 46955916)

    mock_get.assert_called_once_with(
        "https://eu.pythonanywhere.com/user/testuser/consoles/46955916/frame/"
    )


# --- delete tests ---


def test_delete_sends_delete_request():
    """delete sends DELETE request to correct API endpoint with CSRF headers."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "test-csrf-token")

    with patch.object(crawler.session, "delete", return_value=mock_resp) as mock_delete:
        crawler.delete("testuser", 12345)

    mock_delete.assert_called_once()
    call_args = mock_delete.call_args
    assert call_args[0][0] == "https://www.pythonanywhere.com/api/v0/user/testuser/consoles/12345/"
    assert call_args[1]["headers"]["X-CSRFToken"] == "test-csrf-token"
    assert "testuser/consoles" in call_args[1]["headers"]["Referer"]


def test_delete_returns_none():
    """delete returns None on success (204 No Content)."""
    crawler = ConsoleCrawler()
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "test-csrf-token")

    with patch.object(crawler.session, "delete", return_value=mock_resp):
        result = crawler.delete("testuser", 12345)

    assert result is None


def test_delete_raises_on_missing_csrf():
    """delete raises Exception when CSRF token is missing from cookies."""
    crawler = ConsoleCrawler()

    with pytest.raises(Exception, match="CSRF token not found"):
        crawler.delete("testuser", 12345)


def test_delete_raises_on_network_error():
    """delete raises Exception on network failure."""
    crawler = ConsoleCrawler()
    crawler.session.cookies.set("csrftoken", "test-csrf-token")

    with patch.object(crawler.session, "delete", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to delete console"):
            crawler.delete("testuser", 12345)


def test_delete_uses_dynamic_host():
    """delete uses the correct base_url for custom host."""
    crawler = ConsoleCrawler(host="eu.pythonanywhere.com")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    crawler.session.cookies.set("csrftoken", "csrf")

    with patch.object(crawler.session, "delete", return_value=mock_resp) as mock_delete:
        crawler.delete("testuser", 99)

    call_args = mock_delete.call_args
    assert "eu.pythonanywhere.com" in call_args[0][0]
    assert "eu.pythonanywhere.com" in call_args[1]["headers"]["Referer"]
