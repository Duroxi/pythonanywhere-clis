import typer

from pa_cli.api.consoles import ConsolesClient
from pa_cli.config import Config
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

app = typer.Typer(help="Manage consoles on PythonAnywhere.")


def _get_client() -> tuple:
    account = Config.load(verbose=True)
    client = ConsolesClient(token=account["token"], host=account["host"])
    return account, client


@app.command("list")
def list_consoles():
    """List all consoles."""
    account, client = _get_client()
    consoles = client.list(account["username"])
    if not consoles:
        typer.echo("No consoles found.")
        return
    for console in consoles:
        typer.echo(f"ID: {console['id']}, Name: {console['name']}")


@app.command()
def activate(
    console_id: int = typer.Argument(..., help="Console ID"),
):
    """Activate a console via WebSocket (requires login)."""
    try:
        from pa_cli.crawler.console_crawler import ConsoleCrawler

        account = Config.load(verbose=True)

        if "password" not in account:
            typer.echo("Password not found. Run 'pa account login' first.", err=True)
            raise typer.Exit(code=1)

        crawler = ConsoleCrawler(host=account.get("host", "www.pythonanywhere.com"))
        crawler.login(account["username"], account["password"])
        crawler.activate(account["username"], console_id)
        typer.echo(f"Console {console_id} activated successfully.")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def create(
    executable: str = typer.Option("bash", help="Console executable"),
):
    """Create a new console."""
    account, client = _get_client()
    result = client.create(account["username"], executable)
    typer.echo(f"Console created: id={result['id']}, executable={result['executable']}")


@app.command()
def send(
    console_id: int = typer.Argument(..., help="Console ID"),
    command: str = typer.Argument(..., help="Command to send"),
    wait: bool = typer.Option(True, "--wait/--no-wait", "-w/-W", help="Wait for output"),
):
    """Send input to a console and get output."""
    import time
    account, client = _get_client()
    client.send_input(account["username"], console_id, command + "\n")

    if not wait:
        typer.echo(f"Sent to console {console_id}: {command}")
        return

    # Wait for output
    time.sleep(1)
    result = client.get_output(account["username"], console_id)
    output = result.get("output", "(no output)")
    typer.echo(output)


@app.command("get-or-create")
def get_or_create(
    executable: str = typer.Option("bash", "--executable", "-e", help="Console executable"),
):
    """Get an existing console or create a new one (auto-manage lifecycle)."""
    try:
        from pa_cli.crawler.console_crawler import ConsoleCrawler

        account = Config.load(verbose=True)

        if "password" not in account:
            typer.echo("Password not found. Run 'pa account login' first.", err=True)
            raise typer.Exit(code=1)

        crawler = ConsoleCrawler(host=account.get("host", "www.pythonanywhere.com"))
        crawler.login(account["username"], account["password"])
        console_id = crawler.get_or_create(account["username"], executable=executable)
        typer.echo(f"Console ready: {console_id}")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def kill(
    console_id: int = typer.Argument(..., help="Console ID"),
):
    """Kill a console."""
    account, client = _get_client()
    client.kill(account["username"], console_id)
    typer.echo(f"Console {console_id} killed.")
