from pa_cli.api.client import BaseClient


class WebappsClient(BaseClient):
    def create(self, username: str, domain_name: str, python_version: str) -> None:
        self._request(
            "POST",
            "/api/v0/user/{username}/webapps/",
            username=username,
            data={"domain_name": domain_name, "python_version": python_version},
        )

    def update(self, username: str, domain_name: str, **kwargs) -> None:
        self._request(
            "PUT",
            "/api/v0/user/{username}/webapps/{domain_name}/",
            username=username,
            domain_name=domain_name,
            json=kwargs,
        )

    def delete(self, username: str, domain_name: str) -> None:
        self._request(
            "DELETE",
            "/api/v0/user/{username}/webapps/{domain_name}/",
            username=username,
            domain_name=domain_name,
        )

    def enable(self, username: str, domain_name: str) -> None:
        self._request(
            "POST",
            "/api/v0/user/{username}/webapps/{domain_name}/enable/",
            username=username,
            domain_name=domain_name,
        )

    def disable(self, username: str, domain_name: str) -> None:
        self._request(
            "POST",
            "/api/v0/user/{username}/webapps/{domain_name}/disable/",
            username=username,
            domain_name=domain_name,
        )

    def add_static_file(self, username: str, domain_name: str, url: str, path: str) -> None:
        self._request(
            "POST",
            "/api/v0/user/{username}/webapps/{domain_name}/static_files/",
            username=username,
            domain_name=domain_name,
            data={"url": url, "path": path},
        )

    def reload(self, username: str, domain_name: str) -> None:
        self._request(
            "POST",
            "/api/v0/user/{username}/webapps/{domain_name}/reload/",
            username=username,
            domain_name=domain_name,
        )

    def get_ssl_info(self, username: str, domain_name: str) -> dict:
        """Get SSL certificate information."""
        response = self._request(
            "GET",
            "/api/v0/user/{username}/webapps/{domain_name}/ssl/",
            username=username,
            domain_name=domain_name,
        )
        return response.json()
