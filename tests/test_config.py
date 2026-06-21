import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pa_cli.config import Config, _encrypt, _decrypt


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
    assert "password" not in data["accounts"][0]
    assert "password_enc" in data["accounts"][0]
    assert data["accounts"][0]["password_enc"] != "secret"


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
    assert "password_enc" in data["accounts"][0]
    assert "password" not in data["accounts"][0]


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


def test_load_verbose_prints_account_hint(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [{"username": "testuser", "token": "abc123", "host": "www.pythonanywhere.com"}],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        account = Config.load(verbose=True)

    captured = capsys.readouterr()
    assert "[account: testuser]" in captured.out
    assert account["username"] == "testuser"


def test_load_default_is_silent(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [{"username": "testuser", "token": "abc123", "host": "www.pythonanywhere.com"}],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.load()

    captured = capsys.readouterr()
    assert captured.out == ""


# --- encryption tests ---


def test_encrypt_decrypt_roundtrip():
    """Encrypt then decrypt returns original text."""
    assert _decrypt(_encrypt("hello")) == "hello"
    assert _decrypt(_encrypt("benbenzhu.20")) == "benbenzhu.20"
    assert _decrypt(_encrypt("")) == ""


def test_encrypt_produces_different_output():
    """Encrypted text is not the same as plaintext."""
    assert _encrypt("secret") != "secret"
    assert len(_encrypt("secret")) > 0


def test_load_decrypts_password(tmp_path):
    """Config.load() decrypts password_enc and returns it as 'password'."""
    from pa_cli.config import _encrypt as enc
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "t", "host": "h", "password_enc": enc("mypassword")}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        account = Config.load()

    assert account["password"] == "mypassword"
    assert "password_enc" not in account


def test_load_handles_legacy_plaintext_password(tmp_path):
    """Config.load() handles old plaintext password field."""
    config_path = tmp_path / "config.json"
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "t", "host": "h", "password": "plaintext"}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    with patch("pa_cli.config.CONFIG_PATH", config_path):
        account = Config.load()

    assert account["password"] == "plaintext"


def test_save_then_load_password_roundtrip(tmp_path):
    """Save password, load it back, verify it matches."""
    config_path = tmp_path / "config.json"
    with patch("pa_cli.config.CONFIG_PATH", config_path):
        Config.save(username="testuser", token="t", host="h", password="mypassword")
        account = Config.load()

    assert account["password"] == "mypassword"


def test_validate_config_missing_accounts():
    """validate_config raises ValueError when accounts missing."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="missing 'accounts' field"):
        _validate_config({})


def test_validate_config_accounts_not_list():
    """validate_config raises ValueError when accounts is not a list."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a list"):
        _validate_config({"accounts": "not a list"})


def test_validate_config_account_not_dict():
    """validate_config raises ValueError when account is not a dict."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be an object"):
        _validate_config({"accounts": ["not a dict"]})


def test_validate_config_account_missing_username():
    """validate_config raises ValueError when account missing username."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="missing 'username' field"):
        _validate_config({"accounts": [{"token": "t"}]})


def test_validate_config_account_empty_username():
    """validate_config raises ValueError when account has empty username."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a non-empty string"):
        _validate_config({"accounts": [{"username": "", "token": "t"}]})


def test_validate_config_account_missing_token():
    """validate_config raises ValueError when account missing token."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="missing 'token' field"):
        _validate_config({"accounts": [{"username": "u"}]})


def test_validate_config_default_account_not_string():
    """validate_config raises ValueError when default_account is not a string."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a string"):
        _validate_config({"accounts": [{"username": "u", "token": "t"}], "default_account": 123})


def test_validate_config_valid():
    """validate_config returns ConfigData for valid config."""
    from pa_cli.config import _validate_config

    data = {
        "accounts": [{"username": "u", "token": "t", "host": "h"}],
        "default_account": "u",
    }
    result = _validate_config(data)
    assert len(result.accounts) == 1
    assert result.accounts[0].username == "u"
    assert result.default_account == "u"


def test_load_json_error():
    """load raises ValueError when JSON is invalid."""
    from pa_cli.config import Config, CONFIG_PATH
    from unittest.mock import patch

    with patch("pa_cli.config.CONFIG_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "invalid json"

        with pytest.raises(ValueError, match="Invalid JSON"):
            Config.load()


def test_load_invalid_config():
    """load raises ValueError when config is invalid."""
    from pa_cli.config import Config, CONFIG_PATH
    from unittest.mock import patch
    import json

    with patch("pa_cli.config.CONFIG_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = json.dumps({"invalid": "config"})

        with pytest.raises(ValueError, match="Invalid config format"):
            Config.load()


def test_save_updates_existing_account():
    """save updates existing account without losing other fields."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_save.json")
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "old-token", "host": "h"}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            Config.save(username="testuser", token="new-token")

        data = json.loads(config_path.read_text())
        assert data["accounts"][0]["token"] == "new-token"
        assert data["accounts"][0]["host"] == "h"
    finally:
        config_path.unlink()


