# Always-on 命令

Always-on 任务管理相关的命令，用于创建、查看和删除长驻进程。

> **注意**：Always-on 任务仅对付费账户可用。免费账户无法创建 Always-on 任务。

---

## 命令列表

| 命令 | 说明 | 认证方式 |
|------|------|---------|
| `pa always-on list` | 列出所有 Always-on 任务 | Token |
| `pa always-on create <command>` | 创建 Always-on 任务 | Token |
| `pa always-on delete <id>` | 删除 Always-on 任务 | Token |

---

## pa always-on list

列出当前账户的所有 Always-on 任务。

### 语法

```bash
pa always-on list
```

### 示例

```bash
$ pa always-on list
ID: 789, Command: python /home/user/webhook_server.py, Status: enabled
```

**无 Always-on 任务时：**

```bash
$ pa always-on list
No always-on tasks found.
```

### 输出字段

| 字段 | 说明 |
|------|------|
| ID | 任务 ID |
| Command | 要执行的命令 |
| Status | 状态（enabled/disabled） |

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa always-on create

创建一个新的 Always-on 任务。

### 语法

```bash
pa always-on create <command>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `command` | 是 | 要执行的命令 |

### 示例

```bash
$ pa always-on create "python /home/user/webhook_server.py"
Always-on task created: ID=789, Command=python /home/user/webhook_server.py
```

### 错误场景

**超出任务数量限制（免费账户）：**

```bash
Error: Always-on task limit reached. Upgrade your plan to add more.
```

**API 认证失败：**

```bash
Auth error: Invalid token.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需要付费账户

---

## pa always-on delete

删除一个 Always-on 任务。

### 语法

```bash
pa always-on delete <task_id> [-f | --force]
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
$ pa always-on delete 789
Are you sure you want to delete always-on task 789? [y/N]: y
Always-on task 789 deleted.
```

**强制删除（跳过确认）：**

```bash
$ pa always-on delete 789 -f
Always-on task 789 deleted.
```

### 错误场景

**任务不存在：**

```bash
Task not found: 789
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## 典型工作流

### 创建和管理 Always-on 任务

```bash
# 1. 查看现有任务
$ pa always-on list
No always-on tasks found.

# 2. 创建 webhook 服务器
$ pa always-on create "python /home/user/webhook_server.py"
Always-on task created: ID=789, Command=python /home/user/webhook_server.py

# 3. 查看任务状态
$ pa always-on list
ID: 789, Command: python /home/user/webhook_server.py, Status: enabled

# 4. 删除任务
$ pa always-on delete 789 -f
Always-on task 789 deleted.
```

---

## Always-on vs 定时任务

| 特性 | Always-on 任务 | 定时任务 |
|------|---------------|---------|
| 运行方式 | 持续运行 | 按计划执行 |
| 适用场景 | Webhook 服务器、聊天机器人 | 数据备份、报告生成 |
| 账户要求 | 付费账户 | 免费/付费均可 |
| 命令 | `pa always-on` | `pa tasks` |
