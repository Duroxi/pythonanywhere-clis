import typer

from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler

app = typer.Typer(help="Account management commands.")


@app.command()
def switch(
    username: str = typer.Argument(..., help="Username to switch to"),
):
    """Switch the default account."""
    try:
        Config.set_default(username)
        typer.echo(f"Switched to account '{username}'.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def remove(
    username: str = typer.Argument(..., help="Username to remove"),
):
    """Remove an account from config."""
    try:
        new_default = Config.remove(username)
        typer.echo(f"Removed account '{username}'.")
        if new_default:
            typer.echo(f"Switched to account '{new_default}'.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("list")
def list_accounts():
    """List all configured accounts."""
    accounts = Config.list_accounts()
    if not accounts:
        typer.echo("No accounts configured. Run 'pa init' to add one.")
        return

    try:
        current = Config.load()
        current_user = current["username"]
    except (FileNotFoundError, ValueError):
        current_user = ""

    for account in accounts:
        prefix = "* " if account["username"] == current_user else "  "
        token = account.get("token", "")
        token_display = f"token: {token[:8]}..." if token else "(no token)"
        host = account.get("host", "www.pythonanywhere.com")
        typer.echo(f"{prefix}{account['username']}    {host}    {token_display}")


@app.command()
def login():
    """Store password for the current account."""
    password = typer.prompt("Password", hide_input=True)
    Config.save(password=password)
    typer.echo("Password saved successfully.")


@app.command()
def token(
    revoke: bool = typer.Option(False, "--revoke", "-r", help="Revoke current token and create a new one"),
):
    """Get API token. Creates one automatically if none exists. Use --revoke to force refresh."""
    try:
        crawler = AccountCrawler()
        if not crawler.login():
            typer.echo("Login failed. Check your credentials.", err=True)
            raise typer.Exit(code=1)

        if revoke:
            new_token = crawler.create_token()
            Config.save(token=new_token)
            typer.echo(f"Token revoked. New token: {new_token}")
        else:
            try:
                existing = crawler.get_token()
                Config.save(token=existing)
                typer.echo(f"API token: {existing}")
            except Exception:
                new_token = crawler.create_token()
                Config.save(token=new_token)
                typer.echo(f"Token created: {new_token}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def extend():
    """Extend account expiry by logging in via crawler."""
    try:
        crawler = AccountCrawler()
        if not crawler.login():
            typer.echo("Login failed. Check your credentials.", err=True)
            raise typer.Exit(code=1)
        if crawler.extend_expiry():
            typer.echo("Account expiry extended successfully.")
        else:
            typer.echo("Failed to extend account expiry.", err=True)
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

