# Webapp 命令

Web 应用管理相关的命令，用于创建、配置、重载 PythonAnywhere 上的 Web 应用。

---

## pa webapp create

创建一个新的 Web 应用。

### 语法

```bash
pa webapp create <domain_name> [-p <python_version> | --python <python_version>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名，如 `myuser.pythonanywhere.com` |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-p`, `--python` | `python310` | Python 版本，如 `python38`、`python310`、`python311` |

### 示例

**使用默认 Python 版本创建：**

```bash
$ pa webapp create myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com created with python310
```

**指定 Python 版本：**

```bash
$ pa webapp create myuser.pythonanywhere.com --python python311
Webapp myuser.pythonanywhere.com created with python311
```

### 错误场景

**域名已存在：**

```bash
Error: API error 400: A web app with that domain name already exists.
```

**API 认证失败：**

```bash
Error: API error 401: Invalid token.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa webapp config

配置 Web 应用的源码目录和虚拟环境路径。

### 语法

```bash
pa webapp config <domain_name> -s <source_dir> [-v <virtualenv>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 选项

| 选项 | 必填 | 说明 |
|------|------|------|
| `-s`, `--source-dir` | 是 | 源码目录的绝对路径 |
| `-v`, `--virtualenv` | 否 | 虚拟环境的绝对路径 |

### 示例

**配置源码目录：**

```bash
$ pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject
Webapp myuser.pythonanywhere.com configured.
```

**同时配置源码目录和虚拟环境：**

```bash
$ pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject -v /home/myuser/.virtualenvs/myproject
Webapp myuser.pythonanywhere.com configured.
```

### 错误场景

**域名不存在：**

```bash
Error: API error 404: Not found.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- Web 应用需已存在（通过 `pa webapp create` 创建）

---

## pa webapp static

为 Web 应用添加静态文件映射。

### 语法

```bash
pa webapp static <domain_name> --url <url_prefix> --path <directory_path>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 选项

| 选项 | 必填 | 说明 |
|------|------|------|
| `--url` | 是 | URL 前缀，如 `/static/` |
| `--path` | 是 | 服务器上的目录路径 |

### 示例

```bash
$ pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static
Static mapping added: /static/ -> /home/myuser/myproject/static
```

### 错误场景

**域名不存在：**

```bash
Error: API error 404: Not found.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- Web 应用需已存在

---

## pa webapp reload

通过 API 重载 Web 应用。

### 语法

```bash
pa webapp reload <domain_name>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 说明

使用 Token 认证，通过 REST API 触发 Web 应用重载。这是推荐的重载方式。

### 示例

```bash
$ pa webapp reload myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com reloaded.
```

### 错误场景

**域名不存在：**

```bash
Error: API error 404: Not found.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa webapp reload-crawler

通过爬虫模拟浏览器重载 Web 应用（API 重载的替代方案）。

### 语法

```bash
pa webapp reload-crawler <domain_name>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 说明

当 API 重载不可用时（如 Token 问题），可使用此命令通过爬虫模拟浏览器点击重载按钮。此命令需要存储密码（Session 认证）。

### 示例

```bash
$ pa webapp reload-crawler myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com reloaded successfully.
```

### 错误场景

**密码未存储：**

```bash
Error: Password not found in config. Run 'pa account login' to store it.
```

**登录失败：**

```bash
Login failed. Check your credentials.
```

**重载失败：**

```bash
Failed to reload webapp myuser.pythonanywhere.com.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## pa webapp hits

获取 Web 应用的访问统计信息。

### 语法

```bash
pa webapp hits <domain_name>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 说明

通过爬虫模拟浏览器获取 Web 应用的访问统计数据。此命令需要存储密码（Session 认证）。

### 示例

```bash
$ pa webapp hits myuser.pythonanywhere.com
Hit statistics for myuser.pythonanywhere.com:
  today: 42
  yesterday: 128
  this_week: 500
  last_week: 1024
```

### 错误场景

**密码未存储：**

```bash
Error: Password not found in config. Run 'pa account login' to store it.
```

**登录失败：**

```bash
Login failed. Check your credentials.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## pa webapp delete

删除一个 Web 应用。

### 语法

```bash
pa webapp delete <domain_name> [-f | --force]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 选项

| 选项 | 说明 |
|------|------|
| `-f`, `--force` | 跳过确认提示 |

### 示例

```bash
$ pa webapp delete myuser.pythonanywhere.com
Are you sure you want to delete myuser.pythonanywhere.com? [y/N]: y
Webapp myuser.pythonanywhere.com deleted.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa webapp enable

启用一个 Web 应用。

### 语法

```bash
pa webapp enable <domain_name>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 说明

通过爬虫模拟浏览器启用 Web 应用。此命令需要存储密码（Session 认证）。

### 示例

```bash
$ pa webapp enable myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com enabled.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## pa webapp disable

禁用一个 Web 应用。

### 语法

```bash
pa webapp disable <domain_name>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 是 | 域名 |

### 说明

通过爬虫模拟浏览器禁用 Web 应用。此命令需要存储密码（Session 认证）。

### 示例

```bash
$ pa webapp disable myuser.pythonanywhere.com
Webapp myuser.pythonanywhere.com disabled.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## pa webapp logs

查看 Web 应用的日志。

### 语法

```bash
pa webapp logs [<domain_name>] [-t <log_type>] [-n <lines>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 否 | 域名（默认：`{username}.pythonanywhere.com`） |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-t`, `--type` | `error` | 日志类型：access, error, server |
| `-n`, `--lines` | `50` | 显示行数 |

### 示例

**查看 error 日志（默认）：**

```bash
$ pa webapp logs
2026-06-20 10:15:30,123: Exception on /api/data [GET]
Traceback (most recent call last):
  File "/home/user/app.py", line 42, in get_data
    raise ValueError("Invalid input")
ValueError: Invalid input
```

**查看 access 日志：**

```bash
$ pa webapp logs --type access --lines 5
47.79.194.217 - - [20/Jun/2026:10:15:30 +0000] "GET / HTTP/1.1" 200 752
```

**查看 server 日志：**

```bash
$ pa webapp logs --type server
2026-06-20 10:00:00 *** Starting uWSGI 2.0.20 ***
```

### 日志类型

| 类型 | 说明 |
|------|------|
| `access` | HTTP 访问日志 |
| `error` | 错误日志（默认） |
| `server` | 服务器日志 |

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa webapp ssl

查看 Web 应用的 SSL 证书信息。

### 语法

```bash
pa webapp ssl [<domain_name>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `domain_name` | 否 | 域名（默认：`{username}.pythonanywhere.com`） |

### 示例

```bash
$ pa webapp ssl
SSL Certificate Info for myuser.pythonanywhere.com:
  Type: pythonanywhere-subdomain
```

### 证书类型

| 类型 | 说明 |
|------|------|
| `pythonanywhere-subdomain` | PythonAnywhere 子域名证书（免费） |
| `lets-encrypt` | Let's Encrypt 证书（付费） |
| `custom` | 自定义证书（付费） |

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## 典型工作流

### 完整部署一个 Web 应用

```bash
# 1. 上传文件
pa files upload ./myproject /home/myuser/myproject -r

# 2. 创建 Web 应用
pa webapp create myuser.pythonanywhere.com

# 3. 配置源码目录
pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject

# 4. 添加静态文件映射
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static

# 5. 重载应用
pa webapp reload myuser.pythonanywhere.com
```

### 日常维护

```bash
# 检查访问量
pa webapp hits myuser.pythonanywhere.com

# 查看错误日志
pa webapp logs --type error --lines 20

# 查看 SSL 证书
pa webapp ssl

# 更新代码后重载
pa files upload ./app.py /home/myuser/myproject/app.py
pa webapp reload myuser.pythonanywhere.com

# API 重载失败时使用爬虫方式
pa webapp reload-crawler myuser.pythonanywhere.com
```

### 禁用/启用应用

```bash
# 临时禁用应用
pa webapp disable myuser.pythonanywhere.com

# 重新启用应用
pa webapp enable myuser.pythonanywhere.com
```
