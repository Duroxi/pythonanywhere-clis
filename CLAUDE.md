# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pythonanywhere-cli (`pa`) is a command-line interface for [PythonAnywhere](https://www.pythonanywhere.com), wrapping their REST API for browser-free resource management. Targets developers and AI agents on the free tier (no SSH).

## Architecture (from README design)

- **CLI entry point**: `pa` command with subcommands (`init`, `files`, `console`, `webapp`, `tasks`, `always-on`, `status`)
- **Config**: stored at `~/.pa-cli/config.json` (username, API token, host)
- **API client**: wraps PythonAnywhere REST API; standard endpoints rate-limited to 40 req/min, console `send_input` at 120 req/min
- **Python 3.8+**

## Command Groups

| Group | Purpose |
|-------|---------|
| `pa init` | Configure API token and username |
| `pa files` | ls, upload, download, rm |
| `pa console` | ls, create, send, output, kill |
| `pa webapp` | ls, reload, log |
| `pa tasks` | ls (scheduled tasks) |
| `pa always-on` | ls |
| `pa status` | CPU/disk usage |

## Status

Early stage — repo currently contains only README.md and LICENSE. No source code yet.
