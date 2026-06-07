from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.account_cmd import app

runner = CliRunner()


def test_login_prompts_for_password():
    with patch("pa_cli.cli.account_cmd.Config.save") as mock_save:
        result = runner.invoke(app, ["login"], input="secret\n")

    assert result.exit_code == 0
    mock_save.assert_called_once_with(password="secret")
    assert "Password saved" in result.output


def test_login_uses_hidden_input():
    with patch("pa_cli.cli.account_cmd.Config.save"):
        with patch("pa_cli.cli.account_cmd.typer") as mock_typer:
            mock_typer.prompt.return_value = "secret"
            mock_typer.echo = MagicMock()
            from pa_cli.cli.account_cmd import login
            login()

    mock_typer.prompt.assert_called_once_with("Password", hide_input=True)


# --- token command tests ---


def test_token_command_shows_existing_token():
    """token command shows existing token and saves it."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_token.return_value = "abc123token"
        mock_cls.return_value = mock_crawler

        with patch("pa_cli.cli.account_cmd.Config.save") as mock_save:
            result = runner.invoke(app, ["token"])

    assert result.exit_code == 0
    mock_crawler.get_token.assert_called_once()
    mock_save.assert_called_once_with(token="abc123token")
    assert "abc123token" in result.output


def test_token_command_creates_token_when_none_exists():
    """token command auto-creates token when get_token fails."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.get_token.side_effect = Exception("API token not found")
        mock_crawler.create_token.return_value = "newtoken456"
        mock_cls.return_value = mock_crawler

        with patch("pa_cli.cli.account_cmd.Config.save") as mock_save:
            result = runner.invoke(app, ["token"])

    assert result.exit_code == 0
    mock_crawler.create_token.assert_called_once()
    mock_save.assert_called_once_with(token="newtoken456")
    assert "newtoken456" in result.output


def test_token_command_revoke_creates_new_token():
    """token command with --revoke forces token creation."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.create_token.return_value = "revoked_new_token"
        mock_cls.return_value = mock_crawler

        with patch("pa_cli.cli.account_cmd.Config.save") as mock_save:
            result = runner.invoke(app, ["token", "--revoke"])

    assert result.exit_code == 0
    mock_crawler.create_token.assert_called_once()
    mock_save.assert_called_once_with(token="revoked_new_token")
    assert "revoked_new_token" in result.output


def test_token_command_exits_on_login_failure():
    """token command exits with error when login raises."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = ValueError("Login failed: The user name or password is incorrect.")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["token"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_token_command_exits_on_login_exception():
    """token command exits with error when login raises exception."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = ValueError("Password not found in config")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["token"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


# --- extend command tests ---


def test_extend_command_logs_in_and_extends():
    """extend command creates crawler, logs in, and extends account expiry."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.extend_expiry.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["extend"])

    assert result.exit_code == 0
    mock_crawler.login.assert_called_once()
    mock_crawler.extend_expiry.assert_called_once()
    assert "extended" in result.output.lower()


def test_extend_command_exits_on_login_failure():
    """extend command exits with error when login raises."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = ValueError("Login failed: The user name or password is incorrect.")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["extend"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_extend_command_exits_on_extend_failure():
    """extend command exits with error when extend_expiry returns False."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.return_value = True
        mock_crawler.extend_expiry.return_value = False
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["extend"])

    assert result.exit_code == 1
    assert "Failed to extend" in result.output


def test_extend_command_exits_on_login_exception():
    """extend command exits with error when login raises exception."""
    with patch("pa_cli.cli.account_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = ValueError("Password not found in config")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["extend"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


# --- list command tests ---


def test_list_command_shows_all_accounts():
    """list command shows all accounts and marks default."""
    with patch("pa_cli.cli.account_cmd.Config.list_accounts") as mock_list:
        mock_list.return_value = [
            {"username": "user1", "token": "abc123def", "host": "www.pythonanywhere.com"},
            {"username": "user2", "token": "xyz789ghi", "host": "eu.pythonanywhere.com"},
        ]
        with patch("pa_cli.cli.account_cmd.Config.load") as mock_load:
            mock_load.return_value = {"username": "user1", "token": "t", "host": "h"}
            result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "* user1" in result.output
    assert "user2" in result.output
    assert "abc123de" in result.output  # first 8 chars of token


def test_list_command_shows_no_token_warning():
    """list command shows '(no token)' when token is empty."""
    with patch("pa_cli.cli.account_cmd.Config.list_accounts") as mock_list:
        mock_list.return_value = [
            {"username": "user1", "token": "", "host": "www.pythonanywhere.com"},
        ]
        with patch("pa_cli.cli.account_cmd.Config.load") as mock_load:
            mock_load.return_value = {"username": "user1", "token": "", "host": "h"}
            result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "(no token)" in result.output


def test_list_command_empty():
    """list command shows message when no accounts configured."""
    with patch("pa_cli.cli.account_cmd.Config.list_accounts") as mock_list:
        mock_list.return_value = []
        with patch("pa_cli.cli.account_cmd.Config.load") as mock_load:
            mock_load.side_effect = ValueError("No default account configured.")
            result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No accounts configured" in result.output


# --- switch command tests ---


def test_switch_command_changes_default():
    """switch command changes default account."""
    with patch("pa_cli.cli.account_cmd.Config.set_default") as mock_set:
        result = runner.invoke(app, ["switch", "user2"])

    assert result.exit_code == 0
    mock_set.assert_called_once_with("user2")
    assert "Switched to account 'user2'" in result.output


def test_switch_command_exits_on_nonexistent_user():
    """switch command exits with error when account not found."""
    with patch("pa_cli.cli.account_cmd.Config.set_default") as mock_set:
        mock_set.side_effect = ValueError("Account 'nobody' not found in config.")
        result = runner.invoke(app, ["switch", "nobody"])

    assert result.exit_code == 1
    assert "nobody" in result.output


# --- remove command tests ---


def test_remove_command_deletes_account():
    """remove command deletes the specified account."""
    with patch("pa_cli.cli.account_cmd.Config.remove") as mock_remove:
        mock_remove.return_value = None
        result = runner.invoke(app, ["remove", "user2"])

    assert result.exit_code == 0
    mock_remove.assert_called_once_with("user2")
    assert "Removed account 'user2'" in result.output


def test_remove_command_shows_new_default_when_removing_current():
    """remove command shows new default when removing the current default account."""
    with patch("pa_cli.cli.account_cmd.Config.remove") as mock_remove:
        mock_remove.return_value = "user1"
        result = runner.invoke(app, ["remove", "user2"])

    assert result.exit_code == 0
    assert "Switched to account 'user1'" in result.output


def test_remove_command_exits_on_nonexistent_user():
    """remove command exits with error when account not found."""
    with patch("pa_cli.cli.account_cmd.Config.remove") as mock_remove:
        mock_remove.side_effect = ValueError("Account 'nobody' not found in config.")
        result = runner.invoke(app, ["remove", "nobody"])

    assert result.exit_code == 1
    assert "nobody" in result.output
