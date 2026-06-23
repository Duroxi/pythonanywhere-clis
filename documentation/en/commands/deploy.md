# Deploy Command

One-command deployment that automatically deploys a local project to PythonAnywhere.

---

## pa deploy

Deploy a local project directory to PythonAnywhere in one command.

### Syntax

```bash
pa deploy <local_dir> [--domain <domain>] [--python <python_version>] [--dry-run]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `local_dir` | Yes | Local project directory path |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-d`, `--domain` | `{username}.pythonanywhere.com` | Target domain name |
| `-p`, `--python` | `python310` | Python version |
| `-n`, `--dry-run` | False | Preview deploy without executing |

### Description

The one-command deployment automatically performs the following steps:

1. **Upload files** - Recursively upload the entire project directory to `/home/{username}/{dirname}`
2. **Create console** - Automatically create a Bash console for subsequent operations
3. **Install dependencies** - If the project contains `requirements.txt`, automatically create a virtual environment and install dependencies
4. **Create web app** - Create or reuse an existing web app
5. **Configure app** - Set the source directory; if a `static` directory exists, automatically add a static file mapping
6. **Reload app** - Trigger a web app reload

### Examples

**Deploy to the default domain:**

```bash
$ pa deploy ./my-site
Uploading ./my-site to /home/myuser/my-site...
Uploaded 15 files.
Setting up environment...
Creating webapp myuser.pythonanywhere.com...
Reloading webapp...

Deployed! Visit: https://myuser.pythonanywhere.com
```

**Deploy to a custom domain:**

```bash
$ pa deploy ./my-site --domain mysite.pythonanywhere.com
Uploading ./my-site to /home/myuser/my-site...
Uploaded 8 files.
Setting up environment...
Creating webapp mysite.pythonanywhere.com...
Reloading webapp...

Deployed! Visit: https://mysite.pythonanywhere.com
```

**Specify Python version:**

```bash
$ pa deploy ./my-site --python python311
```

### Deployment Flow Details

#### Step 1: File Upload

Traverses all files under `local_dir` and uploads them to the remote `/home/{username}/{dirname}/` while preserving the directory structure.

#### Step 2: Environment Configuration

Executes commands via the console:
- Navigate to the project directory
- If `requirements.txt` exists:
  - Create a virtual environment using `mkvirtualenv`
  - Install dependencies using `pip install -r requirements.txt`

#### Step 3: Web App Configuration

- Create a web app (skip if it already exists)
- Set the source directory to the upload path
- If a local `static` directory exists, automatically add a `/static/` static file mapping

#### Step 4: Reload

Trigger a web app reload to apply changes.

### Project Structure Requirements

The deployment command makes the following assumptions about the project structure:

```
my-site/
├── app.py              # Application entry point (optional)
├── requirements.txt    # Python dependencies (optional, auto-installed)
├── static/             # Static files directory (optional, auto-mapped)
└── ...                 # Other project files
```

### Error Scenarios

**Local directory does not exist:**

```bash
Error: ./nonexistent is not a directory
```

**API authentication failed:**

```bash
Error: API error 401: Invalid token.
```

**Console operation timeout:**

The maximum wait time for console commands during deployment is 300 seconds (5 minutes). If operations such as dependency installation time out, the deployment may be incomplete.

### Prerequisites

- Must run `pa init` first to complete account configuration
- Local directory must exist and contain project files

### Notes

- Deployment will overwrite files in the remote directory with the same name
- The virtual environment name uses the project directory name
- If the web app already exists, it will not be recreated, but the configuration will be updated
- After deployment is complete, you can access the domain directly to view the application
- There is no progress bar during the entire deployment process, only stage-by-stage text output

---

## Relationship with Other Commands

`pa deploy` is a convenience command equivalent to manually executing the following command sequence:

```bash
# Equivalent operations
pa files upload ./my-site /home/myuser/my-site -r
pa console create
pa console send <id> "cd /home/myuser/my-site"
pa console send <id> "mkvirtualenv my-site --python=/usr/bin/python310"
pa console send <id> "workon my-site && pip install -r requirements.txt"
pa webapp create myuser.pythonanywhere.com
pa webapp config myuser.pythonanywhere.com -s /home/myuser/my-site
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/my-site/static
pa webapp reload myuser.pythonanywhere.com
```

If you need more granular control, you can use the individual commands listed above step by step.
