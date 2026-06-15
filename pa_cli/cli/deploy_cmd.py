import typer

from pa_cli.config import Config
from pa_cli.exceptions import PACliError, APIError, NetworkError
from pa_cli.workflows.deploy import deploy as deploy_workflow

app = typer.Typer(help="Deploy a local project to PythonAnywhere.")


@app.command()
def deploy(
    local_dir: str = typer.Argument(..., help="Local project directory"),
    domain: str = typer.Option(None, "--domain", "-d", help="Domain name (default: {username}.pythonanywhere.com)"),
    python_version: str = typer.Option("python310", "--python", "-p", help="Python version"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview deploy without executing"),
):
    """Deploy a local project to PythonAnywhere."""
    try:
        account = Config.load(verbose=True)

        if domain is None:
            domain = f"{account['username']}.pythonanywhere.com"

        url = deploy_workflow(
            local_dir=local_dir,
            username=account["username"],
            token=account["token"],
            host=account["host"],
            domain=domain,
            python_version=python_version,
            dry_run=dry_run,
        )

        if not dry_run:
            typer.echo(f"\nDeployed! Visit: {url}")
    except PACliError as e:
        typer.echo(f"部署失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API 错误: {e}", err=True)
        raise typer.Exit(code=1)
