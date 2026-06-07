from unittest.mock import patch, MagicMock, call
from typer.testing import CliRunner

from pa_cli.cli.init_cmd import app

runner = CliRunner()


def test_init_prompts_username_and_password(tmp_path):
    """init prompts for username and password, not token."""
    with patch("pa_cli.cli.init_cmd.Config.save") as mock_save, \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "test-token-1234"
        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert result.exit_code == 0
    # Should save username, password, host first
    mock_save.assert_any_call(username="testuser", password="secret123", host="www.pythonanywhere.com")


def test_init_auto_fetches_token_on_login_success(tmp_path):
    """init calls AccountCrawler.login() and get_token() to auto-fetch token."""
    with patch("pa_cli.cli.init_cmd.Config.save") as mock_save, \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "auto-fetched-token-abcdef"

        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert result.exit_code == 0
    # Should call login and get_token
    mock_crawler.login.assert_called_once()
    mock_crawler.get_token.assert_called_once()
    # Should save the auto-fetched token
    mock_save.assert_any_call(token="auto-fetched-token-abcdef")


def test_init_shows_success_message_with_token(tmp_path):
    """init shows success message indicating token was fetched."""
    with patch("pa_cli.cli.init_cmd.Config.save"), \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "token-xyz"

        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert result.exit_code == 0
    assert "configured successfully" in result.output
    assert "token" in result.output.lower()


def test_init_login_failure_shows_error(tmp_path):
    """init shows error when login fails."""
    with patch("pa_cli.cli.init_cmd.Config.save"), \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.side_effect = ValueError("Login failed: The user name or password is incorrect.")

        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_init_login_exception_shows_error(tmp_path):
    """init shows error when login raises exception."""
    with patch("pa_cli.cli.init_cmd.Config.save"), \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.side_effect = Exception("Network error")

        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_init_saves_config_before_login(tmp_path):
    """init saves username/password/host to config before attempting login."""
    call_order = []
    with patch("pa_cli.cli.init_cmd.Config.save") as mock_save, \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_save.side_effect = lambda **kwargs: call_order.append(("save", kwargs))
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.side_effect = lambda: call_order.append("login") or True
        mock_crawler.get_token.return_value = "token"

        runner.invoke(app, input="testuser\nsecret123\n\n")

    # Config.save must be called before login
    assert call_order[0][0] == "save"
    assert call_order[1] == "login"


def test_init_uses_custom_host(tmp_path):
    """init passes custom host to Config.save."""
    with patch("pa_cli.cli.init_cmd.Config.save") as mock_save, \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "token"

        result = runner.invoke(app, input="testuser\nsecret123\neu.pythonanywhere.com\n")

    assert result.exit_code == 0
    mock_save.assert_any_call(username="testuser", password="secret123", host="eu.pythonanywhere.com")


def test_init_no_token_prompt_in_input(tmp_path):
    """init does not prompt for API token."""
    with patch("pa_cli.cli.init_cmd.Config.save"), \
         patch("pa_cli.cli.init_cmd.AccountCrawler") as MockCrawler:
        mock_crawler = MockCrawler.return_value
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "token"

        result = runner.invoke(app, input="testuser\nsecret123\n\n")

    assert "API Token" not in result.output
