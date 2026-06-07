import requests

from pa_cli.exceptions import APIError, NetworkError, NotFoundError


class BaseClient:
    def __init__(self, token: str, host: str = "www.pythonanywhere.com"):
        self.host = host
        self.base_url = f"https://{host}"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {token}"})

    def _build_url(self, path: str, **kwargs) -> str:
        return f"{self.base_url}{path.format(**kwargs)}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._build_url(path, **kwargs)

        # Extract path params from kwargs (used in URL formatting)
        path_params = {k for k in kwargs if "{" + k + "}" in path}
        request_kwargs = {k: v for k, v in kwargs.items() if k not in path_params}

        try:
            response = self.session.request(method, url, **request_kwargs)
        except requests.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except requests.Timeout as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {e}") from e

        if response.status_code == 404:
            raise NotFoundError(f"Not found: {path}")

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            detail = ""
            try:
                detail = response.json().get("detail", "")
            except Exception:
                detail = response.text
            raise APIError(f"API error {response.status_code}: {detail}") from e

        return response
