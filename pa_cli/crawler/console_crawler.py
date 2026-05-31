import re

import requests
import websocket
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

    def list(self, username: str) -> list:
        url = f"{self.base_url}/api/v0/user/{username}/consoles/"

        try:
            resp = self.session.get(url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to list consoles: {e}") from e

        return resp.json()

    def create(self, username: str, executable: str = "bash") -> dict:
        csrftoken = self.session.cookies.get("csrftoken")
        if not csrftoken:
            raise Exception("CSRF token not found in session cookies")

        url = f"{self.base_url}/api/v0/user/{username}/consoles/"
        headers = {
            "Referer": f"{self.base_url}/user/{username}/consoles/",
            "X-CSRFToken": csrftoken,
        }

        try:
            resp = self.session.post(url, json={"executable": executable}, headers=headers)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to create console: {e}") from e

        return resp.json()

    def delete(self, username: str, console_id: int) -> None:
        csrftoken = self.session.cookies.get("csrftoken")
        if not csrftoken:
            raise Exception("CSRF token not found in session cookies")

        url = f"{self.base_url}/api/v0/user/{username}/consoles/{console_id}/"
        headers = {
            "Referer": f"{self.base_url}/user/{username}/consoles/",
            "X-CSRFToken": csrftoken,
        }

        try:
            resp = self.session.delete(url, headers=headers)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to delete console: {e}") from e

    def activate(self, username: str, console_id: int) -> None:
        frame_url = f"{self.base_url}/user/{username}/consoles/{console_id}/frame/"

        try:
            resp = self.session.get(frame_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch console frame page: {e}") from e

        match = re.search(r'LoadConsole\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"', resp.text)
        if not match:
            raise Exception("Could not parse WebSocket info from frame page")

        console_server = match.group(1)
        session_key = match.group(2)
        parsed_console_id = match.group(3)

        ws = None
        try:
            ws = websocket.create_connection(f"wss://{console_server}/sj/websocket")
            ws.send(f"\x1b[{session_key};{parsed_console_id};;a")
            ws.send("\x1b[8;24;80t")
        except Exception as e:
            raise Exception(f"WebSocket connection failed: {e}") from e
        finally:
            if ws:
                ws.close()
