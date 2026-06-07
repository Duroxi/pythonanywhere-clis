import time
from pathlib import Path

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


def deploy(
    local_dir: str,
    username: str,
    token: str,
    host: str,
    domain: str,
    python_version: str = "python310",
) -> str:
    local_path = Path(local_dir)
    if not local_path.is_dir():
        raise PACliError(f"{local_dir} is not a directory")

    remote_base = f"/home/{username}/{local_path.name}"
    files_client = FilesClient(token=token, host=host)
    consoles_client = ConsolesClient(token=token, host=host)
    webapps_client = WebappsClient(token=token, host=host)

    # Step 1: Upload files
    print(f"Uploading {local_dir} to {remote_base}...")
    file_count = 0
    for file in local_path.rglob("*"):
        if file.is_file():
            relative = file.relative_to(local_path)
            remote = f"{remote_base}/{relative}".replace("\\", "/")
            content = file.read_bytes()
            files_client.upload(username, remote, content)
            file_count += 1
    print(f"Uploaded {file_count} files.")

    # Step 2: Setup environment via console
    print("Setting up environment...")
    console = consoles_client.create(username)
    console_id = console["id"]

    # Send setup commands
    commands = [f"cd {remote_base}"]

    if (local_path / "requirements.txt").exists():
        commands.extend([
            f"mkvirtualenv {local_path.name} --python=/usr/bin/{python_version}",
            f"workon {local_path.name} && pip install -r requirements.txt",
        ])

    for cmd in commands:
        consoles_client.send_input(username, console_id, cmd + "\n")
        _wait_for_console(consoles_client, username, console_id)

    # Step 3: Create and configure webapp
    print(f"Creating webapp {domain}...")
    try:
        webapps_client.create(username, domain, python_version)
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise

    webapps_client.update(
        username,
        domain,
        source_directory=remote_base,
    )

    # Step 4: Add static file mapping if static dir exists
    static_local = local_path / "static"
    if static_local.exists():
        webapps_client.add_static_file(
            username,
            domain,
            url="/static/",
            path=f"{remote_base}/static",
        )

    # Step 5: Reload
    print("Reloading webapp...")
    webapps_client.reload(username, domain)

    url = f"https://{domain}"
    return url
