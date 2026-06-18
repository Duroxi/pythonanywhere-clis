import typer

from pa_cli.api.always_on import AlwaysOnClient
from pa_cli.cli.utils import get_client
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

app = typer.Typer(help="Manage always-on tasks on PythonAnywhere.")


@app.command("list")
def list_tasks():
    """List all always-on tasks."""
    try:
        account, client = get_client(AlwaysOnClient)
        tasks = client.list(account["username"])
        if not tasks:
            typer.echo("No always-on tasks found.")
            return
        for task in tasks:
            status = "enabled" if task.get("enabled") else "disabled"
            typer.echo(f"ID: {task['id']}, Command: {task['command']}, Status: {status}")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API 错误: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def create(
    command: str = typer.Argument(..., help="Command to run"),
):
    """Create a new always-on task."""
    try:
        account, client = get_client(AlwaysOnClient)
        task = client.create(account["username"], command=command)
        typer.echo(f"Always-on task created: ID={task['id']}, Command={task['command']}")
    except APIError as e:
        if "limit" in str(e).lower():
            typer.echo("Error: Always-on task limit reached. Upgrade your plan to add more.", err=True)
        else:
            typer.echo(f"API 错误: {e}", err=True)
        raise typer.Exit(code=1)
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def delete(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation"),
):
    """Delete an always-on task."""
    try:
        account, client = get_client(AlwaysOnClient)
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete always-on task {task_id}?")
            if not confirm:
                typer.echo("Cancelled.")
                raise typer.Exit()
        client.delete(account["username"], task_id)
        typer.echo(f"Always-on task {task_id} deleted.")
    except AuthError as e:
        typer.echo(f"认证失败: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"网络错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotFoundError as e:
        typer.echo(f"任务不存在: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API 错误: {e}", err=True)
        raise typer.Exit(code=1)
