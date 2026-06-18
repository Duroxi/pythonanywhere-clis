from pa_cli.api.client import BaseClient
from pa_cli.exceptions import APIError, NotFoundError


class FilesClient(BaseClient):
    def upload(self, username: str, remote_path: str, content: bytes) -> int:
        url = self._build_url(
            "/api/v0/user/{username}/files/path{remote_path}",
            username=username,
            remote_path=remote_path,
        )
        response = self.session.post(url, files={"content": content})
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {remote_path}")
        try:
            response.raise_for_status()
        except Exception as e:
            raise APIError(f"Upload failed: {response.status_code} {response.text}") from e
        return response.status_code

    def list(self, username: str, remote_path: str) -> dict:
        """List files and directories at remote path. Returns dict of {name: {type, url}}."""
        url = self._build_url(
            "/api/v0/user/{username}/files/path{remote_path}",
            username=username,
            remote_path=remote_path,
        )
        response = self.session.get(url)
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {remote_path}")
        try:
            response.raise_for_status()
        except Exception as e:
            raise APIError(f"List failed: {response.status_code} {response.text}") from e
        return response.json()

    def download(self, username: str, remote_path: str) -> bytes:
        """Download a file from remote path. Returns file content as bytes."""
        url = self._build_url(
            "/api/v0/user/{username}/files/path{remote_path}",
            username=username,
            remote_path=remote_path,
        )
        response = self.session.get(url)
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {remote_path}")
        try:
            response.raise_for_status()
        except Exception as e:
            raise APIError(f"Download failed: {response.status_code} {response.text}") from e
        return response.content

    def delete(self, username: str, remote_path: str) -> None:
        """Delete a file or directory at remote path."""
        url = self._build_url(
            "/api/v0/user/{username}/files/path{remote_path}",
            username=username,
            remote_path=remote_path,
        )
        response = self.session.delete(url)
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {remote_path}")
        try:
            response.raise_for_status()
        except Exception as e:
            raise APIError(f"Delete failed: {response.status_code} {response.text}") from e

    def share(self, username: str, remote_path: str) -> str:
        """Share a file and return the share URL."""
        response = self._request(
            "POST",
            "/api/v0/user/{username}/files/sharing/",
            username=username,
            json={"path": remote_path},
        )
        return response.json()["url"]

    def unshare(self, username: str, remote_path: str) -> None:
        """Stop sharing a file."""
        self._request(
            "DELETE",
            "/api/v0/user/{username}/files/sharing/",
            username=username,
            params={"path": remote_path},
        )

    def get_share_status(self, username: str, remote_path: str) -> str:
        """Get share status for a file. Returns share URL or raises NotFoundError."""
        response = self._request(
            "GET",
            "/api/v0/user/{username}/files/sharing/",
            username=username,
            params={"path": remote_path},
        )
        return response.json()["url"]
