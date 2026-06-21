import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.deploy_cmd import app
from pa_cli.exceptions import PACliError, NetworkError, APIError

runner = CliRunner()


def test_deploy_command():
    """deploy creates deployment successfully."""
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = "https://u.pythonanywhere.com"

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 0
    assert "u.pythonanywhere.com" in result.output


def test_deploy_with_custom_domain():
    """deploy passes custom domain to workflow."""
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
    """deploy passes python version to workflow."""
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
    """deploy --dry-run passes dry_run=True to workflow."""
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = ""

        result = runner.invoke(app, ["./mysite", "--dry-run"])

    assert result.exit_code == 0
    mock_deploy.assert_called_once()
    call_kwargs = mock_deploy.call_args[1]
    assert call_kwargs["dry_run"] is True
    assert "Deployed" not in result.output


def test_deploy_default_domain():
    """deploy uses default domain when not specified."""
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.return_value = "https://u.pythonanywhere.com"

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 0
    mock_deploy.assert_called_once()
    call_kwargs = mock_deploy.call_args[1]
    assert call_kwargs["domain"] == "u.pythonanywhere.com"


@pytest.mark.parametrize("error_class,expected_msg", [
    (NetworkError, "Network error"),
    (APIError, "API error"),
    (PACliError, "Deploy failed"),
])
def test_deploy_handles_errors(error_class, expected_msg):
    """deploy shows appropriate error message for different error types."""
    with patch("pa_cli.cli.deploy_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.deploy_cmd.deploy_workflow") as mock_deploy:
        mock_load.return_value = {"username": "u", "token": "t", "host": "h"}
        mock_deploy.side_effect = error_class("Test error")

        result = runner.invoke(app, ["./mysite"])

    assert result.exit_code == 1
    assert expected_msg in result.output