def test_save_adds_new_account():
    """save adds new account to existing accounts."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_save2.json")
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"}
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            Config.save(username="user2", token="t2", host="h2")

        data = json.loads(config_path.read_text())
        assert len(data["accounts"]) == 2
        assert data["accounts"][1]["username"] == "user2"
    finally:
        config_path.unlink()


def test_save_password_encrypts():
    """save encrypts password when saving."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_save3.json")

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            Config.save(username="testuser", token="t", password="mypassword")

        data = json.loads(config_path.read_text())
        assert "password_enc" in data["accounts"][0]
        assert "password" not in data["accounts"][0]
    finally:
        config_path.unlink()


def test_load_decrypts_password():
    """load decrypts password_enc field."""
    from pa_cli.config import Config, CONFIG_PATH, _encrypt
    import json

    config_path = Path("./test_config_load.json")
    encrypted = _encrypt("mypassword")
    config_data = {
        "accounts": [
            {"username": "testuser", "token": "t", "host": "h", "password_enc": encrypted}
        ],
        "default_account": "testuser",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            account = Config.load()

        assert account["password"] == "mypassword"
    finally:
        config_path.unlink()


def test_set_default_success():
    """set_default changes default account."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_default.json")
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            Config.set_default("user2")

        data = json.loads(config_path.read_text())
        assert data["default_account"] == "user2"
    finally:
        config_path.unlink()


def test_remove_account():
    """remove deletes account from config."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_remove.json")
    config_data = {
        "accounts": [
            {"username": "user1", "token": "t1", "host": "h1"},
            {"username": "user2", "token": "t2", "host": "h2"},
        ],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            Config.remove("user2")

        data = json.loads(config_path.read_text())
        assert len(data["accounts"]) == 1
        assert data["accounts"][0]["username"] == "user1"
    finally:
        config_path.unlink()


def test_validate_config_account_invalid_host():
    """validate_config raises ValueError when host is not a string."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a string"):
        _validate_config({
            "accounts": [{"username": "u", "token": "t", "host": 123}],
            "default_account": "u",
        })


def test_validate_config_account_invalid_token():
    """validate_config raises ValueError when token is not a string."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a string"):
        _validate_config({
            "accounts": [{"username": "u", "token": 123}],
            "default_account": "u",
        })


def test_validate_config_account_optional_host():
    """validate_config accepts account without host field."""
    from pa_cli.config import _validate_config

    data = {
        "accounts": [{"username": "u", "token": "t"}],
        "default_account": "u",
    }
    result = _validate_config(data)
    assert result.accounts[0].host == "www.pythonanywhere.com"


def test_validate_config_not_dict():
    """validate_config raises ValueError when data is not a dict."""
    from pa_cli.config import _validate_config

    with pytest.raises(ValueError, match="must be a JSON object"):
        _validate_config("not a dict")


def test_load_account_not_found():
    """load raises ValueError when account not found."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_notfound.json")
    config_data = {
        "accounts": [{"username": "user1", "token": "t1", "host": "h1"}],
        "default_account": "user1",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            with pytest.raises(ValueError, match="not found"):
                Config.load(username="nonexistent")
    finally:
        config_path.unlink()


def test_load_no_default_account():
    """load raises ValueError when no default account."""
    from pa_cli.config import Config, CONFIG_PATH
    import json

    config_path = Path("./test_config_nodefault.json")
    config_data = {
        "accounts": [{"username": "user1", "token": "t1", "host": "h1"}],
        "default_account": "",
    }
    config_path.write_text(json.dumps(config_data))

    try:
        with patch("pa_cli.config.CONFIG_PATH", config_path):
            with pytest.raises(ValueError, match="No default account"):
                Config.load()
    finally:
        config_path.unlink()
