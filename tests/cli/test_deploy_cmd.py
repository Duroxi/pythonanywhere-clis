from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.deploy_cmd import app
from pa_cli.exceptions import PACliError, NetworkError, APIError

runner = CliRunner()


def test_deploy_command():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = "https://u.pythonanywhere.com"

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 0
    assert "u.pythonanywhere.com" in result.output


def test_deploy_with_custom_domain():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = "https://custom.example.com"

        result = runner.invoke(app, ["./mysite", "--domain", "custom.example.com"])

    assert result.exit_code == 0
    mock_deploy.assert_called_once()
    call_kwargs = mock_deploy.call_args[1]
    assert call_kwargs["domain"] == "custom.example.com"


def test_deploy_with_python_version():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = "https://u.pythonanywhere.com"

        result = runner.invoke(app, ["./mysite", "--python", "python311"])

    assert result.exit_code == 0
    mock_deploy.assert_called_once()
    call_kwargs = mock_deploy.call_args[1]
    assert call_kwargs["python_version"] == "python311"


def test_deploy_dry_run():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = ""

        result = runner.invoke(app, ["./mysite", "--dry-run"])

    assert result.exit_code == 0
    mock_deploy.assert_called_once()
    call_kwargs = mock_deploy.call_args[1]
    assert call_kwargs["dry_run"] is True
    # dry-run should not show "Deployed!" message
    assert "Deployed" not in result.output


def test_deploy_handles_paclier_error():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.side_effect = PACliError("Deploy failed")

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 1
    assert "Deploy failed" in result.output


def test_deploy_handles_network_error():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.side_effect = NetworkError("Connection failed")

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 1
    # NetworkError is caught by PACliError handler since NetworkError inherits from PACliError
    assert "Deploy failed" in result.output


def test_deploy_handles_api_error():
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.side_effect = APIError("API error 500")

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 1
    assert "API error" in result.output
