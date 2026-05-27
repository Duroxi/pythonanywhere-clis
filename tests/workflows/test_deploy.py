from pathlib import Path
from unittest.mock import patch, MagicMock, call

from pa_cli.workflows.deploy import deploy


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
