import re

import typer

from pa_cli.api.webapps import WebappsClient
from pa_cli.config import Config
from pa_cli.crawler.account_crawler import AccountCrawler

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


def _get_client() -> tuple:
    account = Config.load(verbose=True)
    client = WebappsClient(token=account["token"], host=account["host"])
    return account, client


@app.command()
def create(
    domain_name: str = typer.Argument(..., help="Domain name"),
    python_version: str = typer.Option("python310", "--python", "-p", help="Python version"),
):
    """Create a new web app."""
    account, client = _get_client()
    client.create(account["username"], domain_name, python_version)
    typer.echo(f"Webapp {domain_name} created with {python_version}")


@app.command()
def config(
    domain_name: str = typer.Argument(..., help="Domain name"),
    source_dir: str = typer.Option(..., "--source-dir", "-s", help="Source directory path"),
    virtualenv: str = typer.Option(None, "--virtualenv", "-v", help="Virtualenv path"),
):
    """Configure a web app."""
    account, client = _get_client()
    kwargs = {"source_directory": _fix_remote_path(source_dir)}
    if virtualenv:
        kwargs["virtualenv_path"] = _fix_remote_path(virtualenv)
    client.update(account["username"], domain_name, **kwargs)
    typer.echo(f"Webapp {domain_name} configured.")


@app.command()
def static(
    domain_name: str = typer.Argument(..., help="Domain name"),
    url: str = typer.Option(..., "--url", help="URL prefix"),
    path: str = typer.Option(..., "--path", help="Directory path"),
):
    """Add a static file mapping."""
    account, client = _get_client()
    fixed_path = _fix_remote_path(path)
    client.add_static_file(account["username"], domain_name, url=url, path=fixed_path)
    typer.echo(f"Static mapping added: {url} -> {fixed_path}")


@app.command()
def reload(
    domain_name: str = typer.Argument(..., help="Domain name"),
):
    """Reload a web app."""
    account, client = _get_client()
    client.reload(account["username"], domain_name)
    typer.echo(f"Webapp {domain_name} reloaded.")


@app.command("hits")
def hits(
    domain_name: str = typer.Argument(..., help="Domain name"),
):
    """Get web app hit statistics via crawler."""
    try:
        account = Config.load(verbose=True)
        crawler = AccountCrawler()
        crawler.login()
        data = crawler.get_hits(domain_name)
        typer.echo(f"Hit statistics for {domain_name}:")
        for key, value in data.items():
            typer.echo(f"  {key}: {value}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("reload-crawler")
def reload_crawler(
    domain_name: str = typer.Argument(..., help="Domain name"),
):
    """Reload a web app via crawler (alternative to API reload)."""
    try:
        account = Config.load(verbose=True)
        crawler = AccountCrawler()
        crawler.login()
        if crawler.reload_webapp(domain_name):
            typer.echo(f"Webapp {domain_name} reloaded successfully.")
        else:
            typer.echo(f"Failed to reload webapp {domain_name}.", err=True)
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
