# Tasks Commands

Scheduled tasks management commands for creating, viewing, enabling/disabling, and deleting scheduled tasks.

---

## Command List

| Command | Description | Auth |
|---------|-------------|------|
| `pa tasks list` | List all scheduled tasks | Token |
| `pa tasks create <command>` | Create scheduled task | Token |
| `pa tasks delete <id>` | Delete scheduled task | Token |
| `pa tasks enable <id>` | Enable scheduled task | Token |
| `pa tasks disable <id>` | Disable scheduled task | Token |

---

## pa tasks list

List all scheduled tasks for the current account.

### Syntax

```bash
pa tasks list
```

### Example

```bash
$ pa tasks list
ID: 12345, Command: python /home/user/backup.py, Interval: daily, Status: enabled
ID: 12346, Command: curl https://api.example.com, Interval: hourly, Status: disabled
```

**No tasks:**

```bash
$ pa tasks list
No scheduled tasks found.
```

### Output Fields

| Field | Description |
|-------|-------------|
| ID | Task ID |
| Command | Command to execute |
| Interval | Execution interval (hourly, daily, weekly, monthly) |
| Status | Status (enabled/disabled) |

### Prerequisites

- Must run `pa init` first

---

## pa tasks create

Create a new scheduled task.

### Syntax

```bash
pa tasks create <command> [--interval <interval>] [--hour <hour>] [--minute <minute>] [--description <description>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | Yes | Command to execute |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-i`, `--interval` | `daily` | Interval: hourly, daily, weekly, monthly |
| `-H`, `--hour` | `0` | Hour to run (0-23) |
| `-M`, `--minute` | `0` | Minute to run (0-59) |
| `-d`, `--description` | `""` | Task description |

### Example

```bash
$ pa tasks create "python /home/user/backup.py" --interval daily --hour 0 --minute 0
Task created: ID=12345, Command=python /home/user/backup.py
```

### Prerequisites

- Must run `pa init` first

---

## pa tasks delete

Delete a scheduled task.

### Syntax

```bash
pa tasks delete <task_id> [-f | --force]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | Yes | Task ID |

### Options

| Option | Description |
|--------|-------------|
| `-f`, `--force` | Skip confirmation |

### Example

```bash
$ pa tasks delete 12345 -f
Task 12345 deleted.
```

### Prerequisites

- Must run `pa init` first

---

## pa tasks enable

Enable a scheduled task.

### Syntax

```bash
pa tasks enable <task_id>
```

### Example

```bash
$ pa tasks enable 12345
Task 12345 enabled.
```

### Prerequisites

- Must run `pa init` first

---

## pa tasks disable

Disable a scheduled task.

### Syntax

```bash
pa tasks disable <task_id>
```

### Example

```bash
$ pa tasks disable 12345
Task 12345 disabled.
```

### Prerequisites

- Must run `pa init` first
