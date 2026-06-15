import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

import typer

CONFIG_PATH = Path.home() / ".pa-cli" / "config.json"


@dataclass
class AccountConfig:
    username: str
    token: str
    host: str = "www.pythonanywhere.com"
    password: str | None = None
    password_enc: str | None = None


@dataclass
class ConfigData:
    accounts: list[AccountConfig]
    default_account: str


def _validate_config(data: dict) -> ConfigData:
    """Validate config data and return ConfigData. Raises ValueError on invalid data."""
    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object")

    if "accounts" not in data:
        raise ValueError("Config missing 'accounts' field")

    if not isinstance(data["accounts"], list):
        raise ValueError("'accounts' must be a list")

    accounts = []
    for i, acc in enumerate(data["accounts"]):
        if not isinstance(acc, dict):
            raise ValueError(f"Account {i} must be an object")

        if "username" not in acc:
            raise ValueError(f"Account {i} missing 'username' field")

        if not isinstance(acc["username"], str) or not acc["username"]:
            raise ValueError(f"Account {i} 'username' must be a non-empty string")

        if "token" not in acc:
            raise ValueError(f"Account {i} missing 'token' field")

        if not isinstance(acc["token"], str):
            raise ValueError(f"Account {i} 'token' must be a string")

        host = acc.get("host", "www.pythonanywhere.com")
        if not isinstance(host, str):
            raise ValueError(f"Account {i} 'host' must be a string")

        account_kwargs = {
            "username": acc["username"],
            "token": acc["token"],
            "host": host,
        }
        if "password" in acc:
            account_kwargs["password"] = acc["password"]
        if "password_enc" in acc:
            account_kwargs["password_enc"] = acc["password_enc"]
        accounts.append(AccountConfig(**account_kwargs))

    default_account = data.get("default_account", "")
    if not isinstance(default_account, str):
        raise ValueError("'default_account' must be a string")

    return ConfigData(accounts=accounts, default_account=default_account)


def _get_machine_key() -> bytes:
    """Generate encryption key from machine-specific info."""
    seed = f"{os.environ.get('USERNAME', '')}-{os.environ.get('COMPUTERNAME', '')}"
    return hashlib.sha256(seed.encode()).digest()


def _encrypt(plaintext: str) -> str:
    """Encrypt a string using machine key. Returns base64-encoded ciphertext."""
    key = _get_machine_key()
    data = plaintext.encode("utf-8")
    encrypted = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
    return base64.b64encode(encrypted).decode("ascii")


def _decrypt(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext using machine key."""
    key = _get_machine_key()
    data = base64.b64decode(ciphertext)
    decrypted = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
    return decrypted.decode("utf-8")


def _decrypt_account(account: dict) -> dict:
    """Decrypt password in account dict. Handles both encrypted and legacy plaintext."""
    account = dict(account)
    if "password_enc" in account:
        if account["password_enc"] is not None:
            try:
                account["password"] = _decrypt(account["password_enc"])
            except Exception:
                account["password"] = None
        del account["password_enc"]
    # Keep legacy plaintext password as-is (already in account["password"])
    # Remove password field if it's None (backward compatibility)
    if "password" in account and account["password"] is None:
        del account["password"]
    return account


class Config:
    @staticmethod
    def save(
        username: str | None = None,
        token: str | None = None,
        host: str | None = None,
        password: str | None = None,
    ) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text())
            except json.JSONDecodeError:
                data = {"accounts": [], "default_account": username or ""}
        else:
            data = {"accounts": [], "default_account": username or ""}

        # If partial update (e.g. only password), load existing account
        existing_account = None
        target_username = username or data.get("default_account", "")
        if target_username:
            for a in data.get("accounts", []):
                if a["username"] == target_username:
                    existing_account = a
                    break

        if existing_account:
            account = dict(existing_account)
            if username is not None:
                account["username"] = username
            if token is not None:
                account["token"] = token
            if host is not None:
                account["host"] = host
            if password is not None:
                account["password_enc"] = _encrypt(password)
                account.pop("password", None)
        else:
            account = {
                "username": target_username,
                "token": token or "",
                "host": host or "www.pythonanywhere.com",
            }
            if password is not None:
                account["password_enc"] = _encrypt(password)

        # Update existing or append new
        existing = [i for i, a in enumerate(data["accounts"]) if a["username"] == target_username]
        if existing:
            data["accounts"][existing[0]] = account
        else:
            data["accounts"].append(account)

        data["default_account"] = target_username
        CONFIG_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def load(username: str | None = None, verbose: bool = False) -> dict:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")

        try:
            raw_data = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

        try:
            config = _validate_config(raw_data)
        except ValueError as e:
            raise ValueError(f"Invalid config format: {e}")

        if username:
            for account in config.accounts:
                if account.username == username:
                    if verbose:
                        typer.echo(f"[account: {username}]")
                    return _decrypt_account(vars(account))
            raise ValueError(f"Account '{username}' not found in config.")

        # Return default account
        for account in config.accounts:
            if account.username == config.default_account:
                if verbose:
                    typer.echo(f"[account: {config.default_account}]")
                return _decrypt_account(vars(account))

        raise ValueError("No default account configured.")

    @staticmethod
    def list_accounts() -> list[dict]:
        if not CONFIG_PATH.exists():
            return []
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            return []
        return data.get("accounts", [])

    @staticmethod
    def set_default(username: str) -> None:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        found = any(a["username"] == username for a in data.get("accounts", []))
        if not found:
            raise ValueError(f"Account '{username}' not found in config.")
        data["default_account"] = username
        CONFIG_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def remove(username: str) -> str | None:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        found = [i for i, a in enumerate(data.get("accounts", [])) if a["username"] == username]
        if not found:
            raise ValueError(f"Account '{username}' not found in config.")
        data["accounts"].pop(found[0])
        new_default = None
        if data["default_account"] == username:
            if data["accounts"]:
                data["default_account"] = data["accounts"][0]["username"]
                new_default = data["default_account"]
            else:
                data["default_account"] = ""
        CONFIG_PATH.write_text(json.dumps(data, indent=2))
        return new_default
