# Webapp Commands

Web application management commands for creating, configuring, and reloading web apps on PythonAnywhere.

---

## pa webapp create

Create a new web application.

### Syntax

```bash
pa webapp create <domain_name> [-p <python_version> | --python <python_version>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name, e.g., `myuser.pythonanywhere.com` |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-p`, `--python` | `python310` | Python version, e.g., `python38`, `python310`, `python311` |

### Examples

**Create with default Python version:**

```bash
$ pa webapp create myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com created with python310
```

**Specify Python version:**

```bash
$ pa webapp create myuser.pythonanywhere.com --python python311
Webapp myuser.pythonanywhere.com created with python311
```

### Error Scenarios

**Domain already exists:**

```bash
Error: API error 400: A web app with that domain name already exists.
```

**API authentication failed:**

```bash
Error: API error 401: Invalid token.
```

### Prerequisites

- Must run `pa init` first to complete account configuration

---

## pa webapp config

Configure the source directory and virtual environment path for a web application.

### Syntax

```bash
pa webapp config <domain_name> -s <source_dir> [-v <virtualenv>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name |

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `-s`, `--source-dir` | Yes | Absolute path to the source directory |
| `-v`, `--virtualenv` | No | Absolute path to the virtual environment |

### Examples

**Configure source directory:**

```bash
$ pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject
Webapp myuser.pythonanywhere.com configured.
```

**Configure both source directory and virtual environment:**

```bash
$ pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject -v /home/myuser/.virtualenvs/myproject
Webapp myuser.pythonanywhere.com configured.
```

### Error Scenarios

**Domain does not exist:**

```bash
Error: API error 404: Not found.
```

### Prerequisites

- Must run `pa init` first to complete account configuration
- Web app must already exist (created via `pa webapp create`)

---

## pa webapp static

Add a static file mapping to a web application.

### Syntax

```bash
pa webapp static <domain_name> --url <url_prefix> --path <directory_path>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name |

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `--url` | Yes | URL prefix, e.g., `/static/` |
| `--path` | Yes | Directory path on the server |

### Examples

```bash
$ pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static
Static mapping added: /static/ -> /home/myuser/myproject/static
```

### Error Scenarios

**Domain does not exist:**

```bash
Error: API error 404: Not found.
```

### Prerequisites

- Must run `pa init` first to complete account configuration
- Web app must already exist

---

## pa webapp reload

Reload a web application via the API.

### Syntax

```bash
pa webapp reload <domain_name>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name |

### Description

Uses Token authentication to trigger a web app reload via the REST API. This is the recommended reload method.

### Examples

```bash
$ pa webapp reload myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com reloaded.
```

### Error Scenarios

**Domain does not exist:**

```bash
Error: API error 404: Not found.
```

### Prerequisites

- Must run `pa init` first to complete account configuration

---

## pa webapp reload-crawler

Reload a web application by simulating browser interaction via the crawler (alternative to API reload).

### Syntax

```bash
pa webapp reload-crawler <domain_name>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name |

### Description

When API reload is not available (e.g., Token issues), this command can be used to simulate clicking the reload button via the crawler. This command requires a stored password (Session authentication).

### Examples

```bash
$ pa webapp reload-crawler myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com reloaded successfully.
```

### Error Scenarios

**Password not stored:**

```bash
Error: Password not found in config. Run 'pa account login' to store it.
```

**Login failed:**

```bash
Login failed. Check your credentials.
```

**Reload failed:**

```bash
Failed to reload webapp myuser.pythonanywhere.com.
```

### Prerequisites

- Must run `pa init` first to complete account configuration
- Must run `pa account login` first to store the password

---

## pa webapp hits

Retrieve traffic statistics for a web application.

### Syntax

```bash
pa webapp hits <domain_name>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain_name` | Yes | Domain name |

### Description

Retrieves traffic statistics for a web application by simulating browser interaction via the crawler. This command requires a stored password (Session authentication).

### Examples

```bash
$ pa webapp hits myuser.pythonanywhere.com
Hit statistics for myuser.pythonanywhere.com:
  today: 42
  yesterday: 128
  this_week: 500
  last_week: 1024
```

### Error Scenarios

**Password not stored:**

```bash
Error: Password not found in config. Run 'pa account login' to store it.
```

**Login failed:**

```bash
Login failed. Check your credentials.
```

### Prerequisites

- Must run `pa init` first to complete account configuration
- Must run `pa account login` first to store the password

---

## Typical Workflows

### Full Web App Deployment

```bash
# 1. Upload files
pa files upload ./myproject /home/myuser/myproject -r

# 2. Create web app
pa webapp create myuser.pythonanywhere.com

# 3. Configure source directory
pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject

# 4. Add static file mapping
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static

# 5. Reload the app
pa webapp reload myuser.pythonanywhere.com
```

### Day-to-Day Maintenance

```bash
# Check traffic
pa webapp hits myuser.pythonanywhere.com

# Reload after code updates
pa files upload ./app.py /home/myuser/myproject/app.py
pa webapp reload myuser.pythonanywhere.com

# Use crawler method when API reload fails
pa webapp reload-crawler myuser.pythonanywhere.com
```
