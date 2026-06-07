class PACliError(Exception):
    """Base exception for all pa-cli errors."""


class AuthError(PACliError):
    """Authentication failed (login, token, password)."""


class APIError(PACliError):
    """PythonAnywhere API returned an error."""


class NotFoundError(APIError):
    """Requested resource does not exist (404)."""


class NetworkError(PACliError):
    """Network connection failed."""
