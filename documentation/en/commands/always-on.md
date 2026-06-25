# Always-on Commands

Always-on tasks management commands for creating, viewing, and deleting long-running processes.

> **Note**: Always-on tasks are only available for paid accounts. Free accounts cannot create Always-on tasks.

---

## Command List

| Command | Description | Auth |
|---------|-------------|------|
| `pa always-on list` | List all always-on tasks | Token |
| `pa always-on create <command>` | Create always-on task | Token |
| `pa always-on delete <id>` | Delete always-on task | Token |

---

## pa always-on list

List all always-on tasks for the current account.

### Syntax

```bash
pa always-on list
```

### Example

```bash
$ pa always-on list
ID: 789, Command: python /home/user/webhook_server.py, Status: enabled
```

**No tasks:**

```bash
$ pa always-on list
No always-on tasks found.
```

### Output Fields

| Field | Description |
|-------|-------------|
| ID | Task ID |
| Command | Command to execute |
| Status | Status (enabled/disabled) |

### Prerequisites

- Must run `pa init` first

---

## pa always-on create

Create a new always-on task.

### Syntax

```bash
pa always-on create <command>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | Yes | Command to execute |

### Example

```bash
$ pa always-on create "python /home/user/webhook_server.py"
Always-on task created: ID=789, Command=python /home/user/webhook_server.py
```

### Error Scenarios

**Task limit reached (free accounts):**

```bash
Error: Always-on task limit reached. Upgrade your plan to add more.
```

### Prerequisites

- Must run `pa init` first
- Requires paid account

---

## pa always-on delete

Delete an always-on task.

### Syntax

```bash
pa always-on delete <task_id> [-f | --force]
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
$ pa always-on delete 789 -f
Always-on task 789 deleted.
```

### Prerequisites

- Must run `pa init` first

---

## Always-on vs Scheduled Tasks

| Feature | Always-on Tasks | Scheduled Tasks |
|---------|-----------------|-----------------|
| Execution | Continuous | On schedule |
| Use Cases | Webhook servers, chat bots | Data backups, report generation |
| Account | Paid only | Free/Paid |
| Command | `pa always-on` | `pa tasks` |

---

## pa always-on update

Update an always-on task.

### Syntax

```bash
pa always-on update <task_id> [--command <command>] [--description <description>] [--enabled/--disabled]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | Yes | Task ID |

### Options

| Option | Description |
|--------|-------------|
| `-c`, `--command` | New command |
| `-d`, `--description` | New description |
| `-e`, `--enabled` | Enable task |
| `-E`, `--disabled` | Disable task |

### Examples

**Update command:**

```bash
$ pa always-on update 789 --command "python /home/user/new_server.py"
Always-on task 789 updated.
```

**Disable task:**

```bash
$ pa always-on update 789 --disabled
Always-on task 789 updated.
```

### Prerequisites

- Must run `pa init` first
- Requires paid account

---

## pa always-on restart

Restart an always-on task.

### Syntax

```bash
pa always-on restart <task_id>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | Yes | Task ID |

### Example

```bash
$ pa always-on restart 789
Always-on task 789 restarted.
```

### Prerequisites

- Must run `pa init` first
- Requires paid account
