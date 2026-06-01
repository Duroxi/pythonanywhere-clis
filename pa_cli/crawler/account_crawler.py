import requests
from bs4 import BeautifulSoup


class AccountCrawler:
    def __init__(self, host: str = "www.pythonanywhere.com"):
        self.base_url = f"https://{host}"
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

    def get_token(self, username: str) -> str:
        account_url = f"{self.base_url}/user/{username}/account/"

        try:
            resp = self.session.get(account_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch account page: {e}") from e

        soup = BeautifulSoup(resp.text, "html.parser")
        for inp in soup.find_all("input"):
            name = inp.get("name", "")
            if "token" in name.lower():
                value = inp.get("value", "")
                if len(value) >= 32:
                    return value

        raise Exception("API token not found on account page")

    def refresh(self, username: str) -> bool:
        webapps_url = f"{self.base_url}/user/{username}/webapps/"

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

        try:
            extend_resp = self.session.post(extend_url, data=data)
        except requests.RequestException as e:
            raise Exception(f"Extend request failed: {e}") from e

        return extend_resp.status_code in (200, 302)
