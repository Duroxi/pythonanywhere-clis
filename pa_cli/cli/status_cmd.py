import typer

from pa_cli.api.system import SystemClient
from pa_cli.cli.utils import get_client
from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

app = typer.Typer(help="Query system status and resource usage.")


@app.command()
def cpu():
    """Show CPU usage."""
    try:
        account, client = get_client(SystemClient)
        data = client.get_cpu_usage(account["username"])
        used = data.get("daily_cpu_total_usage_seconds", 0)
        limit = data.get("daily_cpu_limit_seconds", 0)
        reset = data.get("next_reset_time", "N/A")
        typer.echo(f"CPU Usage:")
        typer.echo(f"  Used: {used} seconds")
        typer.echo(f"  Limit: {limit} seconds")
        typer.echo(f"  Reset: {reset}")
    except AuthError as e:
        typer.echo(f"Auth error: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"Not found: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def disk():
    """Show disk usage."""
    try:
        account = Config.load(verbose=True)
        crawler = AccountCrawler()
        crawler.login()
        data = crawler.get_disk_usage(account["username"])
        used = data.get("used", "N/A")
        quota = data.get("quota", "N/A")
        percent = data.get("percent", "N/A")
        typer.echo(f"Disk Usage:")
        typer.echo(f"  Used: {used}")
        typer.echo(f"  Total: {quota}")
        typer.echo(f"  Usage: {percent}")
    except AuthError as e:
        typer.echo(f"Auth error: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"Not found: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("system-image")
def system_image(
    image: str = typer.Argument(None, help="System image to set"),
):
    """Get or set system image."""
    try:
        account, client = get_client(SystemClient)
        if image:
            client.set_system_image(account["username"], image)
            typer.echo(f"System image set to {image}")
        else:
            data = client.get_system_image(account["username"])
            current = data.get("system_image", "N/A")
            available = data.get("available_system_images", [])
            typer.echo(f"Current system image: {current}")
            if available:
                typer.echo(f"Available images: {', '.join(available)}")
    except AuthError as e:
        typer.echo(f"Auth error: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"Not found: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)
