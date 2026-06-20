# Tasks 命令

定时任务管理相关的命令，用于创建、查看、启用/禁用和删除定时任务。

---

## 命令列表

| 命令 | 说明 | 认证方式 |
|------|------|---------|
| `pa tasks list` | 列出所有定时任务 | Token |
| `pa tasks create <command>` | 创建定时任务 | Token |
| `pa tasks delete <id>` | 删除定时任务 | Token |
| `pa tasks enable <id>` | 启用定时任务 | Token |
| `pa tasks disable <id>` | 禁用定时任务 | Token |

---

## pa tasks list

列出当前账户的所有定时任务。

### 语法

```bash
pa tasks list
```

### 示例

```bash
$ pa tasks list
ID: 12345, Command: python /home/user/backup.py, Interval: daily, Status: enabled
ID: 12346, Command: curl https://api.example.com, Interval: hourly, Status: disabled
```

**无定时任务时：**

```bash
$ pa tasks list
No scheduled tasks found.
```

### 输出字段

| 字段 | 说明 |
|------|------|
| ID | 任务 ID |
| Command | 要执行的命令 |
| Interval | 执行间隔（hourly, daily, weekly, monthly） |
| Status | 状态（enabled/disabled） |

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa tasks create

创建一个新的定时任务。

### 语法

```bash
pa tasks create <command> [--interval <interval>] [--hour <hour>] [--minute <minute>] [--description <description>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `command` | 是 | 要执行的命令 |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-i`, `--interval` | `daily` | 执行间隔：hourly, daily, weekly, monthly |
| `-H`, `--hour` | `0` | 执行小时（0-23） |
| `-M`, `--minute` | `0` | 执行分钟（0-59） |
| `-d`, `--description` | `""` | 任务描述 |

### 示例

**创建每日任务：**

```bash
$ pa tasks create "python /home/user/backup.py" --interval daily --hour 0 --minute 0
Task created: ID=12345, Command=python /home/user/backup.py
```

**创建每小时任务：**

```bash
$ pa tasks create "curl https://api.example.com/health" --interval hourly
Task created: ID=12346, Command=curl https://api.example.com/health
```

**带描述的任务：**

```bash
$ pa tasks create "python /home/user/report.py" --description "Daily report generation"
Task created: ID=12347, Command=python /home/user/report.py
```

### 错误场景

**API 认证失败：**

```bash
Auth error: Invalid token.
```

**超出任务数量限制：**

```bash
API error: You have reached your scheduled task limit.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa tasks delete

删除一个定时任务。

### 语法

```bash
pa tasks delete <task_id> [-f | --force]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `task_id` | 是 | 任务 ID |

### 选项

| 选项 | 说明 |
|------|------|
| `-f`, `--force` | 跳过确认提示 |

### 示例

**删除任务（带确认）：**

```bash
$ pa tasks delete 12345
Are you sure you want to delete task 12345? [y/N]: y
Task 12345 deleted.
```

**强制删除（跳过确认）：**

```bash
$ pa tasks delete 12345 -f
Task 12345 deleted.
```

### 错误场景

**任务不存在：**

```bash
Task not found: 12345
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa tasks enable

启用一个定时任务。

### 语法

```bash
pa tasks enable <task_id>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `task_id` | 是 | 任务 ID |

### 示例

```bash
$ pa tasks enable 12345
Task 12345 enabled.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa tasks disable

禁用一个定时任务。

### 语法

```bash
pa tasks disable <task_id>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `task_id` | 是 | 任务 ID |

### 示例

```bash
$ pa tasks disable 12345
Task 12345 disabled.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## 典型工作流

### 创建和管理定时任务

```bash
# 1. 查看现有任务
$ pa tasks list
No scheduled tasks found.

# 2. 创建每日备份任务
$ pa tasks create "python /home/user/backup.py" --interval daily --hour 2 --minute 0
Task created: ID=12345, Command=python /home/user/backup.py

# 3. 查看任务状态
$ pa tasks list
ID: 12345, Command: python /home/user/backup.py, Interval: daily, Status: enabled

# 4. 临时禁用任务
$ pa tasks disable 12345
Task 12345 disabled.

# 5. 重新启用任务
$ pa tasks enable 12345
Task 12345 enabled.

# 6. 删除任务
$ pa tasks delete 12345 -f
Task 12345 deleted.
```
