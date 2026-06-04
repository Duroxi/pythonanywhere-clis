from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.files_cmd import app

runner = CliRunner()


def test_upload_single_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_client.upload.return_value = 201
        mock_client_cls.return_value = mock_client

        result = runner.invoke(app, ["upload", str(test_file), "/home/testuser/test.txt"])

    assert result.exit_code == 0
    assert "uploaded" in result.output.lower() or "success" in result.output.lower()


def test_upload_directory_recursive(tmp_path):
    test_dir = tmp_path / "mysite"
    test_dir.mkdir()
    (test_dir / "index.html").write_text("<h1>Hello</h1>")

    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load, \
         patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        mock_client = MagicMock()
        mock_client.upload.return_value = 201
        mock_client_cls.return_value = mock_client

        result = runner.invoke(app, ["upload", str(test_dir), "/home/testuser/mysite", "-r"])

    assert result.exit_code == 0


def test_ls_shows_directory_contents():
    """ls command shows files and directories."""
    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        with patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.list.return_value = {
                "app.py": {"type": "file", "url": "..."},
                "static": {"type": "directory", "url": "..."},
                "requirements.txt": {"type": "file", "url": "..."},
            }
            mock_client_cls.return_value = mock_client
            result = runner.invoke(app, ["ls", "mysite"])

    assert result.exit_code == 0
    assert "app.py" in result.output
    assert "static/" in result.output
    assert "requirements.txt" in result.output
    # Directories should have trailing slash
    lines = result.output.strip().split("\n")
    assert any("/" in line for line in lines)


def test_ls_default_path_is_home():
    """ls without path lists home directory."""
    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        with patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.list.return_value = {".bashrc": {"type": "file"}}
            mock_client_cls.return_value = mock_client
            result = runner.invoke(app, ["ls"])

    assert result.exit_code == 0
    # Should call with /home/testuser/
    call_args = mock_client.list.call_args
    assert call_args[0] == ("testuser", "/home/testuser/")


def test_ls_empty_directory():
    """ls shows message for empty directory."""
    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        with patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.list.return_value = {}
            mock_client_cls.return_value = mock_client
            result = runner.invoke(app, ["ls", "emptydir"])

    assert result.exit_code == 0
    assert "(empty directory)" in result.output


def test_ls_absolute_path():
    """ls with absolute path uses it directly."""
    with patch("pa_cli.cli.files_cmd.Config.load") as mock_load:
        mock_load.return_value = {"username": "testuser", "token": "t", "host": "h"}
        with patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.list.return_value = {}
            mock_client_cls.return_value = mock_client
            result = runner.invoke(app, ["ls", "/home/other/"])

    assert result.exit_code == 0
    call_args = mock_client.list.call_args
    assert call_args[0] == ("testuser", "/home/other/")


def test_upload_shows_account_hint(tmp_path):
    """upload command shows current account in output."""
    local_file = tmp_path / "test.txt"
    local_file.write_text("hello")

    def fake_load(**kwargs):
        if kwargs.get("verbose", False):
            import typer as _typer
            _typer.echo("[account: testuser]")
        return {"username": "testuser", "token": "t", "host": "h"}

    with patch("pa_cli.cli.files_cmd.Config.load", side_effect=fake_load):
        with patch("pa_cli.cli.files_cmd.FilesClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.upload.return_value = 200
            mock_client_cls.return_value = mock_client
            result = runner.invoke(app, ["upload", str(local_file), "/remote/test.txt"])

    assert result.exit_code == 0
    assert "[account: testuser]" in result.output
