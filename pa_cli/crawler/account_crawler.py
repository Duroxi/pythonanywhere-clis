import requests
from bs4 import BeautifulSoup

from pa_cli.config import Config
from pa_cli.exceptions import APIError, AuthError, NetworkError, NotFoundError


class AccountCrawler:
    def __init__(self, username: str | None = None, host: str | None = None):
        config = Config.load()
        self.username = username or config["username"]
        resolved_host = host or config.get("host", "www.pythonanywhere.com")
        self.base_url = f"https://{resolved_host}"
        self.session = requests.Session()
        self.session.headers.update({
            "Host": resolved_host,
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/login/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        })

    def register(self, username: str, email: str, password: str) -> bool:
        register_url = f"{self.base_url}/registration/register/beginner/"

        try:
            register_page_resp = self.session.get(register_url)
            register_page_resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch registration page: {e}") from e

        soup = BeautifulSoup(register_page_resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found on registration page")

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
            raise NetworkError(f"Registration request failed: {e}") from e

        if "/registration/register/complete/" in register_resp.url:
            return True

        # Extract error messages from the response
        soup2 = BeautifulSoup(register_resp.text, "html.parser")
        errors = []
        for elem in soup2.find_all(["li", "div", "span", "p"], class_=True):
            classes = " ".join(elem.get("class", []))
            if "error" in classes.lower():
                text = elem.get_text(strip=True)
                if text:
                    errors.append(text)
        if errors:
            raise AuthError(f"Registration failed: {'; '.join(errors)}")
        raise AuthError("Registration failed. Please check your input.")

    def login(self, password: str | None = None) -> bool:
        if password is None:
            config = Config.load()
            password = config.get("password")
            if not password:
                raise AuthError(
                    "Password not found in config. Run 'pa account login' to store it."
                )

        login_url = f"{self.base_url}/login/"

        try:
            login_page_resp = self.session.get(login_url)
            login_page_resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch login page: {e}") from e

        soup = BeautifulSoup(login_page_resp.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found on login page")

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
            raise NetworkError(f"Login request failed: {e}") from e

        if "/login/" in login_resp.url:
            soup2 = BeautifulSoup(login_resp.text, "html.parser")
            # Extract error message from <p> tags
            for p in soup2.find_all("p"):
                text = p.get_text(strip=True)
                if "incorrect" in text.lower() or "invalid" in text.lower():
                    raise AuthError(f"Login failed: {text}")
            raise AuthError("Login failed. Check your username and password.")

        return True

    def get_token(self, username: str | None = None) -> str:
        resolved = username or self.username
        account_url = f"{self.base_url}/user/{resolved}/account/"

        try:
            resp = self.session.get(account_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch account page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for <code class="api_token"> element
        token_elem = soup.find("code", class_="api_token")
        if token_elem:
            return token_elem.text.strip()

        raise NotFoundError("API token not found on account page")

    def create_token(self, username: str | None = None) -> str:
        """Create a new API token via the account page form."""
        resolved = username or self.username
        account_url = f"{self.base_url}/user/{resolved}/account/"

        try:
            resp = self.session.get(account_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch account page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form", action=lambda a: a and "new_token" in a)
        if form is None:
            raise NotFoundError("Token creation form not found on account page")

        csrf_input = form.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found in token creation form")

        post_url = form["action"]
        if not post_url.startswith("http"):
            post_url = f"{self.base_url}{post_url}"

        data = {"csrfmiddlewaretoken": csrf_input["value"]}
        headers = {"Referer": account_url}

        try:
            post_resp = self.session.post(post_url, data=data, headers=headers)
        except requests.RequestException as e:
            raise NetworkError(f"Token creation request failed: {e}") from e

        if post_resp.status_code not in (200, 302):
            raise APIError(f"Token creation failed: HTTP {post_resp.status_code}")

        # Re-fetch account page to read the newly created token
        try:
            resp2 = self.session.get(account_url)
            resp2.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch account page after token creation: {e}") from e

        soup2 = BeautifulSoup(resp2.text, "html.parser")
        token_elem = soup2.find("code", class_="api_token")
        if token_elem:
            return token_elem.text.strip()

        raise APIError("Token created but could not be read from account page")

    def extend_expiry(self, username: str | None = None) -> bool:
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            if resp.status_code != 200:
                raise APIError(f"Webapps page returned HTTP {resp.status_code}")
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch webapps page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        extend_form = None
        for form in soup.find_all("form"):
            action = form.get("action", "")
            if "extend" in action:
                extend_form = form
                break

        if extend_form is None:
            raise NotFoundError("Extend form not found on webapps page")

        csrf_input = extend_form.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found in extend form")

        extend_url = extend_form["action"]
        if not extend_url.startswith("http"):
            extend_url = f"{self.base_url}{extend_url}"

        data = {"csrfmiddlewaretoken": csrf_input["value"]}
        headers = {"Referer": webapps_url}

        try:
            extend_resp = self.session.post(extend_url, data=data, headers=headers)
        except requests.RequestException as e:
            raise NetworkError(f"Extend request failed: {e}") from e

        return extend_resp.status_code in (200, 302)

    def get_expiry_date(self, username: str | None = None) -> str | None:
        """Get account expiry date from webapps page. Returns text or None."""
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            if resp.status_code != 200:
                return None
        except requests.RequestException:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        expiry_elem = soup.find("p", class_="webapp_expiry")
        if expiry_elem:
            return expiry_elem.get_text(strip=True)
        return None

    def reload_webapp(self, domain: str, username: str | None = None) -> bool:
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch webapps page: {e}") from e

        csrf_token = self.session.cookies.get("csrftoken")
        if csrf_token is None:
            raise APIError("CSRF token not found in cookies")

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
            raise NetworkError(f"Reload request failed: {e}") from e

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
            raise NetworkError(f"Failed to fetch hits: {e}") from e

        return resp.json()

    def enable_webapp(self, domain: str, username: str | None = None) -> bool:
        """Enable a web app via web form."""
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch webapps page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        enable_form = soup.find("form", action=lambda a: a and "enable" in a)
        if enable_form is None:
            raise NotFoundError("Enable form not found (webapp may already be enabled)")

        csrf_input = enable_form.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found in enable form")

        enable_url = f"{self.base_url}{enable_form['action']}"
        data = {"csrfmiddlewaretoken": csrf_input["value"]}
        headers = {"Referer": webapps_url}

        try:
            enable_resp = self.session.post(enable_url, data=data, headers=headers)
        except requests.RequestException as e:
            raise NetworkError(f"Enable request failed: {e}") from e

        return enable_resp.status_code in (200, 302)

    def disable_webapp(self, domain: str, username: str | None = None) -> bool:
        """Disable a web app via web form."""
        resolved = username or self.username
        webapps_url = f"{self.base_url}/user/{resolved}/webapps/"

        try:
            resp = self.session.get(webapps_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch webapps page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        disable_form = soup.find("form", action=lambda a: a and "disable" in a)
        if disable_form is None:
            raise NotFoundError("Disable form not found (webapp may already be disabled)")

        csrf_input = disable_form.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            raise APIError("CSRF token not found in disable form")

        disable_url = f"{self.base_url}{disable_form['action']}"
        data = {"csrfmiddlewaretoken": csrf_input["value"]}
        headers = {"Referer": webapps_url}

        try:
            disable_resp = self.session.post(disable_url, data=data, headers=headers)
        except requests.RequestException as e:
            raise NetworkError(f"Disable request failed: {e}") from e

        return disable_resp.status_code in (200, 302)

    def get_disk_usage(self, username: str | None = None) -> dict:
        """Get disk usage information."""
        resolved = username or self.username
        quota_url = f"{self.base_url}/user/{resolved}/quota_information/"

        try:
            resp = self.session.get(quota_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch disk usage: {e}") from e

        return resp.json()
