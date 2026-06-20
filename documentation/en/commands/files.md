# Files Commands

File management commands for uploading local files to the PythonAnywhere server.

---

## pa files upload

Upload a file or directory to PythonAnywhere.

### Syntax

```bash
pa files upload <local_path> <remote_path> [-r | --recursive]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `local_path` | Yes | Local file or directory path |
| `remote_path` | Yes | Remote path on PythonAnywhere |

### Options

| Option | Description |
|--------|-------------|
| `-r`, `--recursive` | Recursively upload a directory and all its contents |

### Description

- Uses Token authentication for upload via REST API
- Remote paths use `/home/{username}/` as the root directory
- Single file upload returns an HTTP status code
- Directory upload automatically traverses all sub-files, with path separators normalized to `/`

### Examples

**Upload a single file:**

```bash
$ pa files upload ./app.py /home/myuser/myproject/app.py
Uploaded ./app.py -> /home/myuser/myproject/app.py (HTTP 200)
```

**Upload an entire directory:**

```bash
$ pa files upload ./myproject /home/myuser/myproject -r
Uploaded 15 files to /home/myuser/myproject
```

**Upload to user root directory:**

```bash
$ pa files upload ./config.json /home/myuser/config.json
Uploaded ./config.json -> /home/myuser/config.json (HTTP 200)
```

### Error Scenarios

**Local path does not exist:**

```bash
$ pa files upload ./nonexistent /home/myuser/test
Error: ./nonexistent does not exist
```

**Uploading a directory without `-r`:**

```bash
$ pa files upload ./myproject /home/myuser/myproject
Error: Use -r/--recursive to upload directories
```

**API authentication failed (invalid token):**

```bash
Error: API error 401: Invalid token.
```

**No write permission to remote path:**

```bash
Error: API error 403: You do not have permission to write to this path.
```

**Upload failed:**

```bash
Error: Upload failed: 500 Internal Server Error
```

### Prerequisites

- Must run `pa init` first to complete account configuration (including a valid API Token)

### Notes

- Upload operations will overwrite remote files with the same name
- Directory upload preserves the local directory structure; the last directory name of `local_path` becomes the remote directory name
- Progress bar is displayed for large file uploads

---

## pa files ls

List remote directory contents.

### Syntax

```bash
pa files ls [<remote_path>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | No | Remote path (default: user home directory) |

### Example

```bash
$ pa files ls
  .bashrc
  .profile
  myproject/
  README.txt
```

### Prerequisites

- Must run `pa init` first

---

## pa files download

Download files or directories to local.

### Syntax

```bash
pa files download <remote_path> [<local_path>] [-r | --recursive]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | Yes | Remote file or directory path |
| `local_path` | No | Local destination path (default: current directory) |

### Options

| Option | Description |
|--------|-------------|
| `-r`, `--recursive` | Recursively download directory |

### Example

```bash
$ pa files download /home/myuser/app.py ./app.py
Downloaded /home/myuser/app.py -> app.py
```

### Prerequisites

- Must run `pa init` first

---

## pa files rm

Delete remote files or directories.

### Syntax

```bash
pa files rm <remote_path> [-r | --recursive] [-f | --force]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | Yes | Remote file or directory path |

### Options

| Option | Description |
|--------|-------------|
| `-r`, `--recursive` | Recursively delete directory |
| `-f`, `--force` | Skip confirmation |

### Example

```bash
$ pa files rm /home/myuser/old.txt
Are you sure you want to delete '/home/myuser/old.txt'? [y/N]: y
Deleted /home/myuser/old.txt
```

### Prerequisites

- Must run `pa init` first

---

## pa files share

Share a file and get share link.

### Syntax

```bash
pa files share <remote_path>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | Yes | Remote file path |

### Example

```bash
$ pa files share /home/myuser/data.csv
Share link: https://www.pythonanywhere.com/user/myuser/shares/abc123/
```

### Prerequisites

- Must run `pa init` first

---

## pa files unshare

Stop sharing a file.

### Syntax

```bash
pa files unshare <remote_path>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | Yes | Remote file path |

### Example

```bash
$ pa files unshare /home/myuser/data.csv
Stopped sharing: /home/myuser/data.csv
```

### Prerequisites

- Must run `pa init` first

---

## pa files share-status

Check if a file is shared.

### Syntax

```bash
pa files share-status <remote_path>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `remote_path` | Yes | Remote file path |

### Example

```bash
$ pa files share-status /home/myuser/data.csv
File is shared: https://www.pythonanywhere.com/user/myuser/shares/abc123/
```

### Prerequisites

- Must run `pa init` first

---

## Typical Workflows

### File Sharing

```bash
# 1. Share a file
$ pa files share /home/myuser/report.pdf
Share link: https://www.pythonanywhere.com/user/myuser/shares/abc123/

# 2. Check share status
$ pa files share-status /home/myuser/report.pdf
File is shared: https://www.pythonanywhere.com/user/myuser/shares/abc123/

# 3. Stop sharing
$ pa files unshare /home/myuser/report.pdf
Stopped sharing: /home/myuser/report.pdf
```

### File Backup

```bash
# 1. Download entire project
$ pa files download /home/myuser/myproject ./backup/myproject -r
Downloaded 50 files to backup/myproject

# 2. Download single file
$ pa files download /home/myuser/config.json ./config.json
Downloaded /home/myuser/config.json -> config.json
```
