import requests
from bs4 import BeautifulSoup


class ConsoleCrawler:
    def __init__(self, host: str = "www.pythonanywhere.com"):
        self.base_url = f"https://{host}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def login(self, username: str, password: str) -> bool:
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
            "auth-username": username,
            "auth-password": password,
            "login_view-current_step": "auth",
        }

        try:
            login_resp = self.session.post(login_url, data=data)
            login_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}") from e

        return "/login/" not in login_resp.url
