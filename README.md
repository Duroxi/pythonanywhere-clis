# pythonanywhere-cli

CLI tool for automating PythonAnywhere deployments. **Local project → Live website, one step.**

## Installation

```bash
pip install -e .
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
| `pa account token` | Fetch API token from account page | Password |
| `pa account extend` | Extend free tier account expiry | Password |

### File Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa files ls [path]` | List remote directory contents | Token |
| `pa files download <remote> [local]` | Download a file | Token |
| `pa files download <remote> [local] -r` | Download directory recursively | Token |
| `pa files rm <path>` | Delete a remote file | Token |
| `pa files rm <path> -r` | Delete directory recursively | Token |
| `pa files upload <local> <remote>` | Upload a single file | Token |
| `pa files upload <local> <remote> -r` | Upload directory recursively | Token |

### Console Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa console list` | List all consoles | Token |
| `pa console create` | Create a new console | Token |
| `pa console send <id> <cmd>` | Send command and get output | Token |
| `pa console kill <id>` | Kill a console | Token |
| `pa console activate <id>` | Activate console via WebSocket | Password |
| `pa console get-or-create` | Get existing or create new console | Password |

### Web App Management

| Command | Description | Auth |
|---------|-------------|------|
| `pa webapp create <domain>` | Create a web app | Token |
| `pa webapp config <domain> --source-dir <path>` | Configure source directory | Token |
| `pa webapp config <domain> --virtualenv <path>` | Configure virtualenv path | Token |
| `pa webapp static <domain> --url <url> --path <path>` | Add static file mapping | Token |
| `pa webapp reload <domain>` | Reload web app (API) | Token |
| `pa webapp reload-crawler <domain>` | Reload web app (crawler) | Password |
| `pa webapp hits <domain>` | Get hit statistics | Password |
| `pa webapp delete <domain>` | Delete a web app | Token |
| `pa webapp enable <domain>` | Enable a web app | Token |
| `pa webapp disable <domain>` | Disable a web app | Token |
| `pa webapp logs <domain>` | Show web app logs | Token |

### Deployment

| Command | Description | Auth |
|---------|-------------|------|
| `pa deploy <dir>` | One-click deploy to default domain | Token |
| `pa deploy <dir> --domain <domain>` | One-click deploy to custom domain | Token |

### System Status

| Command | Description | Auth |
|---------|-------------|------|
| `pa status cpu` | Show CPU usage | Token |

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
│   └── webapps.py
├── cli/           # CLI commands (Typer)
│   ├── main.py
│   ├── init_cmd.py
│   ├── register_cmd.py
│   ├── account_cmd.py
│   ├── files_cmd.py
│   ├── consoles_cmd.py
│   ├── webapps_cmd.py
│   └── deploy_cmd.py
├── crawler/       # Browser simulation (Session auth)
│   ├── account_crawler.py
│   └── console_crawler.py
├── workflows/     # Deployment orchestration
│   └── deploy.py
└── config.py      # Configuration management
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

# Run specific test file
pytest tests/test_account_crawler.py
```

**Test coverage:** 206 tests passing

## Roadmap

### ✅ Completed (P0/P1)

- [x] Account configuration (`pa init`)
- [x] Account registration (`pa register`)
- [x] Auto-fetch API token (`pa account token`)
- [x] Auto-extend expiry (`pa account extend`)
- [x] File upload (`pa files upload`)
- [x] File browsing (`pa files ls`)
- [x] File download (`pa files download`)
- [x] File deletion (`pa files rm`)
- [x] Console management (`pa console *`)
- [x] Web app management (`pa webapp *`)
- [x] One-click deployment (`pa deploy`)
- [x] Hit statistics (`pa webapp hits`)
- [x] Multi-account management (`pa account switch`)
- [x] CPU usage query (`pa status`)

### 🔲 Planned (P2)

- [ ] Log management (`pa webapp logs`)
- [ ] Webapp enable/disable (`pa webapp enable/disable`)
- [ ] Batch operations (`pa batch`)
- [ ] SSL management (`pa webapp ssl`)
- [ ] Delete webapp (`pa webapp delete`)

### 🔲 Planned (P3)

- [ ] Scheduled tasks (`pa tasks`)
- [ ] Always-on tasks (`pa always-on`)
- [ ] Disk usage query (`pa status disk`)
- [ ] System configuration (`pa config`)
- [ ] Database info (`pa databases`)
- [ ] File sharing (`pa files share`)

## License

MIT