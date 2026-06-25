# Databases Commands

Database management commands for viewing MySQL database information.

---

## pa databases mysql

Show MySQL database information.

### Syntax

```bash
pa databases mysql
```

### Description

Retrieves information about MySQL databases associated with the current account.

### Example

```bash
$ pa databases mysql
MySQL Databases:
  myuser$mydb: 10.5 MB
  myuser$testdb: 2.1 MB
```

**No databases:**

```bash
$ pa databases mysql
No MySQL databases found.
```

### Output Fields

| Field | Description |
|-------|-------------|
| database_name | Database name |
| size | Database size |

### Prerequisites

- Must run `pa init` first
