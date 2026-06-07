import typer

from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError

app = typer.Typer(help="Configure PythonAnywhere account.")


@app.command()
def init():
    """Interactive setup for PythonAnywhere account."""
    username = typer.prompt("PythonAnywhere username")
    password = typer.prompt("Password", hide_input=True)
    host = typer.prompt("Host", default="www.pythonanywhere.com")

    # Save credentials to config first so AccountCrawler can read them
    Config.save(username=username, password=password, host=host)

    # Auto-login and fetch API token
    try:
        crawler = AccountCrawler()
        crawler.login()
        token = crawler.get_token()
        Config.save(token=token)
        typer.echo(f"Account '{username}' configured successfully.")
        typer.echo("API token fetched and saved.")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        typer.echo("Don't have an account? Register with: pa register", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"资源不存在: {e}", err=True)
        raise typer.Exit(code=1)
