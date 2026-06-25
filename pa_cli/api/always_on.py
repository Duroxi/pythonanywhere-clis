from pa_cli.api.client import BaseClient


class AlwaysOnClient(BaseClient):
    def list(self, username: str) -> list:
        """List all always-on tasks."""
        response = self._request("GET", "/api/v0/user/{username}/always_on/", username=username)
        return response.json()

    def create(self, username: str, command: str, enabled: bool = True) -> dict:
        """Create a new always-on task."""
        response = self._request(
            "POST",
            "/api/v0/user/{username}/always_on/",
            username=username,
            json={"command": command, "enabled": enabled},
        )
        return response.json()

    def delete(self, username: str, task_id: int) -> None:
        """Delete an always-on task."""
        self._request("DELETE", "/api/v0/user/{username}/always_on/{id}/", username=username, id=task_id)

    def update(self, username: str, task_id: int, **kwargs) -> None:
        """Update an always-on task."""
        self._request(
            "PATCH",
            "/api/v0/user/{username}/always_on/{id}/",
            username=username,
            id=task_id,
            json=kwargs,
        )

    def restart(self, username: str, task_id: int, **kwargs) -> None:
        """Restart an always-on task."""
        self._request(
            "POST",
            "/api/v0/user/{username}/always_on/{id}/restart/",
            username=username,
            id=task_id,
            json=kwargs,
        )
