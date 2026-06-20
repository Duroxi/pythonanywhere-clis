# Status Commands

System status commands for viewing CPU and disk usage.

---

## pa status cpu

View CPU usage.

### Syntax

```bash
pa status cpu
```

### Description

Query daily CPU usage, quota, and reset time via REST API.

### Example

```bash
$ pa status cpu
[account: myuser]
CPU Usage:
  Used: 45.2 seconds
  Limit: 100 seconds
  Reset: 2026-06-21T07:00:00
```

### Output Fields

| Field | Description |
|-------|-------------|
| Used | CPU time used today (seconds) |
| Limit | Daily CPU time quota (seconds) |
| Reset | Quota reset time |

### Prerequisites

- Must run `pa init` first

---

## pa status disk

View disk usage.

### Syntax

```bash
pa status disk
```

### Description

Query disk usage via crawler. This command requires stored password (Session authentication).

### Example

```bash
$ pa status disk
[account: myuser]
Disk Usage:
  Used: 20.1 MB
  Total: 512.0 MB
  Usage: 4%
```

### Output Fields

| Field | Description |
|-------|-------------|
| Used | Disk space used |
| Total | Total disk space |
| Usage | Usage percentage |

### Prerequisites

- Must run `pa init` first
- Must run `pa account login` to store password

---

## Command Comparison

| Command | Auth | Source | Description |
|---------|------|--------|-------------|
| `pa status cpu` | Token | REST API | Real-time query |
| `pa status disk` | Password | Crawler | Requires login |
