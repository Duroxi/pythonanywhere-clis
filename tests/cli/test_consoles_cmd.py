from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.consoles_cmd import app
from pa_cli.exceptions import AuthError, NetworkError

runner = CliRunner()


def test_console_list():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_client.list.return_value = [
            {"id": 1, "name": "bash"},
            {"id": 2, "name": "python3.10"},
        ]
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "ID: 1, Name: bash" in result.output
    assert "ID: 2, Name: python3.10" in result.output


def test_console_list_empty():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_client.list.return_value = []
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No consoles found." in result.output


def test_console_activate_no_password():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}

        result = runner.invoke(app, ["activate", "42"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


def test_console_activate_success():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.crawler.console_crawler.ConsoleCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h", "password": "p"}
        mock_crawler = MagicMock()
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["activate", "42"])

    assert result.exit_code == 0
    assert "Console 42 activated successfully." in result.output
    mock_crawler.login.assert_called_once_with("u", "p")
    mock_crawler.activate.assert_called_once_with("u", 42)


def test_console_activate_error():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.crawler.console_crawler.ConsoleCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h", "password": "p"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["activate", "42"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_console_create():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_client.create.return_value = {"id": 42, "executable": "bash"}
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["create"])

    assert result.exit_code == 0
    assert "42" in result.output


def test_console_send_no_wait():
    """send with --no-wait sends input and returns immediately."""
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["send", "42", "ls", "--no-wait"])

    assert result.exit_code == 0
    assert "Sent to console 42: ls" in result.output
    mock_client.send_input.assert_called_once_with("u", 42, "ls\n")


def test_console_send_with_output():
    """send waits for marker and extracts output before it."""
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls, \
         patch("pa_cli.cli.consoles_cmd.time.sleep"), \
         patch("pa_cli.cli.consoles_cmd.uuid.uuid4") as mock_uuid, \
         patch("pa_cli.cli.consoles_cmd.time.time", return_value=1234567890):
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_uuid.return_value = MagicMock(hex="abc123456789")

        # First call: baseline (empty), second call: output with marker
        marker = "__PA_CLI_DONE_1234567890_abc123456789__"
        mock_client.get_output.side_effect = [
            {"output": ""},  # baseline
            {"output": f"$ ls\nfile1.txt\nfile2.txt\n{marker}\n$ "},  # result
        ]

        result = runner.invoke(app, ["send", "42", "ls"])

    assert result.exit_code == 0
    assert "file1.txt" in result.output
    assert "file2.txt" in result.output
    assert "PA_CLI_DONE" not in result.output


def test_console_send_timeout():
    """send exits with error when timeout reached without marker."""
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls, \
         patch("pa_cli.cli.consoles_cmd.time.sleep"):
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        # Always return output without marker
        mock_client.get_output.return_value = {"output": "$ still running...\n"}

        result = runner.invoke(app, ["send", "42", "sleep 10", "--timeout", "2"])

    assert result.exit_code == 1
    assert "Timeout" in result.output


def test_console_kill():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        result = runner.invoke(app, ["kill", "42"])

    assert result.exit_code == 0


def test_console_get_or_create_no_password():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}

        result = runner.invoke(app, ["get-or-create"])

    assert result.exit_code == 1
    assert "Password not found" in result.output


def test_console_get_or_create_success():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.crawler.console_crawler.ConsoleCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h", "password": "p"}
        mock_crawler = MagicMock()
        mock_crawler.get_or_create.return_value = 42
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["get-or-create"])

    assert result.exit_code == 0
    assert "Console ready: 42" in result.output
    mock_crawler.login.assert_called_once_with("u", "p")
    mock_crawler.get_or_create.assert_called_once_with("u", executable="bash")


def test_console_get_or_create_custom_executable():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.crawler.console_crawler.ConsoleCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h", "password": "p"}
        mock_crawler = MagicMock()
        mock_crawler.get_or_create.return_value = 7
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["get-or-create", "-e", "python3.10"])

    assert result.exit_code == 0
    assert "Console ready: 7" in result.output
    mock_crawler.get_or_create.assert_called_once_with("u", executable="python3.10")


def test_console_get_or_create_error():
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.crawler.console_crawler.ConsoleCrawler") as mock_cls:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h", "password": "p"}
        mock_crawler = MagicMock()
        mock_crawler.login.side_effect = AuthError("Login failed")
        mock_cls.return_value = mock_crawler

        result = runner.invoke(app, ["get-or-create"])

    assert result.exit_code == 1
    assert "Login failed" in result.output


def test_console_send_wait_default():
    """console send waits for output by default."""
    with patch("pa_cli.cli.consoles_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.consoles_cmd.ConsolesClient") as mock_cls, \
         patch("pa_cli.cli.consoles_cmd.time.sleep"), \
         patch("pa_cli.cli.consoles_cmd.uuid.uuid4") as mock_uuid, \
         patch("pa_cli.cli.consoles_cmd.time.time", return_value=1234567890):
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_uuid.return_value = MagicMock(hex="abc123456789")

        marker = "__PA_CLI_DONE_1234567890_abc123456789__"
        mock_client.get_output.side_effect = [
            {"output": ""},  # baseline
            {"output": f"$ echo hello\nhello\n{marker}\n$ "},  # result
        ]

        result = runner.invoke(app, ["send", "42", "echo hello"])

    assert result.exit_code == 0
    assert "hello" in result.output


