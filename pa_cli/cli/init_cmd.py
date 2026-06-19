import typer

from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

app = typer.Typer(help="Configure PythonAnywhere account.")


@app.callback(invoke_without_command=True)
def init_callback(
    ctx: typer.Context,
    username: str = typer.Option(None, "--username", "-u", help="PythonAnywhere username"),
    password: str = typer.Option(None, "--password", "-p", help="Account password"),
    host: str = typer.Option("www.pythonanywhere.com", "--host", "-h", help="PythonAnywhere host"),
):
    """Interactive setup for PythonAnywhere account.

    Examples:
        pa init                                    # Interactive mode
        pa init -u myuser -p mypass                # Command-line mode
        pa init -u myuser -p mypass -h eu.pythonanywhere.com
    """
    if ctx.invoked_subcommand is not None:
        return

    # Use command-line args if provided, otherwise prompt interactively
    if username is None:
        username = typer.prompt("PythonAnywhere username")
    if password is None:
        password = typer.prompt("Password", hide_input=True)

    # Save credentials to config first so AccountCrawler can read them
    Config.save(username=username, password=password, host=host)

    # Auto-login and fetch API token
    try:
        crawler = AccountCrawler()
        crawler.login()

        # Try to get existing token, create one if it doesn't exist
        try:
            token = crawler.get_token()
            Config.save(token=token)
            typer.echo(f"Account '{username}' configured successfully.")
            typer.echo(f"API token: {token}")
        except NotFoundError:
            token = crawler.create_token()
            Config.save(token=token)
            typer.echo(f"Account '{username}' configured successfully.")
            typer.echo(f"Token created: {token}")
    except AuthError as e:
        typer.echo(f"Auth error: {e}", err=True)
        typer.echo("Don't have an account? Register with: pa register", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"Not found: {e}", err=True)
        raise typer.Exit(code=1)
