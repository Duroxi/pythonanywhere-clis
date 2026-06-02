from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.register_cmd import app

runner = CliRunner()


def test_register_success():
    """register command succeeds when AccountCrawler.register returns True."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.register.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(
            app, [], input="newuser\nnew@example.com\nsecret123\nsecret123\n"
        )

    assert result.exit_code == 0
    mock_crawler.register.assert_called_once_with("newuser", "new@example.com", "secret123")
    assert "registered successfully" in result.output
    assert "check your email" in result.output
    assert "pa init" in result.output


def test_register_password_mismatch():
    """register command exits with error when passwords do not match."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        result = runner.invoke(
            app, [], input="newuser\nnew@example.com\nsecret123\ndifferent456\n"
        )

    assert result.exit_code == 1
    assert "Passwords do not match" in result.output
    mock_cls.return_value.register.assert_not_called()


def test_register_failure():
    """register command exits with error when AccountCrawler.register returns False."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.register.return_value = False
        mock_cls.return_value = mock_crawler

        result = runner.invoke(
            app, [], input="baduser\nbad@example.com\nweak\nweak\n"
        )

    assert result.exit_code == 1
    assert "Registration failed" in result.output


def test_register_exception():
    """register command exits with error when AccountCrawler raises exception."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.register.side_effect = Exception("Network error")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(
            app, [], input="newuser\nnew@example.com\nsecret123\nsecret123\n"
        )

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_register_prompts_hidden_password():
    """register command uses hidden input for password prompts."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.register.return_value = True
        mock_cls.return_value = mock_crawler

        with patch("pa_cli.cli.register_cmd.typer") as mock_typer:
            mock_typer.prompt.side_effect = ["newuser", "new@example.com", "secret123", "secret123"]
            mock_typer.echo = MagicMock()
            from pa_cli.cli.register_cmd import register

            register()

    calls = mock_typer.prompt.call_args_list
    assert calls[2] == (("Password",), {"hide_input": True})
    assert calls[3] == (("Confirm password",), {"hide_input": True})


def test_register_passes_correct_args_to_crawler():
    """register command passes username, email, and password to AccountCrawler.register."""
    with patch("pa_cli.cli.register_cmd.AccountCrawler") as mock_cls:
        mock_crawler = MagicMock()
        mock_crawler.register.return_value = True
        mock_cls.return_value = mock_crawler

        result = runner.invoke(
            app, [], input="testuser\ntest@email.com\nmypassword\nmypassword\n"
        )

    assert result.exit_code == 0
    mock_crawler.register.assert_called_once_with("testuser", "test@email.com", "mypassword")
