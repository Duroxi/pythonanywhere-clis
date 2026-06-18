from pathlib import Path

import typer

from pa_cli.api.files import FilesClient
from pa_cli.cli.utils import get_client, fix_remote_path
from pa_cli.exceptions import APIError, NetworkError, NotFoundError

app = typer.Typer(help="Manage files on PythonAnywhere.")


@app.callback()
def main():
    """Manage files on PythonAnywhere."""
    pass


def _resolve_path(path: str | None, username: str) -> str:
    """Resolve remote path. Relative paths are under /home/{username}/."""
    if not path:
        return f"/home/{username}/"
    path = fix_remote_path(path)
    if path.startswith("/"):
        return path if path.endswith("/") else path + "/"
    return f"/home/{username}/{path}".rstrip("/") + "/"


@app.command("ls")
def ls(
    path: str = typer.Argument(None, help="Remote path to list (default: home directory)"),
):
    """List files and directories on PythonAnywhere."""
    try:
        account, client = get_client(FilesClient)

        remote_path = _resolve_path(path, account["username"])
        items = client.list(account["username"], remote_path)

        if not items:
            typer.echo("(empty directory)")
            return

        for name in sorted(items.keys()):
            item_type = items[name].get("type", "file")
            if item_type == "directory":
                typer.echo(f"  {name}/")
            else:
                typer.echo(f"  {name}")
    except NotFoundError as e:
        typer.echo(f"Path not found: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def download(
    remote_path: str = typer.Argument(..., help="Remote path to download"),
    local_path: str = typer.Argument(None, help="Local destination (default: current directory)"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Download directory recursively"),
):
    """Download a file or directory from PythonAnywhere."""
    try:
        account, client = get_client(FilesClient)

        resolved = _resolve_path(remote_path, account["username"])

        # Check if remote is a directory by listing its parent
        parent = resolved.rsplit("/", 2)[0] + "/"
        name = resolved.rstrip("/").rsplit("/", 1)[-1]
        parent_items = client.list(account["username"], parent)

        is_directory = False
        if name in parent_items:
            is_directory = parent_items[name].get("type") == "directory"

        if is_directory and not recursive:
            typer.echo("Error: Use -r/--recursive to download directories")
            raise typer.Exit(code=1)

        if is_directory:
            target_dir = Path(local_path) if local_path else Path(name)
            target_dir.mkdir(parents=True, exist_ok=True)
            count = _download_recursive(client, account["username"], resolved, target_dir)
            typer.echo(f"Downloaded {count} files to {target_dir}")
        else:
            file_path = resolved.rstrip("/")
            content = client.download(account["username"], file_path)
            target = Path(local_path) if local_path else Path(file_path.split("/")[-1])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            typer.echo(f"Downloaded {remote_path} -> {target}")
    except NotFoundError as e:
        typer.echo(f"File not found: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


def _download_recursive(client, username, remote_dir, local_dir):
    """Recursively download a directory. Returns file count."""
    items = client.list(username, remote_dir)
    count = 0
    for name, info in items.items():
        remote = f"{remote_dir.rstrip('/')}/{name}"
        local = local_dir / name
        if info.get("type") == "directory":
            local.mkdir(parents=True, exist_ok=True)
            count += _download_recursive(client, username, remote + "/", local)
        else:
            content = client.download(username, remote)
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(content)
            count += 1
    return count


@app.command()
def upload(
    local_path: str = typer.Argument(..., help="Local file or directory path"),
    remote_path: str = typer.Argument(..., help="Remote path on PythonAnywhere"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Upload directory recursively"),
):
    """Upload a file or directory to PythonAnywhere."""
    local = Path(local_path)

    if not local.exists():
        typer.echo(f"Error: {local_path} does not exist")
        raise typer.Exit(code=1)

    if local.is_dir() and not recursive:
        typer.echo("Error: Use -r/--recursive to upload directories")
        raise typer.Exit(code=1)

    try:
        account, client = get_client(FilesClient)

        if local.is_file():
            content = local.read_bytes()
            status = client.upload(account["username"], remote_path, content)
            typer.echo(f"Uploaded {local_path} -> {remote_path} (HTTP {status})")
        else:
            # Recursive directory upload
            count = 0
            for file in local.rglob("*"):
                if file.is_file():
                    relative = file.relative_to(local)
                    remote = f"{remote_path.rstrip('/')}/{relative}".replace("\\", "/")
                    content = file.read_bytes()
                    client.upload(account["username"], remote, content)
                    count += 1
            typer.echo(f"Uploaded {count} files to {remote_path}")
    except NotFoundError as e:
        typer.echo(f"Path not found: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def rm(
    path: str = typer.Argument(..., help="Remote path to delete"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Delete directory recursively"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation"),
):
    """Delete a file or directory on PythonAnywhere."""
    try:
        account, client = get_client(FilesClient)

        resolved = _resolve_path(path, account["username"])

        # Check if target is a directory
        parent = resolved.rsplit("/", 2)[0] + "/"
        name = resolved.rstrip("/").rsplit("/", 1)[-1]
        parent_items = client.list(account["username"], parent)

        is_directory = False
        if name in parent_items:
            is_directory = parent_items[name].get("type") == "directory"

        if is_directory and not recursive:
            typer.echo("Error: Use -r/--recursive to delete directories")
            raise typer.Exit(code=1)

        if not force:
            if is_directory:
                confirm = typer.confirm(f"Are you sure you want to delete '{path}' and all its contents?")
            else:
                confirm = typer.confirm(f"Are you sure you want to delete '{path}'?")
            if not confirm:
                typer.echo("Cancelled.")
                raise typer.Exit()

        file_path = resolved.rstrip("/")
        client.delete(account["username"], file_path)

        if is_directory:
            typer.echo(f"Deleted {path} (recursive)")
        else:
            typer.echo(f"Deleted {path}")
    except NotFoundError as e:
        typer.echo(f"File not found: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def share(
    remote_path: str = typer.Argument(..., help="Remote path to share"),
):
    """Share a file and get a share link."""
    try:
        account, client = get_client(FilesClient)
        resolved = _resolve_path(remote_path, account["username"])
        share_url = client.share(account["username"], resolved)
        full_url = f"https://www.pythonanywhere.com{share_url}"
        typer.echo(f"Share link: {full_url}")
    except NotFoundError as e:
        typer.echo(f"File not found: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def unshare(
    remote_path: str = typer.Argument(..., help="Remote path to unshare"),
):
    """Stop sharing a file."""
    try:
        account, client = get_client(FilesClient)
        resolved = _resolve_path(remote_path, account["username"])
        client.unshare(account["username"], resolved)
        typer.echo(f"Stopped sharing: {remote_path}")
    except NotFoundError as e:
        typer.echo(f"File not found或未分享: {e}", err=True)
        raise typer.Exit(code=1)
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("share-status")
def share_status(
    remote_path: str = typer.Argument(..., help="Remote path to check"),
):
    """Check if a file is shared."""
    try:
        account, client = get_client(FilesClient)
        resolved = _resolve_path(remote_path, account["username"])
        share_url = client.get_share_status(account["username"], resolved)
        full_url = f"https://www.pythonanywhere.com{share_url}"
        typer.echo(f"File is shared: {full_url}")
    except NotFoundError:
        typer.echo(f"File is not shared: {remote_path}")
    except NetworkError as e:
        typer.echo(f"Network error: {e}", err=True)
        raise typer.Exit(code=1)
    except APIError as e:
        typer.echo(f"API error: {e}", err=True)
        raise typer.Exit(code=1)
