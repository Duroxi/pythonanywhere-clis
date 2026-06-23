# Getting Started Guide

Welcome to pythonanywhere-clis (`pa`)! This guide will help you deploy your local Python project to PythonAnywhere from scratch.

## Table of Contents

- [What is pythonanywhere-clis](#what-is-pythonanywhere-clis)
- [Requirements](#requirements)
- [Installation](#installation)
- [Account Setup](#account-setup)
- [First Project Deployment](#first-project-deployment)
- [Common Commands](#common-commands)
- [Command Dependencies](#command-dependencies)
- [FAQ](#faq)

---

## What is pythonanywhere-clis

pythonanywhere-clis is a command-line tool for automating PythonAnywhere resource management. Its core value:

- **One-command deployment** - `pa deploy ./my-site` handles upload, environment setup, webapp creation, and reload
- **No browser needed** - All operations via command line, suitable for scripts and AI Agents
- **Free tier friendly** - Designed specifically for PythonAnywhere free users

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| OS | Windows / macOS / Linux |
| Network | Access to pythonanywhere.com |

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install pythonanywhere-clis
```

### Option 2: Install from source

```bash
# Clone repository
git clone https://github.com/Duroxi/pythonanywhere-cli.git
cd pythonanywhere-cli

# Install in development mode
pip install -e .
```

### Verify installation

```bash
$ pa --help

 Usage: pa [OPTIONS] COMMAND [ARGS]...

 CLI tool for automating PythonAnywhere deployments.

┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --install-completion          Install completion for the current shell.     │
│ --show-completion             Show completion for the current shell, to     │
│                               copy it or customize the installation.        │
│ --help                        Show this message and exit.                   │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Commands ──────────────────────────────────────────────────────────────────┐
│ init       Configure PythonAnywhere account                                 │
│ files      Manage files on PythonAnywhere                                   │
│ console    Manage consoles on PythonAnywhere                                │
│ webapp     Manage web apps on PythonAnywhere                                │
│ deploy     Deploy a local project to PythonAnywhere                         │
│ account    Account management                                               │
│ register   Register a new PythonAnywhere account                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Account Setup

### Step 1: Register a PythonAnywhere account (if needed)

If you don't have a PythonAnywhere account yet, register via command line:

```bash
$ pa register
Username (letters and numbers only): myusername
Email: myemail@example.com
Password: ********
Confirm password: ********
Account 'myusername' registered successfully!
Please check your email to verify your account.
Then run: pa init
```

> **Tip**: Skip this step if you already have an account.

### Step 2: Initialize configuration

```bash
$ pa init
PythonAnywhere username: myusername
Password: ********
Host [www.pythonanywhere.com]:
Account 'myusername' configured successfully.
API token fetched and saved.
```

`pa init` automatically:
1. Saves your username and password
2. Logs into PythonAnywhere
3. Fetches API token from account page
4. Saves everything to `~/.pa-cli/config.json`

---

## First Project Deployment

### Prepare project files

Create a simple Flask project:

```
my-site/
├── app.py
└── requirements.txt
```

**app.py:**

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from PythonAnywhere!'

if __name__ == '__main__':
    app.run()
```

**requirements.txt:**

```
flask
```

### One-click deploy

```bash
$ pa deploy ./my-site
Uploading ./my-site to /home/myusername/my-site...
Uploaded 2 files.
Setting up environment...
Creating webapp myusername.pythonanywhere.com...
Reloading webapp...

Deployed! Visit: https://myusername.pythonanywhere.com
```

After deployment, visit `https://myusername.pythonanywhere.com` to see your website.

---

## Common Commands

### Account Management

```bash
pa init                    # Initialize configuration (auto-fetch token)
pa register                # Register new account
pa account login           # Store password
pa account token           # Fetch API token
pa account extend          # Extend free tier expiry
```

### Deployment

```bash
pa deploy ./my-site                    # Deploy to default domain
pa deploy ./my-site --domain custom    # Deploy to custom domain
```

### File Management

```bash
pa files upload ./index.html /home/user/site/index.html      # Upload single file
pa files upload ./static /home/user/site/static -r            # Upload directory
```

### Console Management

```bash
pa console list                      # List all consoles
pa console create                    # Create new console
pa console send 12345 "ls -la"       # Send command and get output
pa console activate 12345            # Activate console
pa console get-or-create             # Smart get or create
pa console kill 12345                # Kill console
```

### Webapp Management

```bash
pa webapp create mysite.pythonanywhere.com                    # Create webapp
pa webapp config mysite --source-dir /home/user/mysite        # Configure source dir
pa webapp static mysite --url /static/ --path static          # Add static mapping
pa webapp reload mysite.pythonanywhere.com                    # Reload webapp
pa webapp hits mysite.pythonanywhere.com                      # View hit statistics
```

---

## Command Dependencies

Some commands require prerequisites:

| Command | Prerequisite | Notes |
|---------|--------------|-------|
| `pa deploy` | `pa init` | Requires API token |
| `pa files upload` | `pa init` | Requires API token |
| `pa console create/list/send/kill` | `pa init` | Requires API token |
| `pa webapp create/config/static/reload` | `pa init` | Requires API token |
| `pa account token/extend` | `pa init` | Requires password (auto-read from config) |
| `pa console activate/get-or-create` | `pa init` | Requires password (auto-read from config) |
| `pa webapp hits/reload-crawler` | `pa init` | Requires password (auto-read from config) |

**Simply put**: After running `pa init`, all commands are available.

---

## FAQ

### 1. API Token Error

**Error message**:
```
Exception: API error 401: Invalid token.
```

**Solution**:
```bash
pa account token    # Re-fetch token
```

### 2. Password Not Configured

**Error message**:
```
Password not found in config. Run 'pa account login' to store it.
```

**Solution**:
```bash
pa account login    # Store password
```

### 3. Console Not Started

**Error message**:
```
Exception: API error 412: Console not yet started.
```

**Solution**:
```bash
pa console list         # Get console ID
pa console activate 12345   # Activate console
```

### 4. Free Tier Limits

Free tier limits:
- Max 1 web app
- Max 2 consoles
- 100 seconds CPU time per month

### 5. Network Connection Issues

**Error message**:
```
ConnectionError: ('Connection aborted.', RemoteDisconnected(...))
```

**Solution**:
- Check network connection
- Verify access to pythonanywhere.com
- Retry later

---

## Next Steps

- [Command Reference](commands/) - Detailed documentation for all commands
- [Architecture](architecture.md) - Understand project internals
- [GitHub Repository](https://github.com/Duroxi/pythonanywhere-cli) - View source code

---

*Last updated: 2026-06-24*
