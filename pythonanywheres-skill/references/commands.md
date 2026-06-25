# Command Reference

Complete reference for all `pa` commands.

## Table of Contents

- [Account Commands](#account-commands)
- [Console Commands](#console-commands)
- [Deploy Commands](#deploy-commands)
- [Files Commands](#files-commands)
- [Status Commands](#status-commands)
- [Tasks Commands](#tasks-commands)
- [Always-on Commands](#always-on-commands)
- [Webapp Commands](#webapp-commands)

---

## Account Commands

### pa init

Configure a PythonAnywhere account.

**Syntax:**
```bash
pa init [-u <username>] [-p <password>] [-h <host>]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-u`, `--username` | Interactive prompt | PythonAnywhere username |
| `-p`, `--password` | Interactive prompt | Account password |
| `-h`, `--host` | `www.pythonanywhere.com` | PythonAnywhere host address |

**Examples:**
```bash
# Interactive mode
pa init

# Command-line mode
pa init -u myuser -p mypassword

# Custom host
pa init -u myuser -p mypassword -h eu.pythonanywhere.com
```

---

### pa register

Register a new PythonAnywhere account.

**Syntax:**
```bash
pa register
```

**Description:**
Prompts for username, email, password interactively.

---

### pa account list

List all configured accounts.

**Syntax:**
```bash
pa account list
```

**Example output:**
```
* myuser    www.pythonanywhere.com    token: abc12345...
  workuser  www.pythonanywhere.com    token: def67890...
```

---

### pa account switch

Switch the default account.

**Syntax:**
```bash
pa account switch <username>
```

**Parameters:**
- `username` (required): Username to switch to

---

### pa account remove

Remove a configured account.

**Syntax:**
```bash
pa account remove <username>
```

**Parameters:**
- `username` (required): Username to remove

---

### pa account login

Store password for Session authentication.

**Syntax:**
```bash
pa account login
```

**Description:**
Saves password to `~/.pa-cli/config.json` for commands requiring Session auth.

---

### pa account token

Fetch API token via crawler.

**Syntax:**
```bash
pa account token [-r | --revoke]
```

**Options:**
- `-r`, `--revoke`: Revoke current token and create new one

**Examples:**
```bash
# Get existing token
pa account token

# Revoke and create new token
pa account token --revoke
```

---

### pa account extend

Extend free tier account expiry.

**Syntax:**
```bash
pa account extend
```

**Prerequisites:**
- Must run `pa init` first
- Must run `pa account login` first

---

## Console Commands

### pa console list

List all consoles.

**Syntax:**
```bash
pa console list
```

**Example output:**
```
ID: 46955916, Name: Bash console 46955916
```

---

### pa console create

Create a new console.

**Syntax:**
```bash
pa console create [--executable <executable>]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--executable` | `bash` | Console executable (`bash`, `python3.10`, etc.) |

**Examples:**
```bash
pa console create
pa console create --executable python3.10
```

---

### pa console send

Send command to console and get output.

**Syntax:**
```bash
pa console send <console_id> <command> [--wait/--no-wait] [--timeout <seconds>]
```

**Parameters:**
- `console_id` (required): Console ID
- `command` (required): Command to execute

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--wait` / `-w` | True | Wait for output |
| `--no-wait` / `-W` | - | Send without waiting |
| `-t`, `--timeout` | `30` | Max seconds to wait |

**Examples:**
```bash
pa console send 46955916 "echo hello"
pa console send 46955916 "pip install flask" --timeout 120
pa console send 46955916 "long-command" --no-wait
```

---

### pa console kill

Kill a console.

**Syntax:**
```bash
pa console kill <console_id>
```

---

### pa console activate

Activate console via WebSocket (requires Session auth).

**Syntax:**
```bash
pa console activate <console_id>
```

**Prerequisites:**
- Must run `pa account login` first

---

### pa console get-or-create

Smart get or create console (requires Session auth).

**Syntax:**
```bash
pa console get-or-create [--executable <executable>]
```

**Options:**
- `--executable` / `-e` (default: `bash`): Console executable

**Logic:**
1. List existing consoles
2. If available, return its ID
3. If at limit (2), delete oldest and create new
4. If none, create new

---

## Deploy Commands

### pa deploy

One-click deployment to PythonAnywhere.

**Syntax:**
```bash
pa deploy <local_dir> [--domain <domain>] [--python <python_version>] [--dry-run]
```

**Parameters:**
- `local_dir` (required): Local project directory

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-d`, `--domain` | `{username}.pythonanywhere.com` | Target domain |
| `-p`, `--python` | `python310` | Python version |
| `-n`, `--dry-run` | False | Preview without executing |

**Examples:**
```bash
pa deploy ./my-site
pa deploy ./my-site --domain mysite.pythonanywhere.com
pa deploy ./my-site --python python311
pa deploy ./my-site --dry-run
```

**What it does:**
1. Upload files recursively
2. Create console and setup environment
3. Install dependencies if requirements.txt exists
4. Create/configure web app
5. Reload web app

---

## Files Commands

### pa files ls

List remote directory contents.

**Syntax:**
```bash
pa files ls [<remote_path>]
```

**Parameters:**
- `remote_path` (optional): Remote path (default: home directory)

---

### pa files upload

Upload file or directory to PythonAnywhere.

**Syntax:**
```bash
pa files upload <local_path> <remote_path> [-r | --recursive]
```

**Parameters:**
- `local_path` (required): Local file or directory
- `remote_path` (required): Remote path

**Options:**
- `-r`, `--recursive`: Upload directory recursively

**Examples:**
```bash
pa files upload ./app.py /home/myuser/app.py
pa files upload ./myproject /home/myuser/myproject -r
```

---

### pa files download

Download file or directory from PythonAnywhere.

**Syntax:**
```bash
pa files download <remote_path> [<local_path>] [-r | --recursive]
```

**Parameters:**
- `remote_path` (required): Remote file or directory
- `local_path` (optional): Local destination (default: current directory)

**Options:**
- `-r`, `--recursive`: Download directory recursively

---

### pa files rm

Delete remote file or directory.

**Syntax:**
```bash
pa files rm <remote_path> [-r | --recursive] [-f | --force]
```

**Options:**
- `-r`, `--recursive`: Delete directory recursively
- `-f`, `--force`: Skip confirmation

---

### pa files share

Share a file and get share link.

**Syntax:**
```bash
pa files share <remote_path>
```

---

### pa files unshare

Stop sharing a file.

**Syntax:**
```bash
pa files unshare <remote_path>
```

---

### pa files share-status

Check if a file is shared.

**Syntax:**
```bash
pa files share-status <remote_path>
```

---

## Status Commands

### pa status cpu

Show CPU usage (Token auth).

**Syntax:**
```bash
pa status cpu
```

**Output fields:**
- Used: CPU time used today (seconds)
- Limit: Daily CPU time quota (seconds)
- Reset: Quota reset time

---

### pa status disk

Show disk usage (Session auth).

**Syntax:**
```bash
pa status disk
```

**Output fields:**
- Used: Disk space used
- Total: Total disk space
- Usage: Usage percentage

**Prerequisites:**
- Must run `pa account login` first

---

### pa status system-image

Get or set the system image.

**Syntax:**
```bash
pa status system-image [<image>]
```

**Parameters:**
- `image` (optional): System image to set

**Examples:**
```bash
# Get current system image
pa status system-image

# Set system image
pa status system-image ubuntu-22.04
```

---

## Tasks Commands

### pa tasks list

List all scheduled tasks.

**Syntax:**
```bash
pa tasks list
```

**Output fields:**
- ID, Command, Interval (hourly/daily/weekly/monthly), Status (enabled/disabled)

---

### pa tasks create

Create a new scheduled task.

**Syntax:**
```bash
pa tasks create <command> [--interval <interval>] [--hour <hour>] [--minute <minute>] [--description <description>]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-i`, `--interval` | `daily` | Interval: hourly, daily, weekly, monthly |
| `-H`, `--hour` | `0` | Hour to run (0-23) |
| `-M`, `--minute` | `0` | Minute to run (0-59) |
| `-d`, `--description` | `""` | Task description |

**Examples:**
```bash
pa tasks create "python /home/user/backup.py" --interval daily --hour 2
pa tasks create "curl https://api.example.com" --interval hourly
```

---

### pa tasks delete

Delete a scheduled task.

**Syntax:**
```bash
pa tasks delete <task_id> [-f | --force]
```

---

### pa tasks enable

Enable a scheduled task.

**Syntax:**
```bash
pa tasks enable <task_id>
```

---

### pa tasks disable

Disable a scheduled task.

**Syntax:**
```bash
pa tasks disable <task_id>
```

---

## Always-on Commands

> **Note:** Always-on tasks are only available for paid accounts.

### pa always-on list

List all always-on tasks.

**Syntax:**
```bash
pa always-on list
```

---

### pa always-on create

Create a new always-on task.

**Syntax:**
```bash
pa always-on create <command>
```

**Example:**
```bash
pa always-on create "python /home/user/webhook_server.py"
```

---

### pa always-on delete

Delete an always-on task.

**Syntax:**
```bash
pa always-on delete <task_id> [-f | --force]
```

---

### pa always-on update

Update an always-on task.

**Syntax:**
```bash
pa always-on update <task_id> [--command <command>] [--description <description>] [--enabled/--disabled]
```

**Options:**
- `-c`, `--command`: New command
- `-d`, `--description`: New description
- `-e`, `--enabled`: Enable task
- `-E`, `--disabled`: Disable task

**Examples:**
```bash
# Update command
pa always-on update 789 --command "python /home/user/new_server.py"

# Disable task
pa always-on update 789 --disabled
```

---

### pa always-on restart

Restart an always-on task.

**Syntax:**
```bash
pa always-on restart <task_id>
```

**Example:**
```bash
pa always-on restart 789
```

---

## Webapp Commands

### pa webapp create

Create a new web app.

**Syntax:**
```bash
pa webapp create <domain_name> [-p <python_version>]
```

**Options:**
- `-p`, `--python` (default: `python310`): Python version

**Example:**
```bash
pa webapp create myuser.pythonanywhere.com --python python311
```

---

### pa webapp config

Configure web app.

**Syntax:**
```bash
pa webapp config [<domain_name>] [-s <source_dir>] [-v <virtualenv>] [-p <python_version>] [-w <working_dir>]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-s`, `--source-dir` | Source directory path |
| `-v`, `--virtualenv` | Virtualenv path |
| `-p`, `--python-version` | Python version (e.g., 3.10, 3.11) |
| `-w`, `--working-dir` | Working directory path |

**Example:**
```bash
pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject -v /home/myuser/.virtualenvs/myproject
```

---

### pa webapp static

Add static file mapping.

**Syntax:**
```bash
pa webapp static <domain_name> --url <url_prefix> --path <directory_path>
```

**Example:**
```bash
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static
```

---

### pa webapp reload

Reload web app via API.

**Syntax:**
```bash
pa webapp reload <domain_name>
```

---

### pa webapp reload-crawler

Reload web app via crawler (Session auth).

**Syntax:**
```bash
pa webapp reload-crawler <domain_name>
```

---

### pa webapp hits

Get web app hit statistics (Session auth).

**Syntax:**
```bash
pa webapp hits <domain_name>
```

---

### pa webapp delete

Delete a web app.

**Syntax:**
```bash
pa webapp delete <domain_name> [-f | --force]
```

---

### pa webapp enable

Enable a web app (Session auth).

**Syntax:**
```bash
pa webapp enable <domain_name>
```

---

### pa webapp disable

Disable a web app (Session auth).

**Syntax:**
```bash
pa webapp disable <domain_name>
```

---

### pa webapp logs

View web app logs.

**Syntax:**
```bash
pa webapp logs [<domain_name>] [-t <log_type>] [-n <lines>]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-t`, `--type` | `error` | Log type: access, error, server |
| `-n`, `--lines` | `50` | Number of lines to show |

**Example:**
```bash
pa webapp logs --type error --lines 20
```

---

### pa webapp ssl

View SSL certificate info.

**Syntax:**
```bash
pa webapp ssl [<domain_name>]
```

**Certificate types:**
- `pythonanywhere-subdomain` (free)
- `lets-encrypt` (paid)
- `custom` (paid)

---

### pa webapp default-python

Get or set the default Python 3 version.

**Syntax:**
```bash
pa webapp default-python [<version>]
```

**Parameters:**
- `version` (optional): Python version to set (e.g. python310, python311)

**Examples:**
```bash
# Get current default version
pa webapp default-python

# Set default version
pa webapp default-python python311
```

---

## Databases Commands

### pa databases mysql

Show MySQL database information.

**Syntax:**
```bash
pa databases mysql
```

**Example:**
```bash
pa databases mysql
```

**Output:**
```
MySQL Databases:
  myuser$mydb: 10.5 MB
  myuser$testdb: 2.1 MB
```
