from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from pa_cli.workflows.deploy import deploy, deploy_preview, collect_files
from pa_cli.exceptions import PACliError


def test_deploy_full_flow(tmp_path):
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Hello</h1>")

    mock_files = MagicMock()
    mock_consoles = MagicMock()
    mock_webapps = MagicMock()

    mock_consoles.create.return_value = {"id": 42}
    mock_consoles.get_output.return_value = {"output": "done"}

    with patch("pa_cli.workflows.deploy.FilesClient", return_value=mock_files), \
         patch("pa_cli.workflows.deploy.ConsolesClient", return_value=mock_consoles), \
         patch("pa_cli.workflows.deploy.WebappsClient", return_value=mock_webapps), \
         patch("pa_cli.workflows.deploy.time.sleep"):
        result = deploy(
            local_dir=str(site_dir),
            username="testuser",
            token="t",
            host="www.pythonanywhere.com",
            domain="testuser.pythonanywhere.com",
            python_version="python310",
        )

    assert result == "https://testuser.pythonanywhere.com"
    mock_files.upload.assert_called()
    mock_consoles.create.assert_called_once()
    mock_webapps.create.assert_called_once()
    mock_webapps.reload.assert_called_once()


def test_deploy_invalid_directory():
    with pytest.raises(PACliError, match="is not a directory"):
        deploy(
            local_dir="/nonexistent/path",
            username="testuser",
            token="t",
            host="www.pythonanywhere.com",
            domain="testuser.pythonanywhere.com",
        )


def test_deploy_dry_run(tmp_path):
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Hello</h1>")

    mock_files = MagicMock()
    mock_consoles = MagicMock()
    mock_webapps = MagicMock()

    with patch("pa_cli.workflows.deploy.FilesClient", return_value=mock_files), \
         patch("pa_cli.workflows.deploy.ConsolesClient", return_value=mock_consoles), \
         patch("pa_cli.workflows.deploy.WebappsClient", return_value=mock_webapps):
        result = deploy(
            local_dir=str(site_dir),
            username="testuser",
            token="t",
            host="www.pythonanywhere.com",
            domain="testuser.pythonanywhere.com",
            dry_run=True,
        )

    assert result == ""
    mock_files.upload.assert_not_called()
    mock_consoles.create.assert_not_called()
    mock_webapps.create.assert_not_called()
    mock_webapps.reload.assert_not_called()


def test_collect_files(tmp_path):
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Hello</h1>")
    (site_dir / "static").mkdir()
    (site_dir / "static" / "style.css").write_text("body {}")

    files = collect_files(str(site_dir))
    assert len(files) == 2
    filenames = [f.name for f in files]
    assert "index.html" in filenames
    assert "style.css" in filenames


def test_deploy_preview(tmp_path):
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Hello</h1>")
    (site_dir / "requirements.txt").write_text("flask==2.0")
    (site_dir / "static").mkdir()
    (site_dir / "static" / "style.css").write_text("body {}")

    account = {"username": "testuser"}
    deploy_preview(account, str(site_dir), "testuser.pythonanywhere.com", "python310")
    # No assertion needed - just verify it doesn't raise
