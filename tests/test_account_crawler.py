import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from pa_cli.crawler.account_crawler import AccountCrawler


REGISTER_PAGE_HTML = '<html><body><form><input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token"></form></body></html>'


def _mock_get_response(html=REGISTER_PAGE_HTML):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def _mock_post_response(url, status_code=302):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    type(resp).url = PropertyMock(return_value=url)
    type(resp).status_code = PropertyMock(return_value=status_code)
    return resp


# --- constructor tests ---


def test_default_host():
    """AccountCrawler defaults to www.pythonanywhere.com."""
    crawler = AccountCrawler()
    assert crawler.base_url == "https://www.pythonanywhere.com"


def test_custom_host():
    """AccountCrawler accepts custom host parameter."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")
    assert crawler.base_url == "https://eu.pythonanywhere.com"


def test_uses_session():
    """AccountCrawler uses requests.Session for cookie management."""
    crawler = AccountCrawler()
    assert isinstance(crawler.session, requests.Session)


def test_sets_user_agent():
    """AccountCrawler sets User-Agent header on the session."""
    crawler = AccountCrawler()
    assert "User-Agent" in crawler.session.headers


# --- register success tests ---


def test_register_success_returns_true():
    """register returns True when response is 302 redirect to /registration/register/complete/."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/registration/register/complete/"
         )) as mock_post:

        result = crawler.register("testuser", "test@example.com", "securepass123")

    assert result is True


def test_register_fetches_csrf_from_register_page():
    """register GETs the registration page to obtain CSRF token."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/registration/register/complete/"
         )):

        crawler.register("testuser", "test@example.com", "securepass123")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/registration/register/beginner/")


def test_register_posts_correct_form_data():
    """register POSTs csrfmiddlewaretoken, username, email, password1, password2, tos, and recaptcha fields."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/registration/register/complete/"
         )) as mock_post:

        crawler.register("testuser", "test@example.com", "securepass123")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://www.pythonanywhere.com/registration/register/beginner/"

    posted_data = call_args[1]["data"]
    assert posted_data["csrfmiddlewaretoken"] == "test-csrf-token"
    assert posted_data["username"] == "testuser"
    assert posted_data["email"] == "test@example.com"
    assert posted_data["password1"] == "securepass123"
    assert posted_data["password2"] == "securepass123"
    assert posted_data["tos"] == "on"
    assert posted_data["recaptcha_response_token_v3"] == ""


# --- register failure tests ---


def test_register_failure_returns_false():
    """register returns False when response stays on registration page (200 with errors)."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/registration/register/beginner/", status_code=200
         )):

        result = crawler.register("baduser", "bad@example.com", "weak")

    assert result is False


# --- register error handling tests ---


def test_register_raises_on_get_network_error():
    """register raises Exception when fetching registration page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch registration page"):
            crawler.register("testuser", "test@example.com", "securepass123")


def test_register_raises_on_post_network_error():
    """register raises Exception when POST request fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Registration request failed"):
            crawler.register("testuser", "test@example.com", "securepass123")


def test_register_raises_on_missing_csrf():
    """register raises Exception when CSRF token is not found on page."""
    crawler = AccountCrawler()
    html_without_csrf = '<html><body><form></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_without_csrf)):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.register("testuser", "test@example.com", "securepass123")


# --- register dynamic host tests ---


def test_register_uses_custom_host():
    """register uses the correct base_url for custom host."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")

    with patch.object(crawler.session, "get", return_value=_mock_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://eu.pythonanywhere.com/registration/register/complete/"
         )) as mock_post:

        crawler.register("testuser", "test@example.com", "securepass123")

    get_url = mock_get.call_args[0][0]
    post_url = mock_post.call_args[0][0]
    assert "eu.pythonanywhere.com" in get_url
    assert "eu.pythonanywhere.com" in post_url


# --- get_token success tests ---

ACCOUNT_PAGE_HTML = '''<html><body>
<form>
    <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf">
    <label>API token</label>
    <input type="text" name="api_token" value="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890">
</form>
</body></html>'''


def test_get_token_returns_token_string():
    """get_token returns the API token hex string from the account page."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)):
        token = crawler.get_token("testuser")

    assert token == "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"


def test_get_token_fetches_account_page():
    """get_token GETs the correct account page URL."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)) as mock_get:
        crawler.get_token("testuser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/testuser/account/")


def test_get_token_uses_custom_host():
    """get_token uses the correct base_url for custom host."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)) as mock_get:
        crawler.get_token("testuser")

    assert "eu.pythonanywhere.com" in mock_get.call_args[0][0]


# --- get_token failure tests ---


def test_get_token_raises_on_network_error():
    """get_token raises Exception when fetching account page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch account page"):
            crawler.get_token("testuser")


def test_get_token_raises_when_token_not_found():
    """get_token raises Exception when no token input is found on page."""
    crawler = AccountCrawler()
    html_without_token = '<html><body><form></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_without_token)):
        with pytest.raises(Exception, match="API token not found"):
            crawler.get_token("testuser")


# --- refresh success tests ---

WEBAPPS_PAGE_HTML = '''<html><body>
<form action="/user/testuser/webapps/testuser.pythonanywhere.com/extend" method="post">
    <input type="hidden" name="csrfmiddlewaretoken" value="refresh-csrf-token">
    <button type="submit">Extend</button>
</form>
</body></html>'''


def test_refresh_returns_true_on_success():
    """refresh returns True when POST to extend URL succeeds."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )):
        result = crawler.refresh("testuser")

    assert result is True


def test_refresh_returns_true_on_redirect():
    """refresh returns True when POST returns 302 redirect."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=302
         )):
        result = crawler.refresh("testuser")

    assert result is True


def test_refresh_fetches_webapps_page():
    """refresh GETs the correct webapps page URL."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )):
        crawler.refresh("testuser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/testuser/webapps/")


def test_refresh_posts_csrf_to_extend_url():
    """refresh POSTs csrfmiddlewaretoken to the extend URL found in form action."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )) as mock_post:
        crawler.refresh("testuser")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "extend" in call_args[0][0]
    assert call_args[1]["data"]["csrfmiddlewaretoken"] == "refresh-csrf-token"


# --- refresh failure tests ---


def test_refresh_returns_false_on_failure():
    """refresh returns False when POST returns non-success status."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=500
         )):
        result = crawler.refresh("testuser")

    assert result is False


def test_refresh_raises_on_get_network_error():
    """refresh raises Exception when fetching webapps page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch webapps page"):
            crawler.refresh("testuser")


def test_refresh_raises_when_no_extend_form():
    """refresh raises Exception when no extend form is found on page."""
    crawler = AccountCrawler()
    html_without_form = '<html><body><form action="/other"></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_without_form)):
        with pytest.raises(Exception, match="Extend form not found"):
            crawler.refresh("testuser")


def test_refresh_raises_when_no_csrf_in_form():
    """refresh raises Exception when CSRF token is not in the extend form."""
    crawler = AccountCrawler()
    html_no_csrf = '<html><body><form action="/user/testuser/webapps/test.pythonanywhere.com/extend"></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_no_csrf)):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.refresh("testuser")


def test_refresh_raises_on_post_network_error():
    """refresh raises Exception when POST request fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Extend request failed"):
            crawler.refresh("testuser")
