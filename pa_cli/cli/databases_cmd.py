import typer

from pa_cli.api.databases import DatabasesClient
from pa_cli.cli.utils import get_client
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

app = typer.Typer(help="Manage databases on PythonAnywhere.")


@app.command("mysql")
def mysql_info():
    """Show MySQL database information."""
    try:
        account, client = get_client(DatabasesClient)
        data = client.get_mysql_info(account["username"])
        if not data:
            typer.echo("No MySQL databases found.")
            return
        typer.echo("MySQL Databases:")
        for db in data:
            name = db.get("database_name", "N/A")
            size = db.get("size", "N/A")
            typer.echo(f"  {name}: {size}")
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
