from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pa_cli.cli.files_cmd import app
from pa_cli.exceptions import APIError, NetworkError, NotFoundError

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


# --- share command tests ---


def test_share_file():
    """share command generates share link."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.share.return_value = "/user/testuser/shares/abc123/"
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share", "test.txt"])

    assert result.exit_code == 0
    assert "Share link" in result.output
    assert "abc123" in result.output
    mock_client.share.assert_called_once_with("testuser", "/home/testuser/test.txt/")


def test_share_file_not_found():
    """share command shows error when file not found."""
    from pa_cli.exceptions import NotFoundError

    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.share.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share", "missing.txt"])

    assert result.exit_code == 1
    assert "File not found" in result.output


# --- unshare command tests ---


def test_unshare_file():
    """unshare command stops sharing a file."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.unshare.return_value = None
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["unshare", "test.txt"])

    assert result.exit_code == 0
    assert "Stopped sharing" in result.output
    mock_client.unshare.assert_called_once_with("testuser", "/home/testuser/test.txt/")


def test_unshare_file_not_found():
    """unshare command shows error when file not found or not shared."""
    from pa_cli.exceptions import NotFoundError

    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.unshare.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["unshare", "missing.txt"])

    assert result.exit_code == 1
    assert "File not found或未分享" in result.output


# --- share-status command tests ---


def test_share_status_when_shared():
    """share-status shows link when file is shared."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_share_status.return_value = "/user/testuser/shares/abc123/"
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share-status", "test.txt"])

    assert result.exit_code == 0
    assert "File is shared" in result.output
    assert "abc123" in result.output
    mock_client.get_share_status.assert_called_once_with("testuser", "/home/testuser/test.txt/")


def test_share_status_when_not_shared():
    """share-status shows message when file is not shared."""
    from pa_cli.exceptions import NotFoundError

    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_share_status.side_effect = NotFoundError("Not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share-status", "test.txt"])

    assert result.exit_code == 0
    assert "File is not shared" in result.output


def test_files_ls_network_error():
    """files ls shows error on network failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ls"])

    assert result.exit_code == 1
    assert "Network error" in result.output


def test_files_download_not_found():
    """files download shows error when file not found."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["download", "missing.txt"])

    assert result.exit_code == 1
    assert "File not found" in result.output


def test_files_rm_not_found():
    """files rm shows error when file not found."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = NotFoundError("File not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["rm", "missing.txt", "-f"])

    assert result.exit_code == 1
    assert "File not found" in result.output


def test_files_upload_api_error():
    """files upload shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.upload.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        test_file = Path("./test_upload.txt")
        test_file.write_text("test")
        try:
            result = runner.invoke(app, ["upload", str(test_file), "/home/testuser/test.txt"])
        finally:
            test_file.unlink()

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_download_api_error():
    """files download shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"test.txt": {"type": "file"}}
        mock_client.download.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["download", "test.txt"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_rm_api_error():
    """files rm shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.return_value = {"test.txt": {"type": "file"}}
        mock_client.delete.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["rm", "test.txt", "-f"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_share_api_error():
    """files share shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.share.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share", "test.txt"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_unshare_api_error():
    """files unshare shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.unshare.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["unshare", "test.txt"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_share_status_api_error():
    """files share-status shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_share_status.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share-status", "test.txt"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_ls_not_found():
    """files ls shows error when path not found."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = NotFoundError("Path not found")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ls"])

    assert result.exit_code == 1
    assert "Path not found" in result.output


def test_files_ls_api_error():
    """files ls shows error on API failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list.side_effect = APIError("API error 500")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["ls"])

    assert result.exit_code == 1
    assert "API error" in result.output


def test_files_upload_local_not_found(tmp_path):
    """files upload shows error when local file not found."""
    result = runner.invoke(app, ["upload", "/nonexistent/file.txt", "/remote/path"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_files_upload_directory_without_recursive(tmp_path):
    """files upload shows error when uploading directory without -r."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = runner.invoke(app, ["upload", str(test_dir), "/remote/path"])

    assert result.exit_code == 1
    assert "recursive" in result.output.lower()


def test_files_share_status_network_error():
    """files share-status shows error on network failure."""
    with patch("pa_cli.cli.files_cmd.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_share_status.side_effect = NetworkError("Connection failed")
        mock_get_client.return_value = ({"username": "testuser", "token": "t", "host": "h"}, mock_client)

        result = runner.invoke(app, ["share-status", "test.txt"])

    assert result.exit_code == 1
    assert "Network error" in result.output
