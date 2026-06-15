import re

import typer

from pa_cli.api.webapps import WebappsClient
from pa_cli.cli.utils import get_client
from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

app = typer.Typer(help="Manage web apps on PythonAnywhere.")


def _fix_remote_path(path: str) -> str:
    """Fix paths mangled by Git Bash (MSYS2) path conversion.

    Git Bash converts /home/user/dir to D:/Git/home/user/dir.
    This function detects and reverses the conversion.
    """
    if re.match(r"^[A-Za-z]:/", path):
        match = re.search(r"(/home/\S+)", path)
        if match:
            return match.group(1)
    return path


@app.command()
def create(
    domain_name: str = typer.Argument(..., help="Domain name"),
    python_version: str = typer.Option("python310", "--python", "-p", help="Python version"),
):
    """Create a new web app."""
    account, client = get_client(WebappsClient)
    client.create(account["username"], domain_name, python_version)
    typer.echo(f"Webapp {domain_name} created with {python_version}")


@app.command()
def config(
    domain_name: str = typer.Argument(None, help="Domain name (default: {username}.pythonanywhere.com)"),
    source_dir: str = typer.Option(None, "--source-dir", "-s", help="Source directory path"),
    virtualenv: str = typer.Option(None, "--virtualenv", "-v", help="Virtualenv path"),
    python_version: str = typer.Option(None, "--python-version", "-p", help="Python version (e.g. 3.10, 3.11)"),
    working_dir: str = typer.Option(None, "--working-dir", "-w", help="Working directory path"),
):
    """Configure a web app."""
    account, client = get_client(WebappsClient)
    if domain_name is None:
        domain_name = f"{account['username']}.pythonanywhere.com"
    kwargs = {}
    if source_dir:
        kwargs["source_directory"] = _fix_remote_path(source_dir)
    if virtualenv:
        kwargs["virtualenv_path"] = _fix_remote_path(virtualenv)
    if python_version:
        kwargs["python_version"] = python_version
    if working_dir:
        kwargs["working_directory"] = _fix_remote_path(working_dir)
    if not kwargs:
        typer.echo("Error: No configuration specified. Use --source-dir, --virtualenv, --python-version, or --working-dir.", err=True)
        raise typer.Exit(code=1)
    client.update(account["username"], domain_name, **kwargs)
    typer.echo(f"Webapp {domain_name} configured.")


@app.command()
def static(
    domain_name: str = typer.Argument(..., help="Domain name"),
    url: str = typer.Option(..., "--url", help="URL prefix"),
    path: str = typer.Option(..., "--path", help="Directory path"),
):
    """Add a static file mapping."""
    account, client = get_client(WebappsClient)
    fixed_path = _fix_remote_path(path)
    client.add_static_file(account["username"], domain_name, url=url, path=fixed_path)
    typer.echo(f"Static mapping added: {url} -> {fixed_path}")


@app.command()
def reload(
    domain_name: str = typer.Argument(..., help="Domain name"),
):
    """Reload a web app."""
    account, client = get_client(WebappsClient)
    client.reload(account["username"], domain_name)
    typer.echo(f"Webapp {domain_name} reloaded.")


@app.command("hits")
def hits(
    domain_name: str = typer.Argument(None, help="Domain name (default: {username}.pythonanywhere.com)"),
):
    """Get web app hit statistics via crawler."""
    try:
        account = Config.load(verbose=True)
        if domain_name is None:
            domain_name = f"{account['username']}.pythonanywhere.com"
        crawler = AccountCrawler()
        crawler.login()
        data = crawler.get_hits(domain_name)
        typer.echo(f"Hit statistics for {domain_name}:")
        for key, value in data.items():
            typer.echo(f"  {key}: {value}")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"资源不存在: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("reload-crawler")
def reload_crawler(
    domain_name: str = typer.Argument(None, help="Domain name (default: {username}.pythonanywhere.com)"),
):
    """Reload a web app via crawler (alternative to API reload)."""
    try:
        account = Config.load(verbose=True)
        if domain_name is None:
            domain_name = f"{account['username']}.pythonanywhere.com"
        crawler = AccountCrawler()
        crawler.login()
        if crawler.reload_webapp(domain_name):
            typer.echo(f"Webapp {domain_name} reloaded successfully.")
        else:
            typer.echo(f"Failed to reload webapp {domain_name}.", err=True)
            raise typer.Exit(code=1)
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"资源不存在: {e}", err=True)
        raise typer.Exit(code=1)
