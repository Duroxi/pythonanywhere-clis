import time
import uuid

import typer

from pa_cli.api.consoles import ConsolesClient
from pa_cli.cli.utils import get_client
from pa_cli.config import Config
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

app = typer.Typer(help="Manage consoles on PythonAnywhere.")


@app.command("list")
def list_consoles():
    """List all consoles."""
    account, client = get_client(ConsolesClient)
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
        typer.echo(f"Auth error: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def create(
    executable: str = typer.Option("bash", help="Console executable"),
):
    """Create a new console."""
    account, client = get_client(ConsolesClient)
    result = client.create(account["username"], executable)
    typer.echo(f"Console created: id={result['id']}, executable={result['executable']}")


@app.command()
def send(
    console_id: int = typer.Argument(..., help="Console ID"),
    command: str = typer.Argument(..., help="Command to send"),
    wait: bool = typer.Option(True, "--wait/--no-wait", "-w/-W", help="Wait for output"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Max seconds to wait for output"),
):
    """Send input to a console and get output."""
    account, client = get_client(ConsolesClient)

    if not wait:
        client.send_input(account["username"], console_id, command + "\n")
        typer.echo(f"Sent to console {console_id}: {command}")
        return

    # Get baseline output before sending command
    baseline = client.get_output(account["username"], console_id)
    baseline_output = baseline.get("output", "")

    # Generate unique completion marker (timestamp + random hex)
    import time as _time
    marker = f"__PA_CLI_DONE_{int(_time.time())}_{uuid.uuid4().hex}__"

    # Send command + marker echo
    client.send_input(
        account["username"],
        console_id,
        f"{command}\necho {marker}\n",
    )

    # Poll for marker
    elapsed = 0.0
    poll_interval = 0.5
    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval
        result = client.get_output(account["username"], console_id)
        output = result.get("output", "")

        if marker in output and output != baseline_output:
            # Extract new content (after baseline)
            new_output = output[len(baseline_output):]
            # Find and remove marker line
            lines = new_output.split("\n")
            user_lines = []
            for line in lines:
                if marker in line:
                    break
                user_lines.append(line)
            typer.echo("\n".join(user_lines).strip() or "(no output)")
            return

    typer.echo("Timeout waiting for command output", err=True)
    raise typer.Exit(code=1)


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
        typer.echo(f"Auth error: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def kill(
    console_id: int = typer.Argument(..., help="Console ID"),
):
    """Kill a console."""
    account, client = get_client(ConsolesClient)
    client.kill(account["username"], console_id)
    typer.echo(f"Console {console_id} killed.")
