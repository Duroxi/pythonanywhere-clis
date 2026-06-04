import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".pa-cli" / "config.json"


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
            data = json.loads(CONFIG_PATH.read_text())
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
                account["password"] = password
        else:
            account = {
                "username": target_username,
                "token": token or "",
                "host": host or "www.pythonanywhere.com",
            }
            if password is not None:
                account["password"] = password

        # Update existing or append new
        existing = [i for i, a in enumerate(data["accounts"]) if a["username"] == target_username]
        if existing:
            data["accounts"][existing[0]] = account
        else:
            data["accounts"].append(account)

        data["default_account"] = target_username
        CONFIG_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def load(username: str | None = None) -> dict:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")

        data = json.loads(CONFIG_PATH.read_text())

        if username:
            for account in data["accounts"]:
                if account["username"] == username:
                    return account
            raise ValueError(f"Account '{username}' not found in config.")

        # Return default account
        default = data.get("default_account")
        for account in data["accounts"]:
            if account["username"] == default:
                return account

        raise ValueError("No default account configured.")

    @staticmethod
    def list_accounts() -> list[dict]:
        if not CONFIG_PATH.exists():
            return []
        data = json.loads(CONFIG_PATH.read_text())
        return data.get("accounts", [])

    @staticmethod
    def set_default(username: str) -> None:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")
        data = json.loads(CONFIG_PATH.read_text())
        found = any(a["username"] == username for a in data.get("accounts", []))
        if not found:
            raise ValueError(f"Account '{username}' not found in config.")
        data["default_account"] = username
        CONFIG_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def remove(username: str) -> str | None:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found. Run 'pa init' first.")
        data = json.loads(CONFIG_PATH.read_text())
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
