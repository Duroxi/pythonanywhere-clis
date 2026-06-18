from pa_cli.api.client import BaseClient


class TasksClient(BaseClient):
    def list(self, username: str) -> list:
        """List all scheduled tasks."""
        response = self._request("GET", "/api/v0/user/{username}/schedule/", username=username)
        return response.json()

    def get(self, username: str, task_id: int) -> dict:
        """Get a specific scheduled task."""
        response = self._request("GET", "/api/v0/user/{username}/schedule/{id}/", username=username, id=task_id)
        return response.json()

    def create(self, username: str, command: str, interval: str = "daily",
               hour: int = 0, minute: int = 0, enabled: bool = True,
               description: str = "") -> dict:
        """Create a new scheduled task."""
        response = self._request(
            "POST",
            "/api/v0/user/{username}/schedule/",
            username=username,
            json={
                "command": command,
                "interval": interval,
                "hour": hour,
                "minute": minute,
                "enabled": enabled,
                "description": description,
            },
        )
        return response.json()

    def update(self, username: str, task_id: int, **kwargs) -> dict:
        """Update a scheduled task."""
        response = self._request(
            "PATCH",
            "/api/v0/user/{username}/schedule/{id}/",
            username=username,
            id=task_id,
            json=kwargs,
        )
        return response.json()

    def delete(self, username: str, task_id: int) -> None:
        """Delete a scheduled task."""
        self._request("DELETE", "/api/v0/user/{username}/schedule/{id}/", username=username, id=task_id)
