import requests
from bs4 import BeautifulSoup

from pa_cli.config import Config


class AccountCrawler:
    def __init__(self, username: str | None = None, host: str | None = None):
        config = Config.load()
        self.username = username or config["username"]
        resolved_host = host or config.get("host", "www.pythonanywhere.com")
        self.base_url = f"https://{resolved_host}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def register(self, username: str, email: str, password: str) -> bool:
        register_url = f"{self.base_url}/registration/register/beginner/"

        try:
            register_page_resp = self.session.get(register_url)
            register_page_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch registration page: {e}") from e

        soup = BeautifulSoup(register_page_resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise Exception("CSRF token not found on registration page")

        data = {
            "csrfmiddlewaretoken": csrf_input["value"],
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
            "tos": "on",
            "recaptcha_response_token_v3": "",
        }

        headers = {
            "Referer": register_url,
            "Origin": self.base_url,
        }

        try:
            register_resp = self.session.post(register_url, data=data, headers=headers)
            register_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Registration request failed: {e}") from e

        return "/registration/register/complete/" in register_resp.url

    def login(self, password: str | None = None) -> bool:
        if password is None:
            config = Config.load()
            password = config.get("password")
            if not password:
                raise ValueError(
                    "Password not found in config. Run 'pa account login' to store it."
                )

        login_url = f"{self.base_url}/login/"

        try:
            login_page_resp = self.session.get(login_url)
            login_page_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch login page: {e}") from e

        soup = BeautifulSoup(login_page_resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise Exception("CSRF token not found on login page")

        data = {
            "csrfmiddlewaretoken": csrf_input["value"],
            "auth-username": self.username,
            "auth-password": password,
            "login_view-current_step": "auth",
        }

        headers = {
            "Referer": login_url,
            "Origin": self.base_url,
        }

        try:
            login_resp = self.session.post(login_url, data=data, headers=headers)
            login_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}") from e

        return "/login/" not in login_resp.url

    def get_token(self, username: str | None = None) -> str:
        resolved = username or self.username
        account_url = f"{self.base_url}/user/{resolved}/account/"

        try:
            resp = self.session.get(account_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch account page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for <code class="api_token"> element
        token_elem = soup.find("code", class_="api_token")
        if token_elem:
            return token_elem.text.strip()

        raise Exception("API token not found on account page")

    def extend_expiry(self, username: str | None = None) -> bool:
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch webapps page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        extend_form = None
        for form in soup.find_all("form"):
            action = form.get("action", "")
            if "extend" in action:
                extend_form = form
                break

        if extend_form is None:
            raise Exception("Extend form not found on webapps page")

        csrf_input = extend_form.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise Exception("CSRF token not found in extend form")

        extend_url = extend_form["action"]
        if not extend_url.startswith("http"):
            extend_url = f"{self.base_url}{extend_url}"

        data = {"csrfmiddlewaretoken": csrf_input["value"]}
        headers = {"Referer": webapps_url}

        try:
            extend_resp = self.session.post(extend_url, data=data, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Extend request failed: {e}") from e

        return extend_resp.status_code in (200, 302)

    def reload_webapp(self, domain: str, username: str | None = None) -> bool:
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch webapps page: {e}") from e

        csrf_token = self.session.cookies.get("csrftoken")
        if csrf_token is None:
            raise Exception("CSRF token not found in cookies")

        reload_url = f"{self.base_url}/user/{resolved}/webapps/{domain}/reload"
        headers = {
            "X-CSRFToken": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": webapps_url,
            "Origin": self.base_url,
        }

        try:
            reload_resp = self.session.post(reload_url, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Reload request failed: {e}") from e

        return reload_resp.text == "OK"

    def get_hits(self, domain: str, username: str | None = None) -> dict:
        resolved = username or self.username
        hits_url = f"{self.base_url}/user/{resolved}/webapps/{domain}/hits_summary/"
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": webapps_url,
        }

        try:
            resp = self.session.get(hits_url, headers=headers)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch hits: {e}") from e

        return resp.json()
