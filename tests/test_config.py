import json
import os
from pathlib import Path
from unittest.mock import patch

from pa_cli.config import Config


def test_save_creates_config_file(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.save(username="testuser", token="abc123", host="www.pythonanywhere.com")

    assert config_path.exists()
    data = json.loads(config_path.read_text())
    assert data["default_account"] == "testuser"
    assert data["accounts"][0]["username"] == "testuser"
    assert data["accounts"][0]["token"] == "abc123"
    assert data["accounts"][0]["host"] == "www.pythonanywhere.com"


def test_load_returns_account_info(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "abc123", "host": "www.pythonanywhere.com"}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        account = Config.load()

    assert account["username"] == "testuser"
    assert account["token"] == "abc123"
    assert account["host"] == "www.pythonanywhere.com"


def test_load_raises_when_no_config(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        try:
            Config.load()
            assert False, "Should have raised"
        except FileNotFoundError:
            pass
