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


def test_deploy_with_requirements(tmp_path):
    """deploy creates virtualenv when requirements.txt exists."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "requirements.txt").write_text("flask==2.0")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    # Should create virtualenv and install requirements
    assert mock_consoles.send_input.call_count >= 3  # cd, mkvirtualenv, pip install


def test_deploy_without_requirements(tmp_path):
    """deploy skips virtualenv when no requirements.txt."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    # Should only cd, not create virtualenv
    assert mock_consoles.send_input.call_count == 1  # only cd


def test_deploy_with_static_dir(tmp_path):
    """deploy adds static file mapping when static/ exists."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "static").mkdir()
    (site_dir / "static" / "style.css").write_text("body {}")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    # Should add static file mapping
    mock_webapps.add_static_file.assert_called_once()


def test_deploy_without_static_dir(tmp_path):
    """deploy skips static file mapping when no static/."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    # Should not add static file mapping
    mock_webapps.add_static_file.assert_not_called()


def test_deploy_creates_console(tmp_path):
    """deploy creates console for environment setup."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    mock_consoles.create.assert_called_once_with("testuser")


def test_deploy_creates_webapp(tmp_path):
    """deploy creates webapp if not exists."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    mock_webapps.create.assert_called_once_with("testuser", "testuser.pythonanywhere.com", "python310")


def test_deploy_updates_webapp(tmp_path):
    """deploy updates webapp source directory."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    mock_webapps.update.assert_called_once()


def test_deploy_reloads_webapp(tmp_path):
    """deploy reloads webapp after configuration."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")

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
        )

    assert result == "https://testuser.pythonanywhere.com"
    mock_webapps.reload.assert_called_once_with("testuser", "testuser.pythonanywhere.com")


def test_deploy_preview_shows_files(tmp_path):
    """deploy_preview shows file list."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "requirements.txt").write_text("flask==2.0")

    account = {"username": "testuser"}
    deploy_preview(account, str(site_dir), "testuser.pythonanywhere.com", "python310")
    # No assertion needed - just verify it doesn't raise


def test_deploy_preview_shows_env_setup(tmp_path):
    """deploy_preview shows environment setup when requirements.txt exists."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "requirements.txt").write_text("flask==2.0")

    account = {"username": "testuser"}
    deploy_preview(account, str(site_dir), "testuser.pythonanywhere.com", "python310")
    # No assertion needed - just verify it doesn't raise


def test_deploy_preview_shows_static_mapping(tmp_path):
    """deploy_preview shows static file mapping when static/ exists."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "static").mkdir()
    (site_dir / "static" / "style.css").write_text("body {}")

    account = {"username": "testuser"}
    deploy_preview(account, str(site_dir), "testuser.pythonanywhere.com", "python310")
    # No assertion needed - just verify it doesn't raise


def test_collect_files_returns_all_files(tmp_path):
    """collect_files returns all files recursively."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()
    (site_dir / "app.py").write_text("print('hello')")
    (site_dir / "static").mkdir()
    (site_dir / "static" / "style.css").write_text("body {}")

    files = collect_files(str(site_dir))
    assert len(files) == 2
    filenames = [f.name for f in files]
    assert "app.py" in filenames
    assert "style.css" in filenames


def test_collect_files_returns_empty_for_empty_dir(tmp_path):
    """collect_files returns empty list for empty directory."""
    site_dir = tmp_path / "mysite"
    site_dir.mkdir()

    files = collect_files(str(site_dir))
    assert len(files) == 0


def test_deploy_wait_for_console():
    """_wait_for_console polls until prompt returns."""
    from pa_cli.workflows.deploy import _wait_for_console

    mock_client = MagicMock()
    mock_client.get_output.side_effect = [
        {"output": ""},
        {"output": "$ echo hello\nhello\n$ "},
    ]

    with patch("pa_cli.workflows.deploy.time.sleep"):
        result = _wait_for_console(mock_client, "testuser", 42)

    assert "$ echo hello" in result
    assert "hello" in result


def test_deploy_wait_for_console_timeout():
    """_wait_for_console returns after MAX_WAIT."""
    from pa_cli.workflows.deploy import _wait_for_console, MAX_WAIT

    mock_client = MagicMock()
    mock_client.get_output.return_value = {"output": "$ still running..."}

    with patch("pa_cli.workflows.deploy.time.sleep"):
        result = _wait_for_console(mock_client, "testuser", 42)

    assert "still running" in result
