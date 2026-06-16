import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from pa_cli.crawler.account_crawler import AccountCrawler
from pa_cli.exceptions import AuthError, NetworkError, APIError, NotFoundError


MOCK_CONFIG = {"username": "configuser", "token": "cfg-token-1234567890abcdef1234567890", "host": "www.pythonanywhere.com", "password": "configpass"}


@pytest.fixture(autouse=True)
def mock_config_load():
    """Patch Config.load for all tests so AccountCrawler() doesn't hit real config."""
    with patch("pa_cli.crawler.account_crawler.Config.load", return_value=MOCK_CONFIG):
        yield


REGISTER_PAGE_HTML = '<html><body><form><input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token"></form></body></html>'


def _mock_get_response(html=REGISTER_PAGE_HTML):
    resp = MagicMock()
    resp.text = html
    resp.status_code = 200
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


def test_register_raises_on_failure():
    """register raises AuthError when response stays on registration page (200 with errors)."""
    crawler = AccountCrawler()

    error_html = '<html><body><ul class="errorlist"><li>This username is already taken.</li></ul></body></html>'
    mock_resp = _mock_post_response(
        "https://www.pythonanywhere.com/registration/register/beginner/", status_code=200
    )
    mock_resp.text = error_html

    with patch.object(crawler.session, "get", return_value=_mock_get_response()), \
         patch.object(crawler.session, "post", return_value=mock_resp):

        with pytest.raises(AuthError, match="Registration failed"):
            crawler.register("baduser", "bad@example.com", "weak")


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
<div class="tab-pane" id="api_token">
    <code class="api_token">abcdef1234567890abcdef1234567890abcdef12</code>
</div>
</body></html>'''


def test_get_token_returns_token_string():
    """get_token returns the API token hex string from the account page."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)):
        token = crawler.get_token("testuser")

    assert token == "abcdef1234567890abcdef1234567890abcdef12"


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


# --- extend_expiry success tests ---

WEBAPPS_PAGE_HTML = '''<html><body>
<form action="/user/testuser/webapps/testuser.pythonanywhere.com/extend" method="post">
    <input type="hidden" name="csrfmiddlewaretoken" value="extend_expiry-csrf-token">
    <button type="submit">Extend</button>
