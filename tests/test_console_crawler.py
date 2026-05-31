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
