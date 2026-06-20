# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-20

### Added

#### Account Management
- `pa init` - Configure account with interactive and command-line modes
- `pa register` - Register a new PythonAnywhere account
- `pa account list` - List all configured accounts
- `pa account switch` - Switch default account
- `pa account remove` - Remove an account
- `pa account login` - Store password for crawler operations
- `pa account token` - Fetch API token (auto-creates if not exists)
- `pa account extend` - Extend free tier account expiry

#### File Management
- `pa files ls` - List remote directory contents
- `pa files upload` - Upload files or directories
- `pa files download` - Download files or directories
- `pa files rm` - Delete files or directories
- `pa files share` - Share a file and get share link
- `pa files unshare` - Stop sharing a file
- `pa files share-status` - Check if a file is shared

#### Console Management
- `pa console list` - List all consoles
- `pa console create` - Create a new console
- `pa console send` - Send command and get output
- `pa console kill` - Kill a console
- `pa console activate` - Activate console via WebSocket
- `pa console get-or-create` - Get existing or create new console

#### Web App Management
- `pa webapp create` - Create a web app
- `pa webapp config` - Configure web app
- `pa webapp static` - Add static file mapping
- `pa webapp reload` - Reload web app (API)
- `pa webapp reload-crawler` - Reload web app (crawler)
- `pa webapp hits` - Get hit statistics
- `pa webapp delete` - Delete a web app
- `pa webapp enable` - Enable a web app
- `pa webapp disable` - Disable a web app
- `pa webapp logs` - Show web app logs
- `pa webapp ssl` - Show SSL certificate info

#### Deployment
- `pa deploy` - One-click deployment with progress bar
- `pa deploy --dry-run` - Preview deployment without executing

#### System Status
- `pa status cpu` - Show CPU usage
- `pa status disk` - Show disk usage

#### Scheduled Tasks
- `pa tasks list` - List all scheduled tasks
- `pa tasks create` - Create a new scheduled task
- `pa tasks delete` - Delete a scheduled task
- `pa tasks enable` - Enable a scheduled task
- `pa tasks disable` - Disable a scheduled task

#### Always-on Tasks
- `pa always-on list` - List all always-on tasks
- `pa always-on create` - Create a new always-on task
- `pa always-on delete` - Delete an always-on task

### Technical

- Token authentication for REST API operations
- Session authentication (crawler) for browser-only operations
- Multi-account support with account switching
- Configuration validation with clear error messages
- Comprehensive test suite (277+ tests)
- Error handling with custom exception hierarchy
- Progress bar for file uploads
- Dry-run support for deployments
