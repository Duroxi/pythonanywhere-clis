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
