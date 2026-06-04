import json
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


def test_save_with_password(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.save(username="testuser", token="abc123", host="www.pythonanywhere.com", password="secret")

    assert config_path.exists()
    data = json.loads(config_path.read_text())
    assert data["accounts"][0]["password"] == "secret"


def test_save_without_password_backward_compat(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.save(username="testuser", token="abc123", host="www.pythonanywhere.com")

    data = json.loads(config_path.read_text())
    assert "password" not in data["accounts"][0]


def test_load_returns_password_when_present(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "abc123", "host": "www.pythonanywhere.com", "password": "secret"}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        account = Config.load()

    assert account["password"] == "secret"


def test_load_backward_compat_no_password_field(tmp_path):
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

    assert "password" not in account


def test_save_update_preserves_existing_account_structure(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.save(username="testuser", token="abc123", password="oldpw")
        Config.save(username="testuser", token="abc123", password="newpw")

    data = json.loads(config_path.read_text())
    assert len(data["accounts"]) == 1
    assert data["accounts"][0]["password"] == "newpw"


def test_list_accounts_returns_all_accounts(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        accounts = Config.list_accounts()

    assert len(accounts) == 2
    assert accounts[0]["username"] == "user1"
    assert accounts[1]["username"] == "user2"


def test_list_accounts_returns_empty_list_when_no_config(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        accounts = Config.list_accounts()

    assert accounts == []


def test_set_default_changes_default_account(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.set_default("user2")

    data = json.loads(config_path.read_text())
    assert data["default_account"] == "user2"


def test_set_default_raises_for_nonexistent_user(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [{"username": "user1", "token": "t1", "host": "h1"}],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        try:
            Config.set_default("nobody")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


def test_remove_account(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.remove("user2")

    data = json.loads(config_path.read_text())
    assert len(data["accounts"]) == 1
    assert data["accounts"][0]["username"] == "user1"
    assert data["default_account"] == "user1"


def test_remove_default_account_switches_to_first_remaining(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        new_default = Config.remove("user1")

    data = json.loads(config_path.read_text())
    assert len(data["accounts"]) == 1
    assert data["default_account"] == "user2"
    assert new_default == "user2"


def test_remove_last_account_clears_default(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [{"username": "user1", "token": "t1", "host": "h1"}],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        new_default = Config.remove("user1")

    data = json.loads(config_path.read_text())
    assert len(data["accounts"]) == 0
    assert data["default_account"] == ""
    assert new_default is None


def test_remove_raises_for_nonexistent_user(tmp_path):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [{"username": "user1", "token": "t1", "host": "h1"}],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        try:
            Config.remove("nobody")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
