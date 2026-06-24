---
name: pythonanywheres-skill
description: >
  Use this skill whenever the user mentions PythonAnywhere, deploying websites to the cloud,
  managing remote Python projects, or any operation related to the `pa` command-line tool.
  This skill provides comprehensive guidance on using pythonanywhere-clis to automate
  PythonAnywhere resource management including deployment, file management, console operations,
  web app configuration, scheduled tasks, and more. Make sure to use this skill even if the
  user doesn't explicitly ask for 'pa' commands - any mention of PythonAnywhere, cloud deployment,
  or remote Python hosting should trigger this skill.
---

# PythonAnywhere CLI Skill

Complete guide for using `pythonanywhere-clis` (`pa`) to manage PythonAnywhere resources via command line.

## Resources

- **GitHub**: https://github.com/Duroxi/pythonanywhere-clis
- **Documentation**: https://pythonanywhere-clis.readthedocs.io
- **PyPI**: https://pypi.org/project/pythonanywhere-clis/
- **Install**: `pip install pythonanywhere-clis`
- **Version**: 1.0.0
- **License**: MIT
- **Python**: 3.10+

## What is pythonanywhere-clis

pythonanywhere-clis is a CLI tool that wraps PythonAnywhere's REST API, enabling:
- **One-command deployment** - `pa deploy ./my-site` handles upload, environment, webapp creation, reload
- **No browser needed** - All operations via command line, suitable for scripts and AI Agents
- **Free tier friendly** - Designed specifically for PythonAnywhere free users

### Supported Python Versions

- **Local CLI**: Python 3.10+ (required to run `pa` commands)
- **PythonAnywhere**: Python 3.8, 3.9, 3.10, 3.11, 3.12 (for deployed apps)

## Installation

```bash
pip install pythonanywhere-clis
```

## Quick Start

```bash
# 1. Configure account (interactive)
pa init

# 2. Deploy a project
pa deploy ./my-site

# 3. Visit your site
# https://yourusername.pythonanywhere.com
```

## Authentication

The CLI uses two authentication methods:

| Method | Credentials | Use For |
|--------|-------------|---------|
| Token | API Token | Most commands (files, console, webapp, deploy, tasks) |
| Session | Username + Password | Browser operations (activate console, get hits, extend expiry) |

### Configure Authentication

```bash
# Interactive setup (saves username, password, fetches token)
pa init

# Or command-line mode
pa init -u myuser -p mypassword

# Store password for Session auth commands
pa account login
```

## Command Overview

| Group | Purpose | Commands |
|-------|---------|----------|
| `pa init` | Configure account | init, register |
| `pa account` | Account management | list, switch, remove, login, token, extend |
| `pa files` | File operations | ls, upload, download, rm, share, unshare, share-status |
| `pa console` | Console management | list, create, send, kill, activate, get-or-create |
| `pa webapp` | Web app management | create, config, static, reload, hits, delete, enable, disable, logs, ssl |
| `pa deploy` | One-click deployment | deploy (supports --dry-run, --domain, --python) |
| `pa status` | System status | cpu, disk |
| `pa tasks` | Scheduled tasks | list, create, delete, enable, disable |
| `pa always-on` | Always-on tasks | list, create, delete |

## Common Workflows

### Deploy a Website

```bash
# One-click deploy
pa deploy ./my-site

# With custom domain
pa deploy ./my-site --domain mysite.pythonanywhere.com

# With specific Python version
pa deploy ./my-site --python python311

# Preview without executing
pa deploy ./my-site --dry-run
```

### Manage Files

```bash
# List files
pa files ls

# Upload single file
pa files upload ./app.py /home/myuser/app.py

# Upload directory
pa files upload ./myproject /home/myuser/myproject -r

# Download file
pa files download /home/myuser/app.py ./app.py

# Delete file
pa files rm /home/myuser/old.txt
```

### Manage Console

```bash
# List consoles
pa console list

# Create and activate console
pa console create
pa console activate 12345

# Send command
pa console send 12345 "ls -la"

# Smart get or create
pa console get-or-create
```

### Manage Web App

```bash
# Create web app
pa webapp create mysite.pythonanywhere.com

# Configure source directory
pa webapp config mysite -s /home/user/mysite

# Add static files
pa webapp static mysite --url /static/ --path /home/user/mysite/static

# Reload app
pa webapp reload mysite.pythonanywhere.com

# View logs
pa webapp logs --type error --lines 20
```

### Manage Tasks

```bash
# Create daily backup task
pa tasks create "python /home/user/backup.py" --interval daily --hour 2

# List tasks
pa tasks list

# Disable task
pa tasks disable 12345
```

### Multi-Account Management

```bash
# Add account
pa init

# List accounts
pa account list

# Switch account
pa account switch user1

# Remove account
pa account remove user2
```

## Detailed References

For complete command documentation, see:
- [Command Reference](references/commands.md) - All commands with full syntax and options
- [Workflow Examples](references/workflows.md) - Step-by-step task examples

## Free Tier Limits

- Max 1 web app
- Max 2 consoles
- 100 seconds CPU time per month

## Troubleshooting

### Command fails with "Invalid token"
```bash
pa account token    # Re-fetch token
```

### Command fails with "Password not found"
```bash
pa account login    # Store password
```

### Command fails with "Console not yet started"
```bash
pa console activate <id>    # Activate console
```

### Command fails with "Rate limit exceeded"
- Standard API: 40 requests/minute
- Console send_input: 120 requests/minute
- Wait 60 seconds and retry
- Use `--no-wait` for non-blocking commands

### Web app returns 500 error
```bash
pa webapp logs --type error --lines 50    # Check error logs
pa webapp reload                          # Reload app
```

### Free tier account expired
```bash
pa account extend    # Extend expiry
```

## Authentication Quick Reference

| Command | Auth Type | Prerequisite |
|---------|-----------|--------------|
| `pa init` | - | None |
| `pa register` | - | None |
| `pa account list` | - | None |
| `pa account switch` | - | `pa init` |
| `pa account remove` | - | `pa init` |
| `pa account login` | - | `pa init` |
| `pa account token` | Session | `pa account login` |
| `pa account extend` | Session | `pa account login` |
| `pa files *` | Token | `pa init` |
| `pa console list/create/send/kill` | Token | `pa init` |
| `pa console activate/get-or-create` | Session | `pa account login` |
| `pa deploy` | Token | `pa init` |
| `pa webapp create/config/static/reload/delete` | Token | `pa init` |
| `pa webapp reload-crawler/hits/enable/disable` | Session | `pa account login` |
| `pa webapp logs/ssl` | Token | `pa init` |
| `pa status cpu` | Token | `pa init` |
| `pa status disk` | Session | `pa account login` |
| `pa tasks *` | Token | `pa init` |
| `pa always-on *` | Token | `pa init` |

## Tips

1. Use `--dry-run` with `pa deploy` to preview changes before executing
2. Use `pa console get-or-create` for automatic console lifecycle management
3. For long-running commands, use `--timeout` to extend wait time
4. Store password with `pa account login` for commands requiring Session auth
5. Use `pa account extend` regularly to prevent free tier account expiration
6. Check logs first when debugging: `pa webapp logs --type error`
