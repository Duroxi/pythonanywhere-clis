# pythonanywhere-cli 🐍

A command-line interface for [PythonAnywhere](https://www.pythonanywhere.com), designed for developers and AI agents to manage PythonAnywhere resources without a browser.

## Why?

PythonAnywhere's free tier doesn't support SSH, and the web UI can be cumbersome for repetitive tasks. This CLI tool wraps PythonAnywhere's REST API, making it easy to:

- 📁 Manage files (upload, download, list, delete)
- 💻 Run commands via remote consoles
- 🌐 Manage web apps (create, reload, configure)
- ⏰ Handle scheduled tasks and always-on tasks
- 📊 Monitor resource usage (CPU, disk)

## Installation

```bash
pip install pythonanywhere-cli
```

## Quick Start

```bash
# Configure your account
pa init

# List files
pa files ls /home/yourusername/

# Upload a file
pa files upload ./index.html /home/yourusername/mysite/index.html

# Create and use a console
pa console create
pa console send <console-id> "print('hello')"

# Reload your web app
pa webapp reload yourusername.pythonanywhere.com
```

## Commands

| Command | Description |
|---------|-------------|
| `pa init` | Configure API token and username |
| `pa files ls <path>` | List files |
| `pa files upload <local> <remote>` | Upload file |
| `pa files download <remote> <local>` | Download file |
| `pa files rm <path>` | Delete file |
| `pa console ls` | List consoles |
| `pa console create` | Create a new console |
| `pa console send <id> <input>` | Send input to console |
| `pa console output <id>` | Get console output |
| `pa console kill <id>` | Kill a console |
| `pa webapp ls` | List web apps |
| `pa webapp reload <domain>` | Reload web app |
| `pa webapp log <domain>` | View web app log |
| `pa tasks ls` | List scheduled tasks |
| `pa always-on ls` | List always-on tasks |
| `pa status` | Show CPU/disk usage |

## Configuration

Configuration is stored in `~/.pa-cli/config.json`:

```json
{
  "username": "yourusername",
  "token": "your-api-token",
  "host": "www.pythonanywhere.com"
}
```

## API Rate Limits

- Standard endpoints: 40 requests/minute
- Console `send_input`: 120 requests/minute

## Requirements

- Python 3.8+
- A PythonAnywhere account (free tier works!)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or submit a PR.

---

Built with ❤️ for the PythonAnywhere community.
