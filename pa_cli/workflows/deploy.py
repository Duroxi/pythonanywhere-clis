import time
from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

from pa_cli.api.files import FilesClient
from pa_cli.api.consoles import ConsolesClient
from pa_cli.api.webapps import WebappsClient
from pa_cli.exceptions import PACliError

POLL_INTERVAL = 2  # seconds between output checks
MAX_WAIT = 300  # max seconds to wait for a command


def _wait_for_console(client: ConsolesClient, username: str, console_id: int) -> str:
    """Poll console output until the prompt returns or timeout."""
    elapsed = 0
    last_output = ""
    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        result = client.get_output(username, console_id)
        output = result.get("output", "")
        if output != last_output:
            last_output = output
            # PA console shows $ or >>> when idle
            if output.rstrip().endswith("$") or output.rstrip().endswith(">>>"):
                break
    return last_output


def collect_files(local_dir: str) -> list:
    """Collect all files in directory recursively."""
    local_path = Path(local_dir)
    return [f for f in local_path.rglob("*") if f.is_file()]


def deploy_preview(account: dict, local_dir: str, domain: str, python_version: str) -> None:
    """Print deploy preview without executing any operations."""
    local_path = Path(local_dir)
    username = account["username"]
    remote_base = f"/home/{username}/{local_path.name}"

    typer.echo("=== 部署预览 (dry-run) ===\n")

    # Step 1: File list
    typer.echo("📁 Step 1: 将要上传的文件")
    files = collect_files(local_dir)
    max_display = 20
    for f in files[:max_display]:
        size = f.stat().st_size
        typer.echo(f"  - {f.relative_to(local_path)} ({size} bytes)")
    if len(files) > max_display:
        typer.echo(f"  ... 还有 {len(files) - max_display} 个文件")
    typer.echo(f"  共 {len(files)} 个文件\n")

    # Step 2: Environment setup
    typer.echo("📦 Step 2: 环境配置")
    typer.echo("  - 创建 bash console")
    typer.echo(f"  - cd {remote_base}")
    if (local_path / "requirements.txt").exists():
        typer.echo(f"  - mkvirtualenv {local_path.name} --python=/usr/bin/{python_version}")
        typer.echo(f"  - workon {local_path.name} && pip install -r requirements.txt")
    typer.echo()

    # Step 3: Webapp configuration
    typer.echo("⚙️ Step 3: Webapp 配置")
    typer.echo(f"  - 创建/更新 webapp: {domain}")
    typer.echo(f"  - 源码目录: {remote_base}")
    typer.echo()

    # Step 4: Static file mapping
    if (local_path / "static").exists():
        typer.echo("📂 Step 4: 静态文件映射")
        typer.echo(f"  - /static/ -> {remote_base}/static")
        typer.echo()
    else:
        typer.echo("📂 Step 4: 无 static 目录，跳过\n")

    # Step 5: Reload
    typer.echo("🔄 Step 5: Reload webapp\n")

    typer.echo("以上为预览，使用不带 --dry-run 的命令执行：")
    typer.echo(f"  pa deploy {local_dir}")


def deploy(
    local_dir: str,
    username: str,
    token: str,
    host: str,
    domain: str,
    python_version: str = "python310",
    dry_run: bool = False,
) -> str:
    local_path = Path(local_dir)
    if not local_path.is_dir():
        raise PACliError(f"{local_dir} is not a directory")

    if dry_run:
        account = {"username": username}
        deploy_preview(account, local_dir, domain, python_version)
        return ""

    remote_base = f"/home/{username}/{local_path.name}"
    files_client = FilesClient(token=token, host=host)
    consoles_client = ConsolesClient(token=token, host=host)
    webapps_client = WebappsClient(token=token, host=host)

    # Step 1: Upload files with progress bar
    print(f"[1/5] Uploading {local_dir} to {remote_base}...")
    try:
        files = collect_files(local_dir)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("Uploading files...", total=len(files))
            for file in files:
                relative = file.relative_to(local_path)
                remote = f"{remote_base}/{relative}".replace("\\", "/")
                content = file.read_bytes()
                files_client.upload(username, remote, content)
                progress.advance(task)
        print(f"  ✓ Uploaded {len(files)} files.")
    except Exception as e:
        print(f"  ✗ Upload failed: {e}")
        print(f"  Hint: Retry with `pa deploy {local_dir} {domain}`")
        raise

    # Step 2: Setup environment via console
    print(f"[2/5] Setting up environment...")
    try:
        console = consoles_client.create(username)
        console_id = console["id"]

        commands = [f"cd {remote_base}"]
        if (local_path / "requirements.txt").exists():
            commands.extend([
                f"mkvirtualenv {local_path.name} --python=/usr/bin/{python_version}",
                f"workon {local_path.name} && pip install -r requirements.txt",
            ])

        for cmd in commands:
            consoles_client.send_input(username, console_id, cmd + "\n")
            _wait_for_console(consoles_client, username, console_id)
        print(f"  ✓ Environment configured.")
    except Exception as e:
        print(f"  ✗ Environment setup failed: {e}")
        print(f"  Hint: Check requirements.txt and retry.")
        raise

    # Step 3: Create and configure webapp
    print(f"[3/5] Configuring webapp {domain}...")
    try:
        webapps_client.create(username, domain, python_version)
    except Exception as e:
        if "already exists" not in str(e).lower():
            print(f"  ✗ Webapp creation failed: {e}")
            raise

    try:
        webapps_client.update(
            username,
            domain,
            source_directory=remote_base,
        )
        print(f"  ✓ Webapp configured.")
    except Exception as e:
        print(f"  ✗ Webapp configuration failed: {e}")
        raise

    # Step 4: Add static file mapping if static dir exists
    static_local = local_path / "static"
    if static_local.exists():
        print(f"[4/5] Adding static file mapping...")
        try:
            webapps_client.add_static_file(
                username,
                domain,
                url="/static/",
                path=f"{remote_base}/static",
            )
            print(f"  ✓ Static files mapped.")
        except Exception as e:
            print(f"  ✗ Static file mapping failed: {e}")
            raise
    else:
        print(f"[4/5] No static directory, skipping.")

    # Step 5: Reload
    print(f"[5/5] Reloading webapp...")
    try:
        webapps_client.reload(username, domain)
        print(f"  ✓ Webapp reloaded.")
    except Exception as e:
        print(f"  ✗ Reload failed: {e}")
        print(f"  Hint: Run `pa webapp reload {domain}` manually.")
        raise

    url = f"https://{domain}"
    print(f"\nDeploy complete: {url}")
    return url
