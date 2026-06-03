# Console Commands

Console management commands for creating, operating, and managing remote consoles on PythonAnywhere.

## Command List

| Command | Description | Auth |
|---------|-------------|------|
| `pa console list` | List all consoles | Token |
| `pa console create` | Create new console | Token |
| `pa console send <id> <cmd>` | Send command and get output | Token |
| `pa console kill <id>` | Kill console | Token |
| `pa console activate <id>` | Activate console | Password |
| `pa console get-or-create` | Smart get or create | Password |

---

## pa console list

List all consoles for the current account.

### Syntax

```bash
pa console list
```

### Examples

```bash
$ pa console list
ID: 46955916, Name: Bash console 46955916
```

**When no consoles exist:**

```bash
$ pa console list
No consoles found.
```

### Error Scenarios

**API authentication failed:**

```bash
$ pa console list
Error: API error 401: Invalid token.
```

**Solution**: Run `pa account token` to re-fetch token.

### Prerequisites

- Must run `pa init` first

---

## pa console create

Create a new console.

### Syntax

```bash
pa console create [--executable <executable>]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--executable` | `bash` | Console executable, e.g. `bash`, `python3.10` |

### Examples

**Create default Bash console:**

```bash
$ pa console create
Console created: id=46991591, executable=bash
```

**Create Python console:**

```bash
$ pa console create --executable python3.10
Console created: id=46991592, executable=python3.10
```

### Error Scenarios

**Console limit exceeded (free tier max 2):**

```bash
$ pa console create
Error: API error 400: You have too many consoles.
```

**Solution**: Kill a console first with `pa console kill <id>`.

### Prerequisites

- Must run `pa init` first

---

## pa console send

Send a command to console and get output.

### Syntax

```bash
pa console send <console_id> <command> [--wait/--no-wait]
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `console_id` | Console ID |
| `command` | Command to execute |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--wait` | True | Wait and get output |
| `--no-wait` | - | Send command without waiting |

### Examples

**Send command and get output:**

```bash
$ pa console send 46955916 "echo hello"
16:16 ~ $ echo hello
hello
16:16 ~ $
```

**Send command without waiting:**

```bash
$ pa console send 46955916 "long-running-command" --no-wait
```

### Error Scenarios

**Console not started:**

```bash
$ pa console send 46955916 "ls"
Error: API error 412: Console not yet started.
```

**Solution**: Run `pa console activate 46955916` first.

**Console not found:**

```bash
$ pa console send 99999 "ls"
Error: API error 404: Not found.
```

**Solution**: Run `pa console list` to see available consoles.

### Prerequisites

- Must run `pa init` first
- Must create console first (`pa console create` or `pa console get-or-create`)
- If console not started, run `pa console activate <id>` first

---

## pa console kill

Kill a console.

### Syntax

```bash
pa console kill <console_id>
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `console_id` | Console ID |

### Examples

```bash
$ pa console kill 46991591
Console 46991591 killed.
```

### Error Scenarios

**Console not found:**

```bash
$ pa console kill 99999
Error: API error 404: Not found.
```

### Prerequisites

- Must run `pa init` first

---

## pa console activate

Activate a console via WebSocket. This command uses crawler to simulate browser behavior and start the console process.

### Syntax

```bash
pa console activate <console_id>
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `console_id` | Console ID |

### Description

PythonAnywhere consoles need to be opened in a browser once before they can be used via API. This command simulates opening the console page in a browser to start the console process.

### Examples

```bash
$ pa console activate 46955916
Console 46955916 activated successfully.
```

### Error Scenarios

**Password not configured:**

```bash
$ pa console activate 46955916
Error: Password not found. Run 'pa account login' first.
```

**Solution**: Run `pa account login` to store password.

**Login failed:**

```bash
$ pa console activate 46955916
Error: Login failed. Please check your username and password.
```

**Solution**: Check username and password in config file.

### Prerequisites

- Must run `pa init` first
- Config file must have password (entered during `pa init`, or later with `pa account login`)

---

## pa console get-or-create

Smart get or create console. This command automatically manages console lifecycle.

### Syntax

```bash
pa console get-or-create [--executable <executable>]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--executable` / `-e` | `bash` | Console executable |

### Logic

1. List existing consoles
2. If available console exists, return its ID (reuse)
3. If at limit (2), delete oldest and create new
4. If no consoles, create new

### Examples

```bash
$ pa console get-or-create
Console ready: 46955916
```

**With custom executable:**

```bash
$ pa console get-or-create -e python3.10
Console ready: 46991592
```

### Error Scenarios

**Password not configured:**

```bash
$ pa console get-or-create
Error: Password not found. Run 'pa account login' first.
```

**Solution**: Run `pa account login` to store password.

### Prerequisites

- Must run `pa init` first
- Config file must have password

---

## Typical Workflow

### Complete console usage flow

```bash
# 1. List existing consoles
$ pa console list
ID: 46955916, Name: Bash console 46955916

# 2. Activate console (if just created or not started)
$ pa console activate 46955916
Console 46955916 activated successfully.

# 3. Send command
$ pa console send 46955916 "ls -la"
total 8
drwxr-xr-x 2 user user 4096 Jun  3 16:16 .
drwxr-xr-x 3 user user 4096 Jun  3 16:16 ..
-rw-r--r-- 1 user user   18 Jun  3 16:16 README.txt

# 4. Clean up
$ pa console kill 46955916
Console 46955916 killed.
```

### Simplified flow with get-or-create

```bash
# Auto get or create console
$ pa console get-or-create
Console ready: 46955916

# Use directly (if console already activated)
$ pa console send 46955916 "echo hello"
hello

# If console not activated, activate first
$ pa console activate 46955916
Console 46955916 activated successfully.

$ pa console send 46955916 "echo hello"
hello
```
