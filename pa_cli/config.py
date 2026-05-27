import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".pa-cli" / "config.json"


class Config:
    @staticmethod
    def save(username: str, token: str, host: str = "www.pythonanywhere.com") -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
        else:
            data = {"accounts": [], "default_account": username}

        account = {"username": username, "token": token, "host": host}

        # Update existing or append new
        existing = [i for i, a in enumerate(data["accounts"]) if a["username"] == username]
        if existing:
            data["accounts"][existing[0]] = account
        else:
            data["accounts"].append(account)

        data["default_account"] = username
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
