from pa_cli.api.client import BaseClient


class DatabasesClient(BaseClient):
    def get_mysql_info(self, username: str) -> dict:
        """Get MySQL database information."""
        response = self._request("GET", "/api/v0/user/{username}/databases/mysql/", username=username)
        return response.json()
