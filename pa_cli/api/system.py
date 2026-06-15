from pa_cli.api.client import BaseClient


class SystemClient(BaseClient):
    def get_cpu_usage(self, username: str) -> dict:
        """Get CPU usage stats."""
        response = self._request("GET", "/api/v0/user/{username}/cpu/", username=username)
        return response.json()
