import typer

from pa_cli.api.tasks import TasksClient
from pa_cli.cli.utils import get_client
from pa_cli.exceptions import AuthError, NetworkError, NotFoundError, APIError

app = typer.Typer(help="Manage scheduled tasks on PythonAnywhere.")


@app.command("list")
def list_tasks():
    """List all scheduled tasks."""
    try:
        account, client = get_client(TasksClient)
        tasks = client.list(account["username"])
        if not tasks:
            typer.echo("No scheduled tasks found.")
            return
        for task in tasks:
            status = "enabled" if task.get("enabled") else "disabled"
            typer.echo(f"ID: {task['id']}, Command: {task['command']}, "
                       f"Interval: {task['interval']}, Status: {status}")
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
    command: str = typer.Argument(..., help="Command to execute"),
    interval: str = typer.Option("daily", "--interval", "-i", help="Interval: hourly, daily, weekly, monthly"),
    hour: int = typer.Option(0, "--hour", "-H", help="Hour to run (0-23)"),
    minute: int = typer.Option(0, "--minute", "-M", help="Minute to run (0-59)"),
    description: str = typer.Option("", "--description", "-d", help="Task description"),
):
    """Create a new scheduled task."""
    try:
        account, client = get_client(TasksClient)
        task = client.create(
            account["username"],
            command=command,
            interval=interval,
            hour=hour,
            minute=minute,
            description=description,
        )
        typer.echo(f"Task created: ID={task['id']}, Command={task['command']}")
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
def delete(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation"),
):
    """Delete a scheduled task."""
    try:
        account, client = get_client(TasksClient)
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete task {task_id}?")
            if not confirm:
                typer.echo("Cancelled.")
                raise typer.Exit()
        client.delete(account["username"], task_id)
        typer.echo(f"Task {task_id} deleted.")
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


@app.command()
def enable(
    task_id: int = typer.Argument(..., help="Task ID to enable"),
):
    """Enable a scheduled task."""
    try:
        account, client = get_client(TasksClient)
        client.update(account["username"], task_id, enabled=True)
        typer.echo(f"Task {task_id} enabled.")
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


@app.command()
def disable(
    task_id: int = typer.Argument(..., help="Task ID to disable"),
):
    """Disable a scheduled task."""
    try:
        account, client = get_client(TasksClient)
        client.update(account["username"], task_id, enabled=False)
        typer.echo(f"Task {task_id} disabled.")
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
