# pythonanywhere-cli

[![PyPI version](https://img.shields.io/pypi/v/pythonanywhere-clis)](https://pypi.org/project/pythonanywhere-clis/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pythonanywhere-clis)](https://pypi.org/project/pythonanywhere-clis/)
[![Tests](https://img.shields.io/badge/tests-454%20passed-brightgreen)](https://github.com/Duroxi/pythonanywhere-clis/actions)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/Duroxi/pythonanywhere-clis)
[![Documentation](https://readthedocs.org/projects/pythonanywhere-clis/badge/?version=latest)](https://pythonanywhere-clis.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Duroxi/pythonanywhere-clis)](https://github.com/Duroxi/pythonanywhere-clis/stargazers)

CLI tool for automating PythonAnywhere deployments. **Local project → Live website, one step.**

## Documentation

Full documentation is available at **[pythonanywhere-clis.readthedocs.io](https://pythonanywhere-clis.readthedocs.io/en/latest/)**

## Installation

```bash
pip install pythonanywhere-clis
```

## Quick Start

```bash
# 1. Register a new account (if needed)
pa register

# 2. Configure your account (auto-fetches API token)
pa init

# 3. Deploy a project
pa deploy ./my-site
```

## Commands

### Account Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa init` | Configure account (auto-fetches token) | - |
| `pa register` | Register a new PythonAnywhere account | - |
| `pa account list` | List all configured accounts | - |
| `pa account switch <username>` | Switch default account | - |
| `pa account remove <username>` | Remove an account | - |
| `pa account login` | Store password for crawler operations | - |
| `pa account token` | Fetch API token (use `--revoke` to refresh) | Password |
| `pa account extend` | Extend free tier account expiry | Password |

### File Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa files ls [path]` | List remote directory contents | Token |
| `pa files upload <local> <remote> [-r]` | Upload file or directory | Token |
| `pa files download <remote> [local] [-r]` | Download file or directory | Token |
| `pa files rm <path> [-r] [-f]` | Delete remote file or directory | Token |
| `pa files share <path>` | Share a file and get link | Token |
| `pa files unshare <path>` | Stop sharing a file | Token |
| `pa files share-status <path>` | Check if a file is shared | Token |

### Console Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa console list` | List all consoles | Token |
| `pa console create [--executable]` | Create a new console | Token |
| `pa console send <id> <cmd> [--timeout]` | Send command and get output | Token |
| `pa console kill <id>` | Kill a console | Token |
| `pa console activate <id>` | Activate console via WebSocket | Password |
| `pa console get-or-create [-e]` | Get existing or create new console | Password |

### Web App Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa webapp create <domain> [-p]` | Create a web app | Token |
| `pa webapp config <domain> [-s] [-v] [-p] [-w]` | Configure web app | Token |
| `pa webapp static <domain> --url --path` | Add static file mapping | Token |
| `pa webapp reload <domain>` | Reload web app (API) | Token |
| `pa webapp reload-crawler <domain>` | Reload web app (crawler) | Password |
| `pa webapp hits <domain>` | Get hit statistics | Password |
| `pa webapp delete <domain> [-f]` | Delete a web app | Token |
| `pa webapp enable <domain>` | Enable a web app | Password |
| `pa webapp disable <domain>` | Disable a web app | Password |
| `pa webapp logs <domain> [-t] [-n]` | Show web app logs | Token |
| `pa webapp ssl <domain>` | Show SSL certificate info | Token |
| `pa webapp default-python [version]` | Get/set default Python version | Token |

### Deployment

| Command | Description | Auth |
|---------|-------------|------|
| `pa deploy <dir> [--domain] [--python] [--dry-run]` | One-click deploy | Token |

### System Status

| Command | Description | Auth |
|---------|-------------|------|
| `pa status cpu` | Show CPU usage | Token |
| `pa status disk` | Show disk usage | Password |
| `pa status system-image [image]` | Get/set system image | Token |

### Scheduled Tasks

| Command | Description | Auth |
|---------|-------------|------|
| `pa tasks list` | List all scheduled tasks | Token |
| `pa tasks create <command> [--interval] [--hour] [--minute]` | Create a new scheduled task | Token |
| `pa tasks delete <id> [-f]` | Delete a scheduled task | Token |
| `pa tasks enable <id>` | Enable a scheduled task | Token |
| `pa tasks disable <id>` | Disable a scheduled task | Token |

### Always-on Tasks

| Command | Description | Auth |
|---------|-------------|------|
| `pa always-on list` | List all always-on tasks | Token |
| `pa always-on create <command>` | Create a new always-on task | Token |
| `pa always-on delete <id> [-f]` | Delete an always-on task | Token |
| `pa always-on update <id> [-c] [-d] [-e/-E]` | Update an always-on task | Token |
| `pa always-on restart <id>` | Restart an always-on task | Token |

### Databases

| Command | Description | Auth |
|---------|-------------|------|
| `pa databases mysql` | Show MySQL database info | Token |

## Typical Workflows

### Deploy a new project

```bash
pa init                          # Configure account
pa deploy ./my-site              # One-click deploy
```

### Manage existing web app

```bash
pa webapp reload mysite.pythonanywhere.com           # Reload
pa webapp hits mysite.pythonanywhere.com             # Check traffic
pa account extend                                    # Extend expiry
```

### Work with consoles

```bash
pa console list                  # See available consoles
pa console get-or-create        # Get or create a console
pa console activate 12345       # Activate it
pa console send 12345 "ls -la"  # Run a command
pa console kill 12345           # Clean up
```

### Manage multiple accounts

```bash
pa init                          # Add first account
pa init                          # Add second account (becomes default)
pa account list                  # See all accounts
pa account switch user1          # Switch back to first
pa deploy ./site                 # Deploys under user1
pa account remove user2          # Remove an account
```

## Configuration

Configuration is stored at `~/.pa-cli/config.json`:

```json
{
  "accounts": [
    {
      "username": "yourusername",
      "token": "your-api-token",
      "host": "www.pythonanywhere.com",
      "password": "your-password"
    }
  ],
  "default_account": "yourusername"
}
```

## Architecture

```
pa_cli/
├── api/           # REST API clients (Token auth)
│   ├── client.py  # BaseClient with Token auth
│   ├── consoles.py
│   ├── files.py
│   ├── webapps.py
│   ├── system.py
│   ├── tasks.py
│   ├── always_on.py
│   └── databases.py
├── cli/           # CLI commands (Typer)
│   ├── main.py
│   ├── utils.py
│   ├── init_cmd.py
│   ├── register_cmd.py
│   ├── account_cmd.py
│   ├── files_cmd.py
│   ├── consoles_cmd.py
│   ├── webapps_cmd.py
│   ├── deploy_cmd.py
│   ├── status_cmd.py
│   ├── tasks_cmd.py
│   ├── always_on_cmd.py
│   └── databases_cmd.py
├── crawler/       # Browser simulation (Session auth)
│   ├── account_crawler.py
│   └── console_crawler.py
├── workflows/     # Deployment orchestration
│   └── deploy.py
├── config.py      # Configuration management
└── exceptions.py  # Exception hierarchy
```

## Dependencies

- `typer` - CLI framework
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `websocket-client` - WebSocket connections

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=pa_cli --cov-report=html

# Run specific test file
pytest tests/cli/test_webapps_cmd.py
```

**Test coverage:** 454 tests passing, 91% coverage

## License

MIT
