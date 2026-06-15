from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.files_cmd import app

runner = CliRunner()


def test_upload_single_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.upload.return_value = 201
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["upload", str(test_file), "/home/testuser/test.txt"])

    assert result.exit_code == 0
    assert "uploaded" in result.output.lower() or "success" in result.output.lower()


def test_upload_directory_recursive(tmp_path):
    test_dir = tmp_path / "mysite"
    test_dir.mkdir()
    (test_dir / "index.html").write_text("<h1>Hello</h1>")

    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.upload.return_value = 201
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["upload", str(test_dir), "/home/testuser/mysite", "-r"])

    assert result.exit_code == 0


def test_ls_shows_directory_contents():
    """ls command shows files and directories."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {
            "app.py": {"type": "file", "url": "..."},
            "static": {"type": "directory", "url": "..."},
            "requirements.txt": {"type": "file", "url": "..."},
        }
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
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
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {".bashrc": {"type": "file"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["ls"])

    assert result.exit_code == 0
    # Should call with /home/testuser/
    call_args = mock_client.list.call_args
    assert call_args[0] == ("testuser", "/home/testuser/")


def test_ls_empty_directory():
    """ls shows message for empty directory."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["ls", "emptydir"])

    assert result.exit_code == 0
    assert "(empty directory)" in result.output


def test_ls_absolute_path():
    """ls with absolute path uses it directly."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["ls", "/home/other/"])

    assert result.exit_code == 0
    call_args = mock_client.list.call_args
    assert call_args[0] == ("testuser", "/home/other/")


def test_download_single_file(tmp_path):
    """download command downloads a single file."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"test.txt": {"type": "file"}}
        mock_client.download.return_value = b"file content"
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        local_file = tmp_path / "downloaded.txt"
        result = runner.invoke(app, ["download", "test.txt", str(local_file)])
    assert result.exit_code == 0
    assert "Downloaded" in result.output
    assert local_file.read_bytes() == b"file content"


def test_download_requires_recursive_for_dir():
    """download command requires -r for directories."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"mysite": {"type": "directory"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["download", "mysite"])
    assert result.exit_code == 1
    assert "recursive" in result.output.lower()


def test_download_recursive_directory(tmp_path):
    """download -r downloads entire directory."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = [
            {"mysite": {"type": "directory"}},
            {"app.py": {"type": "file"}, "static": {"type": "directory"}},
            {"style.css": {"type": "file"}},
        ]
        mock_client.download.return_value = b"content"
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        local_dir = tmp_path / "downloaded"
        result = runner.invoke(app, ["download", "mysite", str(local_dir), "-r"])
    assert result.exit_code == 0
    assert "Downloaded" in result.output
    assert (local_dir / "app.py").exists()
    assert (local_dir / "static" / "style.css").exists()


def test_upload_shows_account_hint(tmp_path):
    """upload command shows current account in output."""
    local_file = tmp_path / "test.txt"
    local_file.write_text("hello")

    def fake_get_client(client_class):
        import typer as _typer
        _typer.echo("[account: testuser]")
        mock_client = MagicMock()
        mock_client.upload.return_value = 200
        return {"username": "testuser", "token": "t", "host": "h"}, mock_client

    with patch("pa_cli.cli.files_cmd.get_client", side_effect=fake_get_client):
        result = runner.invoke(app, ["upload", str(local_file), "/remote/test.txt"])

    assert result.exit_code == 0
    assert "[account: testuser]" in result.output


def test_rm_file():
    """rm command deletes a file after confirmation."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"old.txt": {"type": "file"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["rm", "old.txt"], input="y\n")
    assert result.exit_code == 0
    assert "Deleted old.txt" in result.output
    mock_client.delete.assert_called_once()


def test_rm_file_force():
    """rm -f skips confirmation."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"old.txt": {"type": "file"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["rm", "old.txt", "-f"])
    assert result.exit_code == 0
    assert "Deleted" in result.output
    mock_client.delete.assert_called_once()


def test_rm_cancelled():
    """rm cancels when user says no."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"old.txt": {"type": "file"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["rm", "old.txt"], input="n\n")
    assert "Cancelled" in result.output
    mock_client.delete.assert_not_called()


def test_rm_directory_requires_recursive():
    """rm requires -r for directories."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"olddir": {"type": "directory"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["rm", "olddir"])
    assert result.exit_code == 1
    assert "recursive" in result.output.lower()


def test_rm_directory_recursive():
    """rm -rf deletes directory."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"olddir": {"type": "directory"}}
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)
        result = runner.invoke(app, ["rm", "olddir", "-r", "-f"])
    assert result.exit_code == 0
    assert "Deleted olddir" in result.output
    assert "recursive" in result.output
    mock_client.delete.assert_called_once()
