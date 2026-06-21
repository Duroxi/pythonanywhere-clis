# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pythonanywhere-clis (`pa`) is a command-line interface for [PythonAnywhere](https://www.pythonanywhere.com), wrapping their REST API for browser-free resource management. Targets developers and AI agents on the free tier (no SSH).

## Architecture

- **CLI entry point**: `pa` command with subcommands
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

**Completed**: 48 commands implemented, 277+ tests passing.

See README.md for full command reference and Roadmap.
