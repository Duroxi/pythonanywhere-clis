# Console 命令

控制台管理相关的命令，用于在 PythonAnywhere 上创建、操作和管理远程控制台。

## 命令列表

| 命令 | 说明 | 认证方式 |
|------|------|---------|
| `pa console list` | 列出所有 console | Token |
| `pa console create` | 创建新 console | Token |
| `pa console send <id> <cmd>` | 发送命令并获取输出 | Token |
| `pa console kill <id>` | 销毁 console | Token |
| `pa console activate <id>` | 激活 console | 密码 |
| `pa console get-or-create` | 智能获取或创建 | 密码 |

---

## pa console list

列出当前账户的所有控制台。

### 语法

```bash
pa console list
```

### 示例

```bash
$ pa console list
ID: 46955916, Name: Bash console 46955916
```

**无控制台时：**

```bash
$ pa console list
No consoles found.
```

### 错误场景

**API 认证失败：**

```bash
$ pa console list
Error: API error 401: Invalid token.
```

**解决方案**：运行 `pa account token` 重新获取 token。

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa console create

创建一个新的控制台。

### 语法

```bash
pa console create [--executable <executable>]
```

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--executable` | `bash` | 控制台可执行程序，如 `bash`、`python3.10` |

### 示例

**创建默认 Bash 控制台：**

```bash
$ pa console create
Console created: id=46991591, executable=bash
```

**创建 Python 控制台：**

```bash
$ pa console create --executable python3.10
Console created: id=46991592, executable=python3.10
```

### 错误场景

**超出控制台数量限制（免费用户最多 2 个）：**

```bash
$ pa console create
Error: API error 400: You have too many consoles.
```

**解决方案**：先用 `pa console kill <id>` 销毁一个 console。

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa console send

向控制台发送命令并获取输出。

### 语法

```bash
pa console send <console_id> <command> [--wait/--no-wait]
```

### 参数

| 参数 | 说明 |
|------|------|
| `console_id` | 控制台 ID |
| `command` | 要执行的命令 |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--wait` | True | 等待并获取输出 |
| `--no-wait` | - | 只发送命令，不等待输出 |

### 示例

**发送命令并获取输出：**

```bash
$ pa console send 46955916 "echo hello"
16:16 ~ $ echo hello
hello
16:16 ~ $
```

**只发送命令，不等待：**

```bash
$ pa console send 46955916 "long-running-command" --no-wait
```

### 错误场景

**Console 未启动：**

```bash
$ pa console send 46955916 "ls"
Error: API error 412: Console not yet started.
```

**解决方案**：先运行 `pa console activate 46955916` 激活 console。

**Console 不存在：**

```bash
$ pa console send 99999 "ls"
Error: API error 404: Not found.
```

**解决方案**：运行 `pa console list` 查看可用的 console。

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先创建 console（`pa console create` 或 `pa console get-or-create`）
- 如果 console 未启动，需先运行 `pa console activate <id>`

---

## pa console kill

销毁一个控制台。

### 语法

```bash
pa console kill <console_id>
```

### 参数

| 参数 | 说明 |
|------|------|
| `console_id` | 控制台 ID |

### 示例

```bash
$ pa console kill 46991591
Console 46991591 killed.
```

### 错误场景

**Console 不存在：**

```bash
$ pa console kill 99999
Error: API error 404: Not found.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa console activate

通过 WebSocket 激活控制台。此命令使用爬虫模拟浏览器行为来启动 console 进程。

### 语法

```bash
pa console activate <console_id>
```

### 参数

| 参数 | 说明 |
|------|------|
| `console_id` | 控制台 ID |

### 说明

PythonAnywhere 的 console 需要先在浏览器中打开一次才能通过 API 使用。此命令模拟浏览器打开 console 页面，启动 console 进程。

### 示例

```bash
$ pa console activate 46955916
Console 46955916 activated successfully.
```

### 错误场景

**密码未配置：**

```bash
$ pa console activate 46955916
Error: Password not found. Run 'pa account login' first.
```

**解决方案**：运行 `pa account login` 存储密码。

**登录失败：**

```bash
$ pa console activate 46955916
Error: Login failed. Please check your username and password.
```

**解决方案**：检查配置文件中的用户名和密码是否正确。

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 配置文件中需要有密码（`pa init` 时输入，或之后用 `pa account login` 存储）

---

## pa console get-or-create

智能获取或创建控制台。此命令会自动管理 console 生命周期。

### 语法

```bash
pa console get-or-create [--executable <executable>]
```

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--executable` / `-e` | `bash` | 控制台可执行程序 |

### 逻辑

1. 列出现有 consoles
2. 如果有可用的 console，返回其 ID（复用）
3. 如果达到上限（2 个），删除最旧的，创建新的
4. 如果没有 console，创建新的

### 示例

```bash
$ pa console get-or-create
Console ready: 46955916
```

**使用自定义 executable：**

```bash
$ pa console get-or-create -e python3.10
Console ready: 46991592
```

### 错误场景

**密码未配置：**

```bash
$ pa console get-or-create
Error: Password not found. Run 'pa account login' first.
```

**解决方案**：运行 `pa account login` 存储密码。

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 配置文件中需要有密码

---

## 典型工作流程

### 完整的 console 使用流程

```bash
# 1. 查看现有 consoles
$ pa console list
ID: 46955916, Name: Bash console 46955916

# 2. 激活 console（如果刚创建或未启动）
$ pa console activate 46955916
Console 46955916 activated successfully.

# 3. 发送命令
$ pa console send 46955916 "ls -la"
total 8
drwxr-xr-x 2 user user 4096 Jun  3 16:16 .
drwxr-xr-x 3 user user 4096 Jun  3 16:16 ..
-rw-r--r-- 1 user user   18 Jun  3 16:16 README.txt

# 4. 用完后销毁
$ pa console kill 46955916
Console 46955916 killed.
```

### 使用 get-or-create 简化流程

```bash
# 自动获取或创建 console
$ pa console get-or-create
Console ready: 46955916

# 直接使用（如果 console 已激活）
$ pa console send 46955916 "echo hello"
hello

# 如果 console 未激活，先激活
$ pa console activate 46955916
Console 46955916 activated successfully.

$ pa console send 46955916 "echo hello"
hello
```
