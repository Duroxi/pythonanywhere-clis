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
| `pa status system-image` | Token | REST API | Get/set system image |

---

## pa status system-image

Get or set the system image.

### Syntax

```bash
pa status system-image [<image>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `image` | No | System image to set |

### Description

If no image is specified, shows the current system image and available images. If an image is specified, sets the system image.

### Examples

**Get current system image:**

```bash
$ pa status system-image
Current system image: ubuntu-20.04
Available images: ubuntu-20.04, ubuntu-22.04
```

**Set system image:**

```bash
$ pa status system-image ubuntu-22.04
System image set to ubuntu-22.04
```

### Prerequisites

- Must run `pa init` first