</form>
</body></html>'''


def test_extend_expiry_returns_true_on_success():
    """extend_expiry returns True when POST to extend URL succeeds."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )):
        result = crawler.extend_expiry("testuser")

    assert result is True


def test_extend_expiry_returns_true_on_redirect():
    """extend_expiry returns True when POST returns 302 redirect."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=302
         )):
        result = crawler.extend_expiry("testuser")

    assert result is True


def test_extend_expiry_fetches_webapps_page():
    """extend_expiry GETs the correct webapps page URL."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )):
        crawler.extend_expiry("testuser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/testuser/webapps/")


def test_extend_expiry_posts_csrf_to_extend_url():
    """extend_expiry POSTs csrfmiddlewaretoken to the extend URL found in form action."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=200
         )) as mock_post:
        crawler.extend_expiry("testuser")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "extend" in call_args[0][0]
    assert call_args[1]["data"]["csrfmiddlewaretoken"] == "extend_expiry-csrf-token"


# --- extend_expiry failure tests ---


def test_extend_expiry_returns_false_on_failure():
    """extend_expiry returns False when POST returns non-success status."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/testuser/webapps/", status_code=500
         )):
        result = crawler.extend_expiry("testuser")

    assert result is False


def test_extend_expiry_raises_on_get_network_error():
    """extend_expiry raises Exception when fetching webapps page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch webapps page"):
            crawler.extend_expiry("testuser")


def test_extend_expiry_raises_when_no_extend_form():
    """extend_expiry raises Exception when no extend form is found on page."""
    crawler = AccountCrawler()
    html_without_form = '<html><body><form action="/other"></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_without_form)):
        with pytest.raises(Exception, match="Extend form not found"):
            crawler.extend_expiry("testuser")


def test_extend_expiry_raises_when_no_csrf_in_form():
    """extend_expiry raises Exception when CSRF token is not in the extend form."""
    crawler = AccountCrawler()
    html_no_csrf = '<html><body><form action="/user/testuser/webapps/test.pythonanywhere.com/extend"></form></body></html>'

    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_no_csrf)):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.extend_expiry("testuser")


def test_extend_expiry_raises_on_post_network_error():
    """extend_expiry raises Exception when POST request fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Extend request failed"):
            crawler.extend_expiry("testuser")


# --- reload_webapp success tests ---


def _mock_reload_get_response():
    """Response for the GET request that fetches the webapps page for CSRF token."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    return resp


def _mock_reload_post_response(text="OK", status_code=200):
    """Response for the POST request to reload the webapp."""
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    type(resp).status_code = PropertyMock(return_value=status_code)
    return resp


def test_reload_webapp_returns_true_on_success():
    """reload_webapp returns True when response text is 'OK'."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")):
        result = crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")

    assert result is True


def test_reload_webapp_gets_webapps_page():
    """reload_webapp GETs the webapps page to obtain CSRF token from cookies."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")):
        crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/testuser/webapps/")


def test_reload_webapp_posts_with_correct_headers():
    """reload_webapp POSTs with CSRF token, XMLHttpRequest, Referer, and Origin headers."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")) as mock_post:
        crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://www.pythonanywhere.com/user/testuser/webapps/testuser.pythonanywhere.com/reload"
    headers = call_args[1]["headers"]
    assert headers["X-CSRFToken"] == "reload-csrf-token"
    assert headers["X-Requested-With"] == "XMLHttpRequest"
    assert headers["Referer"] == "https://www.pythonanywhere.com/user/testuser/webapps/"
    assert headers["Origin"] == "https://www.pythonanywhere.com"


def test_reload_webapp_uses_custom_host():
    """reload_webapp uses the correct base_url for custom host."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")) as mock_post:
        crawler.reload_webapp("testuser.eu.pythonanywhere.com", "testuser")

    assert "eu.pythonanywhere.com" in mock_get.call_args[0][0]
    assert "eu.pythonanywhere.com" in mock_post.call_args[0][0]


# --- reload_webapp failure tests ---


def test_reload_webapp_returns_false_on_non_ok_response():
    """reload_webapp returns False when response text is not 'OK'."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("ERROR", status_code=500)):
        result = crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")

    assert result is False


def test_reload_webapp_raises_on_get_network_error():
    """reload_webapp raises Exception when fetching webapps page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch webapps page"):
            crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")


def test_reload_webapp_raises_on_missing_csrf_token():
    """reload_webapp raises Exception when CSRF token is not found in cookies."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = None

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")


def test_reload_webapp_raises_on_post_network_error():
    """reload_webapp raises Exception when POST request fails."""
    crawler = AccountCrawler()
    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Reload request failed"):
            crawler.reload_webapp("testuser.pythonanywhere.com", "testuser")


# --- get_hits success tests ---

HITS_RESPONSE_JSON = {
    "hits_current_hour": 0,
    "hits_previous_hour": 2,
    "hits_current_day": 2,
    "hits_previous_day": 0,
    "hits_current_month": 2,
    "hits_previous_month": 0,
}


def _mock_json_response(json_data, status_code=200):
    """Response for JSON API requests."""
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    type(resp).status_code = PropertyMock(return_value=status_code)
    return resp


def test_get_hits_returns_dict_on_success():
    """get_hits returns dict with hit counts when request succeeds."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)):
        result = crawler.get_hits("testuser.pythonanywhere.com", "testuser")

    assert isinstance(result, dict)
    assert result == HITS_RESPONSE_JSON


def test_get_hits_sends_correct_url():
    """get_hits GETs the correct hits_summary endpoint."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)) as mock_get:
        crawler.get_hits("testuser.pythonanywhere.com", "testuser")

    mock_get.assert_called_once_with(
        "https://www.pythonanywhere.com/user/testuser/webapps/testuser.pythonanywhere.com/hits_summary/",
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.pythonanywhere.com/user/testuser/webapps/",
        },
    )


def test_get_hits_uses_custom_host():
    """get_hits uses the correct base_url for custom host."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)) as mock_get:
        crawler.get_hits("testuser.eu.pythonanywhere.com", "testuser")

    call_args = mock_get.call_args
    assert "eu.pythonanywhere.com" in call_args[0][0]
    assert "eu.pythonanywhere.com" in call_args[1]["headers"]["Referer"]


def test_get_hits_returns_all_hit_fields():
    """get_hits returns dict containing all expected hit count fields."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)):
        result = crawler.get_hits("testuser.pythonanywhere.com", "testuser")

    assert "hits_current_hour" in result
    assert "hits_previous_hour" in result
    assert "hits_current_day" in result
    assert "hits_previous_day" in result
    assert "hits_current_month" in result
    assert "hits_previous_month" in result


# --- get_hits error handling tests ---


def test_get_hits_raises_on_network_error():
    """get_hits raises Exception when network request fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Failed to fetch hits"):
            crawler.get_hits("testuser.pythonanywhere.com", "testuser")


def test_get_hits_raises_on_http_error():
    """get_hits raises Exception when HTTP response indicates error."""
    crawler = AccountCrawler()

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

    with patch.object(crawler.session, "get", return_value=mock_resp):
        with pytest.raises(Exception, match="Failed to fetch hits"):
            crawler.get_hits("testuser.pythonanywhere.com", "testuser")


# --- constructor config integration tests ---


def test_init_reads_username_from_config():
    """AccountCrawler reads username from Config when no username parameter given."""
    crawler = AccountCrawler()
    assert crawler.username == "configuser"


def test_init_explicit_username_overrides_config():
    """Explicit username parameter overrides config value."""
    crawler = AccountCrawler(username="explicituser")
    assert crawler.username == "explicituser"


def test_init_raises_when_no_config_and_no_username():
    """AccountCrawler raises when config not found and no username given."""
    # Override the autouse fixture for this test
    with patch("pa_cli.crawler.account_crawler.Config.load", side_effect=FileNotFoundError("Config not found. Run 'pa init' first.")):
        with pytest.raises(FileNotFoundError, match="Config not found"):
            AccountCrawler()


def test_init_uses_host_from_config():
    """AccountCrawler reads host from Config when not explicitly provided."""
    crawler = AccountCrawler()
    assert crawler.base_url == "https://www.pythonanywhere.com"


def test_init_explicit_host_overrides_config():
    """Explicit host parameter overrides config value."""
    crawler = AccountCrawler(host="eu.pythonanywhere.com")
    assert crawler.base_url == "https://eu.pythonanywhere.com"


# --- login method tests ---


LOGIN_PAGE_HTML = '<html><body><form><input type="hidden" name="csrfmiddlewaretoken" value="login-csrf-token"></form></body></html>'


def test_login_reads_password_from_config():
    """login reads password from Config when no password parameter given."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(LOGIN_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/"
         )):
        result = crawler.login()

    assert result is True


def test_login_uses_explicit_password():
    """login uses explicit password parameter over config value."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(LOGIN_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/"
         )) as mock_post:
        result = crawler.login(password="explicitpass")

    assert result is True
    posted_data = mock_post.call_args[1]["data"]
    assert posted_data["auth-password"] == "explicitpass"


def test_login_raises_when_no_password_in_config():
    """login raises AuthError when config has no password and no password param given."""
    config_no_pw = {"username": "configuser", "token": "abc", "host": "www.pythonanywhere.com"}
    with patch("pa_cli.crawler.account_crawler.Config.load", return_value=config_no_pw):
        crawler = AccountCrawler()
        with pytest.raises(AuthError, match="Password not found"):
            crawler.login()


def test_login_posts_to_login_url():
    """login POSTs credentials to the correct login URL."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(LOGIN_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/"
         )) as mock_post:
        crawler.login()

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://www.pythonanywhere.com/login/"
    posted_data = call_args[1]["data"]
    assert posted_data["auth-username"] == "configuser"
    assert posted_data["auth-password"] == "configpass"
    assert posted_data["login_view-current_step"] == "auth"


def test_login_raises_on_wrong_password():
    """login raises AuthError when password is incorrect."""
    crawler = AccountCrawler()

    error_html = '<html><body><p>The user name or password is incorrect. Please try again.</p></body></html>'
    mock_resp = _mock_post_response("https://www.pythonanywhere.com/login/", status_code=200)
    mock_resp.text = error_html

    with patch.object(crawler.session, "get", return_value=_mock_get_response(LOGIN_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=mock_resp):
        with pytest.raises(AuthError, match="incorrect"):
            crawler.login()


def test_login_raises_on_get_network_error():
    """login raises NetworkError when fetching login page fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(NetworkError, match="Failed to fetch login page"):
            crawler.login()


def test_login_raises_on_post_network_error():
    """login raises Exception when POST request fails."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(LOGIN_PAGE_HTML)), \
         patch.object(crawler.session, "post", side_effect=requests.ConnectionError("timeout")):
        with pytest.raises(Exception, match="Login request failed"):
            crawler.login()


def test_login_raises_on_missing_csrf():
    """login raises Exception when CSRF token not found on login page."""
    crawler = AccountCrawler()

    html_no_csrf = '<html><body><form></form></body></html>'
    with patch.object(crawler.session, "get", return_value=_mock_get_response(html_no_csrf)):
        with pytest.raises(Exception, match="CSRF token not found"):
            crawler.login()


# --- get_token with config-based username ---


def test_get_token_uses_self_username_when_no_param():
    """get_token uses self.username when no username parameter given."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)) as mock_get:
        token = crawler.get_token()

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/configuser/account/")
    assert token == "abcdef1234567890abcdef1234567890abcdef12"


def test_get_token_explicit_username_overrides_self():
    """get_token uses explicit username parameter over self.username."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(ACCOUNT_PAGE_HTML)) as mock_get:
        crawler.get_token("otheruser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/otheruser/account/")


# --- extend_expiry with config-based username ---


def test_extend_expiry_uses_self_username_when_no_param():
    """extend_expiry uses self.username when no username parameter given."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/webapps/", status_code=200
         )):
        result = crawler.extend_expiry()

    assert result is True


def test_extend_expiry_explicit_username_overrides_self():
    """extend_expiry uses explicit username parameter over self.username."""
    crawler = AccountCrawler()

    other_html = '''<html><body>
    <form action="/user/otheruser/webapps/otheruser.pythonanywhere.com/extend" method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value="extend-csrf">
        <button type="submit">Extend</button>
    </form>
    </body></html>'''

    with patch.object(crawler.session, "get", return_value=_mock_get_response(other_html)) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/otheruser/webapps/", status_code=200
         )):
        crawler.extend_expiry("otheruser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/otheruser/webapps/")


# --- reload_webapp with config-based username ---


def test_reload_webapp_uses_self_username_when_no_param():
    """reload_webapp uses self.username when no username parameter given."""
    crawler = AccountCrawler()

    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()), \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")) as mock_post:
        result = crawler.reload_webapp("configuser.pythonanywhere.com")

    assert result is True
    assert "configuser" in mock_post.call_args[0][0]


def test_reload_webapp_explicit_username_overrides_self():
    """reload_webapp uses explicit username parameter over self.username."""
    crawler = AccountCrawler()

    mock_cookies = MagicMock()
    mock_cookies.get.return_value = "reload-csrf-token"

    with patch.object(crawler.session, "cookies", mock_cookies), \
         patch.object(crawler.session, "get", return_value=_mock_reload_get_response()) as mock_get, \
         patch.object(crawler.session, "post", return_value=_mock_reload_post_response("OK")):
        crawler.reload_webapp("otheruser.pythonanywhere.com", "otheruser")

    mock_get.assert_called_once_with("https://www.pythonanywhere.com/user/otheruser/webapps/")


# --- get_hits with config-based username ---


def test_get_hits_uses_self_username_when_no_param():
    """get_hits uses self.username when no username parameter given."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)) as mock_get:
        result = crawler.get_hits("configuser.pythonanywhere.com")

    assert result == HITS_RESPONSE_JSON
    assert "configuser" in mock_get.call_args[0][0]


def test_get_hits_explicit_username_overrides_self():
    """get_hits uses explicit username parameter over self.username."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_json_response(HITS_RESPONSE_JSON)) as mock_get:
        crawler.get_hits("otheruser.pythonanywhere.com", "otheruser")

    assert "otheruser" in mock_get.call_args[0][0]


# --- enable_webapp / disable_webapp tests ---

WEBAPPS_PAGE_WITH_DISABLE_FORM = """
<html>
<body>
<form action="/user/configuser/webapps/configuser.pythonanywhere.com/disable" method="POST">
    <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
</form>
</body>
</html>
"""

WEBAPPS_PAGE_WITH_ENABLE_FORM = """
<html>
<body>
<form action="/user/configuser/webapps/configuser.pythonanywhere.com/enable" method="POST">
    <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
</form>
</body>
</html>
"""


def test_disable_webapp():
    """disable_webapp sends POST to disable form action."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_WITH_DISABLE_FORM)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/webapps/"
         )) as mock_post:
        result = crawler.disable_webapp("configuser.pythonanywhere.com")

    assert result is True
    mock_post.assert_called_once()
    assert "disable" in mock_post.call_args[0][0]


def test_enable_webapp():
    """enable_webapp sends POST to enable form action."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_WITH_ENABLE_FORM)), \
         patch.object(crawler.session, "post", return_value=_mock_post_response(
             "https://www.pythonanywhere.com/user/configuser/webapps/"
         )) as mock_post:
        result = crawler.enable_webapp("configuser.pythonanywhere.com")

    assert result is True
    mock_post.assert_called_once()
    assert "enable" in mock_post.call_args[0][0]


def test_disable_webapp_raises_when_already_disabled():
    """disable_webapp raises NotFoundError when disable form not found."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_WITH_ENABLE_FORM)):
        with pytest.raises(NotFoundError, match="Disable form not found"):
            crawler.disable_webapp("configuser.pythonanywhere.com")


def test_enable_webapp_raises_when_already_enabled():
    """enable_webapp raises NotFoundError when enable form not found."""
    crawler = AccountCrawler()

    with patch.object(crawler.session, "get", return_value=_mock_get_response(WEBAPPS_PAGE_HTML)):
        with pytest.raises(NotFoundError, match="Enable form not found"):
            crawler.enable_webapp("configuser.pythonanywhere.com")
