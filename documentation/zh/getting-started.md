# 快速开始指南

欢迎使用 pythonanywhere-cli (`pa`)！本指南将帮助你从零开始，将本地 Python 项目部署到 PythonAnywhere。

## 目录

- [什么是 pythonanywhere-cli](#什么是-pythonanywhere-cli)
- [环境要求](#环境要求)
- [安装](#安装)
- [账号配置](#账号配置)
- [第一个项目部署](#第一个项目部署)
- [常用命令速查](#常用命令速查)
- [命令依赖关系](#命令依赖关系)
- [常见问题](#常见问题)

---

## 什么是 pythonanywhere-cli

pythonanywhere-cli 是一个命令行工具，用于自动化管理 PythonAnywhere 上的资源。它的核心价值是：

- **一行命令部署** - `pa deploy ./my-site` 完成上传、环境配置、网站创建、重载全流程
- **无需浏览器** - 所有操作通过命令行完成，适合脚本和 AI Agent 调用
- **免费套餐友好** - 专为 PythonAnywhere 免费用户设计

---

## 环境要求

| 要求 | 版本 |
|------|------|
| Python | 3.10 或更高 |
| 操作系统 | Windows / macOS / Linux |
| 网络 | 需要能访问 pythonanywhere.com |

---

## 安装

### 方式一：从源码安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/Duroxi/pythonanywhere-cli.git
cd pythonanywhere-cli

# 安装（开发模式）
pip install -e .
```

### 方式二：直接安装依赖

```bash
pip install typer requests beautifulsoup4 websocket-client
```

### 验证安装

```bash
$ pa --help

 Usage: pa [OPTIONS] COMMAND [ARGS]...

 CLI tool for automating PythonAnywhere deployments.

┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --install-completion          Install completion for the current shell.     │
│ --show-completion             Show completion for the current shell, to     │
│                               copy it or customize the installation.        │
│ --help                        Show this message and exit.                   │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Commands ──────────────────────────────────────────────────────────────────┐
│ init       Configure PythonAnywhere account                                 │
│ files      Manage files on PythonAnywhere                                   │
│ console    Manage consoles on PythonAnywhere                                │
│ webapp     Manage web apps on PythonAnywhere                                │
│ deploy     Deploy a local project to PythonAnywhere                         │
│ account    Account management                                               │
│ register   Register a new PythonAnywhere account                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 账号配置

### 第一步：注册 PythonAnywhere 账号（如果没有）

如果你还没有 PythonAnywhere 账号，可以通过命令行注册：

```bash
$ pa register
Username (letters and numbers only): myusername
Email: myemail@example.com
Password: ********
Confirm password: ********
Account 'myusername' registered successfully!
Please check your email to verify your account.
Then run: pa init
```

> **提示**：如果你已有账号，跳过此步。

### 第二步：初始化配置

```bash
$ pa init
PythonAnywhere username: myusername
Password: ********
Host [www.pythonanywhere.com]:
Account 'myusername' configured successfully.
API token fetched and saved.
```

`pa init` 会自动完成以下操作：
1. 保存你的用户名和密码
2. 登录 PythonAnywhere
3. 从账号页面获取 API Token
4. 保存所有信息到 `~/.pa-cli/config.json`

---

## 第一个项目部署

### 准备项目文件

创建一个简单的 Flask 项目：

```
my-site/
├── app.py
└── requirements.txt
```

**app.py:**

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from PythonAnywhere!'

if __name__ == '__main__':
    app.run()
```

**requirements.txt:**

```
flask
```

### 一键部署

```bash
$ pa deploy ./my-site
Uploading ./my-site to /home/myusername/my-site...
Uploaded 2 files.
Setting up environment...
Creating webapp myusername.pythonanywhere.com...
Reloading webapp...
Deployed successfully! Visit: https://myusername.pythonanywhere.com
```

部署完成后，访问 `https://myusername.pythonanywhere.com` 即可看到你的网站。

---

## 常用命令速查

### 账号管理

```bash
pa init                    # 初始化配置（自动获取 token）
pa register                # 注册新账号
pa account login           # 存储密码
pa account token           # 获取 API token
pa account extend          # 延长免费账号有效期
```

### 部署

```bash
pa deploy ./my-site                    # 部署到默认域名
pa deploy ./my-site --domain custom    # 部署到自定义域名
```

### 文件管理

```bash
pa files upload ./index.html /home/user/site/index.html      # 上传单个文件
pa files upload ./static /home/user/site/static -r            # 上传目录
```

### Console 管理

```bash
pa console list                      # 列出所有 console
pa console create                    # 创建新 console
pa console send 12345 "ls -la"       # 发送命令并获取输出
pa console activate 12345            # 激活 console
pa console get-or-create             # 智能获取或创建
pa console kill 12345                # 销毁 console
```

### Webapp 管理

```bash
pa webapp create mysite.pythonanywhere.com                    # 创建 webapp
pa webapp config mysite --source-dir /home/user/mysite        # 配置源码目录
pa webapp static mysite --url /static/ --path static          # 添加静态映射
pa webapp reload mysite.pythonanywhere.com                    # 重载 webapp
pa webapp hits mysite.pythonanywhere.com                      # 查看访问统计
```

---

## 命令依赖关系

某些命令需要先完成前置操作：

| 命令 | 前置条件 | 说明 |
|------|---------|------|
| `pa deploy` | `pa init` | 需要 API token |
| `pa files upload` | `pa init` | 需要 API token |
| `pa console create/list/send/kill` | `pa init` | 需要 API token |
| `pa webapp create/config/static/reload` | `pa init` | 需要 API token |
| `pa account token/extend` | `pa init` | 需要密码（自动从配置读取） |
| `pa console activate/get-or-create` | `pa init` | 需要密码（自动从配置读取） |
| `pa webapp hits/reload-crawler` | `pa init` | 需要密码（自动从配置读取） |

**简单来说**：运行 `pa init` 后，所有命令都可以使用。

---

## 常见问题

### 1. API Token 错误

**错误信息**：
```
Exception: API error 401: Invalid token.
```

**解决方案**：
```bash
pa account token    # 重新获取 token
```

### 2. 密码未配置

**错误信息**：
```
Password not found in config. Run 'pa account login' to store it.
```

**解决方案**：
```bash
pa account login    # 存储密码
```

### 3. Console 未启动

**错误信息**：
```
Exception: API error 412: Console not yet started.
```

**解决方案**：
```bash
pa console list         # 获取 console ID
pa console activate 12345   # 激活 console
```

### 4. 免费账号限制

免费账号限制：
- 最多 1 个 web app
- 最多 2 个 console
- 每月 100 秒 CPU 时间

### 5. 网络连接问题

**错误信息**：
```
ConnectionError: ('Connection aborted.', RemoteDisconnected(...))
```

**解决方案**：
- 检查网络连接
- 确认能访问 pythonanywhere.com
- 稍后重试

---

## 下一步

- [命令参考](commands/) - 查看所有命令的详细文档
- [架构设计](architecture.md) - 了解项目内部结构
- [GitHub 仓库](https://github.com/Duroxi/pythonanywhere-cli) - 查看源码
