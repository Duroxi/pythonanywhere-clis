# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pythonanywhere-clis (`pa`) is a command-line interface for [PythonAnywhere](https://www.pythonanywhere.com), wrapping their REST API for browser-free resource management. Targets developers and AI agents on the free tier (no SSH).

## Architecture

- **CLI entry point**: `pa` command with subcommands (Typer framework)
- **Config**: stored at `~/.pa-cli/config.json` (username, API token, host)
- **API client**: wraps PythonAnywhere REST API; standard endpoints rate-limited to 40 req/min, console `send_input` at 120 req/min
- **Crawler**: browser simulation for operations not supported by API (enable/disable webapp, get hits, etc.)
- **Python 3.10+**

## Command Groups

| Group | Purpose |
|-------|---------|
| `pa init` | Configure API token and username |
| `pa register` | Register a new PythonAnywhere account |
| `pa account` | list, switch, remove, login, token, extend |
| `pa files` | ls, upload, download, rm, share, unshare, share-status |
| `pa console` | list, create, send, kill, activate, get-or-create |
| `pa webapp` | create, config, static, reload, reload-crawler, hits, delete, enable, disable, logs, ssl |
| `pa deploy` | One-click deployment with --dry-run support |
| `pa status` | cpu, disk |
| `pa tasks` | list, create, delete, enable, disable |
| `pa always-on` | list, create, delete |

## Status

**Completed**: 42 commands implemented, 412 tests passing.

## Development

### Build and Test

```bash
# Install in development mode
pip install -e .

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/cli/test_account_cmd.py

# Run with coverage
pytest --cov=pa_cli --cov-report=html
```

### Documentation

```bash
# Install docs dependencies
pip install -r requirements-docs.txt

# Build Sphinx documentation
cd documentation
sphinx-build -b html . _build/html

# Local preview
sphinx-autobuild . _build/html
```

### Publishing

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Key Files

- `pa_cli/cli/main.py` - CLI entry point, registers all subcommands
- `pa_cli/config.py` - Configuration management
- `pa_cli/api/client.py` - Base API client with Token auth
- `pa_cli/crawler/account_crawler.py` - Browser simulation for account operations
- `pa_cli/workflows/deploy.py` - Deployment workflow orchestration

## Documentation

- **User docs**: https://pythonanywhere-clis.readthedocs.io
- **Source**: `documentation/` directory (Sphinx with MyST Markdown)
- **Dev docs**: `docs/` directory (development notes)

## Package Info

- **PyPI**: https://pypi.org/project/pythonanywhere-clis/
- **GitHub**: https://github.com/Duroxi/pythonanywhere-clis
- **Install**: `pip install pythonanywhere-clis`
