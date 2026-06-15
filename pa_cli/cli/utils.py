from typing import Type, TypeVar, Tuple

from pa_cli.config import Config
from pa_cli.api.client import BaseClient

T = TypeVar("T", bound=BaseClient)


def get_client(client_class: Type[T]) -> Tuple[dict, T]:
    """Load config and create API client."""
    account = Config.load(verbose=True)
    client = client_class(token=account["token"], host=account["host"])
    return account, client
