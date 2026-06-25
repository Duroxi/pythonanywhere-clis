from pa_cli.api.client import BaseClient


class SystemClient(BaseClient):
    def get_cpu_usage(self, username: str) -> dict:
        """Get CPU usage stats."""
        response = self._request("GET", "/api/v0/user/{username}/cpu/", username=username)
        return response.json()

    def get_system_image(self, username: str) -> dict:
        """Get current system image and available images."""
        response = self._request("GET", "/api/v0/user/{username}/system_image/", username=username)
        return response.json()

    def set_system_image(self, username: str, image: str) -> None:
        """Set system image."""
        self._request(
            "PATCH",
            "/api/v0/user/{username}/system_image/",
            username=username,
            json={"system_image": image},
        )
