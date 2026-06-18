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
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"资源不存在: {e}", err=True)
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
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"资源不存在: {e}", err=True)
        raise typer.Exit(code=1)
