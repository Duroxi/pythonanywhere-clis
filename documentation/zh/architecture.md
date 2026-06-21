# pythonanywhere-clis 架构文档

本文档描述 pythonanywhere-clis (`pa`) 项目的整体架构设计、模块职责和扩展方式。

---

## 1. 项目结构

```
pythonanywhere-cli/
├── pa_cli/                    # 主源码目录
│   ├── __init__.py
│   ├── config.py              # 配置管理（读写 ~/.pa-cli/config.json）
│   ├── exceptions.py          # 异常层级定义
│   │
│   ├── api/                   # REST API 客户端模块（Token 认证）
│   │   ├── __init__.py
│   │   ├── client.py          # BaseClient 基类，封装 HTTP 请求
│   │   ├── consoles.py        # ConsolesClient - 控制台 API
│   │   ├── files.py           # FilesClient - 文件 API
│   │   ├── webapps.py         # WebappsClient - Web 应用 API
│   │   ├── system.py          # SystemClient - 系统 API（CPU）
│   │   ├── tasks.py           # TasksClient - 定时任务 API
│   │   └── always_on.py       # AlwaysOnClient - Always-on 任务 API
│   │
│   ├── cli/                   # CLI 命令层（Typer 框架）
│   │   ├── __init__.py
│   │   ├── main.py            # 入口：注册所有子命令
│   │   ├── utils.py           # 公共工具函数（get_client, fix_remote_path）
│   │   ├── init_cmd.py        # pa init - 初始化配置
│   │   ├── register_cmd.py    # pa register - 注册新账户
│   │   ├── account_cmd.py     # pa account - 账户管理
│   │   ├── files_cmd.py       # pa files - 文件操作
│   │   ├── consoles_cmd.py    # pa console - 控制台操作
│   │   ├── webapps_cmd.py     # pa webapp - Web 应用操作
│   │   ├── deploy_cmd.py      # pa deploy - 部署项目
│   │   ├── status_cmd.py      # pa status - 系统状态查询
│   │   ├── tasks_cmd.py       # pa tasks - 定时任务管理
│   │   └── always_on_cmd.py   # pa always-on - Always-on 任务管理
│   │
│   ├── crawler/               # 浏览器模拟模块（Session 认证）
│   │   ├── __init__.py
│   │   ├── account_crawler.py # AccountCrawler - 账户操作爬虫
│   │   └── console_crawler.py # ConsoleCrawler - 控制台操作爬虫
│   │
│   └── workflows/             # 工作流编排
│       ├── __init__.py
│       └── deploy.py          # 部署工作流（上传 → 环境 → 配置 → 重载）
│
├── tests/                     # 测试目录
├── docs/                      # 开发文档
├── documentation/             # 用户文档（本文档所在位置）
├── pyproject.toml             # 项目元数据和依赖
├── README.md                  # 项目说明
├── CHANGELOG.md               # 版本变更记录
└── LICENSE                    # MIT 许可证
```

### 模块职责

| 模块 | 职责 | 依赖 |
|------|------|------|
| `config.py` | 管理配置文件的读写，支持多账户 | 标准库 |
| `api/` | 封装 PythonAnywhere REST API，提供类型安全的客户端 | requests |
| `cli/` | 解析命令行参数，调用 api 或 crawler 模块 | typer, api, crawler |
| `crawler/` | 模拟浏览器操作，处理无 API 的功能 | requests, bs4, websocket |
| `workflows/` | 编排多步骤操作（如完整部署流程） | api |

---

## 2. 认证模型

PythonAnywhere 提供两种访问方式，本项目同时支持。

### 2.1 Token 认证（API 模块）

```
┌─────────┐    Token: xxxxx    ┌──────────────────┐
│  pa CLI  │ ─────────────────→│  PA REST API     │
│          │ ←─────────────────│  (api/v0/...)    │
└─────────┘    JSON Response   └──────────────────┘
```

**特点：**
- 使用 API Token 进行认证，通过 `Authorization: Token xxxxx` 请求头传递
- 适用于标准 REST API 端点
- 速率限制：40 请求/分钟（标准端点），120 请求/分钟（`send_input` 端点）
- Token 在 `pa init` 时配置，存储在 `~/.pa-cli/config.json`

**实现位置：** `pa_cli/api/client.py` 的 `BaseClient`

```python
# 认证方式
self.session.headers.update({"Authorization": f"Token {token}"})
```

### 2.2 Session 认证（Crawler 模块）

```
┌─────────┐   POST /login/    ┌──────────────────┐
│  pa CLI  │ ────────────────→│  PA Web 界面     │
│          │ ←────────────────│  (HTML 页面)     │
│          │   Session Cookie  │                  │
│          │ ────────────────→│  操作页面...      │
└─────────┘                   └──────────────────┘
```

**特点：**
- 使用用户名 + 密码登录，获取 Session Cookie
- 模拟浏览器行为（解析 HTML、处理 CSRF Token）
- 无官方速率限制（但应自行控制请求频率）
- 适用于无 REST API 的功能（如注册账户、延长过期时间）

**实现位置：** `pa_cli/crawler/` 目录

```python
# 登录流程
data = {
    "csrfmiddlewaretoken": csrf_input["value"],
    "auth-username": username,
    "auth-password": password,
    "login_view-current_step": "auth",
}
login_resp = self.session.post(login_url, data=data)
```

### 2.3 认证方式对比

| 特性 | Token 认证 | Session 认证 |
|------|-----------|--------------|
| 凭证 | API Token | 用户名 + 密码 |
| 认证头 | `Authorization: Token xxx` | Session Cookie |
| 速率限制 | 40 req/min | 无官方限制 |
| 适用场景 | 标准 API 操作 | 浏览器专属功能 |
| 实现复杂度 | 低 | 高（需处理 CSRF） |
| 稳定性 | 高（官方 API） | 中（依赖页面结构） |

---

## 3. 设计决策：为什么需要 Crawler 模块

### 3.1 问题背景

PythonAnywhere 的 REST API 并未覆盖所有功能。以下操作只能通过 Web 界面完成：

1. **注册新账户** — 无 API 端点
2. **延长账户过期时间** — 无 API 端点
3. **获取 API Token** — 需要登录后从页面提取
4. **WebSocket 控制台激活** — 需要从页面解析连接参数

### 3.2 解决方案

Crawler 模块通过模拟浏览器行为来补充 API 的不足：

```
用户请求
    │
    ├─ 标准操作（上传文件、创建控制台等）
    │   └─→ 使用 API 模块（Token 认证）
    │
    └─ 浏览器专属操作（注册、延长过期等）
        └─→ 使用 Crawler 模块（Session 认证）
```

### 3.3 设计原则

1. **最小化使用** — 优先使用 API，仅在无 API 可用时使用 Crawler
2. **隔离关注点** — Crawler 代码独立于 API 代码，互不依赖
3. **防御性编程** — 处理 CSRF Token、页面结构变化等潜在问题
4. **可替换性** — 如果 PythonAnywhere 未来提供对应 API，可平滑迁移

---

## 4. API vs Crawler：使用场景

### 4.1 使用 API 模块的场景

| 操作 | 客户端类 | 方法 |
|------|---------|------|
| 上传文件 | `FilesClient` | `upload()` |
| 列出控制台 | `ConsolesClient` | `list()` |
| 创建控制台 | `ConsolesClient` | `create()` |
| 发送命令 | `ConsolesClient` | `send_input()` |
| 获取输出 | `ConsolesClient` | `get_output()` |
| 创建 Web 应用 | `WebappsClient` | `create()` |
| 更新配置 | `WebappsClient` | `update()` |
| 重载应用 | `WebappsClient` | `reload()` |

### 4.2 使用 Crawler 模块的场景

| 操作 | 爬虫类 | 方法 |
|------|--------|------|
| 注册新账户 | `AccountCrawler` | `register()` |
| 登录获取 Session | `AccountCrawler` | `login()` |
| 提取 API Token | `AccountCrawler` | `get_token()` |
| 延长账户过期 | `AccountCrawler` | `extend_expiry()` |
| 重载 Web 应用（备选） | `AccountCrawler` | `reload_webapp()` |
| 获取访问统计 | `AccountCrawler` | `get_hits()` |
| 激活控制台（WebSocket） | `ConsoleCrawler` | `activate()` |

### 4.3 决策流程图

```
需要执行操作
    │
    ▼
该操作有 REST API 吗？
    │
    ├─ 是 → 使用 API 模块（api/）
    │       优点：稳定、快速、有速率限制保护
    │
    └─ 否 → 使用 Crawler 模块（crawler/）
            注意：依赖页面结构，可能需要维护
```

---

## 5. 配置管理

### 5.1 配置文件位置

```
~/.pa-cli/config.json
```

### 5.2 配置文件格式

```json
{
  "default_account": "myusername",
  "accounts": [
    {
      "username": "myusername",
      "token": "abc123def456...",
      "host": "www.pythonanywhere.com",
      "password": "optional_for_crawler"
    },
    {
      "username": "work_account",
      "token": "xyz789...",
      "host": "www.pythonanywhere.com"
    }
  ]
}
```

### 5.3 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `default_account` | 是 | 默认使用的账户用户名 |
| `accounts` | 是 | 账户列表 |
| `accounts[].username` | 是 | PythonAnywhere 用户名 |
| `accounts[].token` | 是 | API Token（通过 `pa init` 获取） |
| `accounts[].host` | 否 | API 主机，默认 `www.pythonanywhere.com` |
| `accounts[].password` | 否 | 密码（仅 Crawler 功能需要） |

### 5.4 配置操作

```bash
# 初始化配置（交互式）
pa init
```

### 5.5 实现细节

配置管理由 `pa_cli/config.py` 的 `Config` 类实现：

- `Config.save()` — 保存或更新配置，支持部分更新
- `Config.load()` — 加载配置，支持按用户名查找

---

## 6. 扩展点

### 6.1 添加新的 API 客户端

当 PythonAnywhere 发布新 API 端点时：

**步骤 1：** 在 `pa_cli/api/` 创建新客户端文件

```python
# pa_cli/api/databases.py
from pa_cli.api.client import BaseClient


class DatabasesClient(BaseClient):
    def list(self, username: str) -> list:
        response = self._request(
            "GET",
            "/api/v0/user/{username}/databases/",
            username=username,
        )
        return response.json()

    def create(self, username: str, name: str) -> dict:
        response = self._request(
            "POST",
            "/api/v0/user/{username}/databases/",
            username=username,
            json={"name": name},
        )
        return response.json()
```

**步骤 2：** 在 `pa_cli/cli/` 创建对应命令

```python
# pa_cli/cli/databases_cmd.py
import typer
from pa_cli.config import Config
from pa_cli.api.databases import DatabasesClient

app = typer.Typer()


@app.command("ls")
def list_databases():
    config = Config.load()
    client = DatabasesClient(token=config["token"], host=config["host"])
    databases = client.list(config["username"])
    for db in databases:
        print(db["name"])
```

**步骤 3：** 在 `pa_cli/cli/main.py` 注册新命令

```python
from pa_cli.cli.databases_cmd import app as databases_app
app.add_typer(databases_app, name="database", help="Manage databases")
```

### 6.2 添加新的 Crawler 功能

当需要操作无 API 的 Web 页面时：

```python
# pa_cli/crawler/new_crawler.py
import requests
from bs4 import BeautifulSoup


class NewCrawler:
    def __init__(self, host: str = "www.pythonanywhere.com"):
        self.base_url = f"https://{host}"
        self.session = requests.Session()

    def login(self, username: str, password: str) -> bool:
        # 标准登录流程
        login_url = f"{self.base_url}/login/"
        resp = self.session.get(login_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        csrf = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

        data = {
            "csrfmiddlewaretoken": csrf,
            "auth-username": username,
            "auth-password": password,
            "login_view-current_step": "auth",
        }
        login_resp = self.session.post(login_url, data=data)
        return "/login/" not in login_resp.url

    def new_operation(self):
        # 实现新操作
        pass
```

### 6.3 添加新的工作流

编排多步骤操作时：

```python
# pa_cli/workflows/setup.py
from pa_cli.api.files import FilesClient
from pa_cli.api.consoles import ConsolesClient


def setup_project(username, token, host, project_name):
    """完整的项目初始化工作流"""
    files = FilesClient(token=token, host=host)
    consoles = ConsolesClient(token=token, host=host)

    # 步骤 1：创建目录结构
    # 步骤 2：上传模板文件
    # 步骤 3：安装依赖
    # 步骤 4：配置环境
    pass
```

### 6.4 扩展检查清单

添加新功能时，确认以下事项：

- [ ] 确认是否有 REST API 可用（优先使用 API）
- [ ] 如无 API，评估 Crawler 实现的稳定性
- [ ] 遵循现有命名规范（全英文、语义明确）
- [ ] 客户端类继承 `BaseClient`（API 模块）
- [ ] 命令使用 Typer 框架（CLI 模块）
- [ ] 在 `main.py` 注册新命令
- [ ] 添加相应的测试用例

---

## 7. 数据流示例

### 7.1 部署流程

```
用户执行: pa deploy ./myproject myusername.pythonanywhere.com

    ┌─────────────────────────────────────────────────────────────┐
    │                      deploy workflow                        │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  1. FilesClient.upload() × N                                │
    │     上传本地文件到远程目录                                     │
    │                          ↓                                  │
    │  2. ConsolesClient.create()                                  │
    │     创建临时控制台                                            │
    │                          ↓                                  │
    │  3. ConsolesClient.send_input() × N                         │
     │     执行 mkvirtualenv、pip install 等命令                    │
    │                          ↓                                  │
    │  4. WebappsClient.create()                                   │
    │     创建/更新 Web 应用配置                                    │
    │                          ↓                                  │
    │  5. WebappsClient.reload()                                   │
    │     重载 Web 应用                                             │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

### 7.2 账户注册流程

```
用户执行: pa register

    ┌─────────────────────────────────────────────────────────────┐
    │                   AccountCrawler.register()                 │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  1. GET /registration/register/beginner/                     │
    │     获取注册页面和 CSRF Token                                 │
    │                          ↓                                  │
    │  2. POST /registration/register/beginner/                    │
    │     提交注册表单（用户名、邮箱、密码）                          │
    │                          ↓                                  │
    │  3. 检查是否跳转到 /registration/register/complete/           │
    │     确认注册成功                                              │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## 8. 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| CLI 框架 | Typer | 命令行参数解析、帮助生成 |
| HTTP 客户端 | requests | API 调用和页面请求 |
| HTML 解析 | BeautifulSoup4 | 解析 Web 页面、提取 CSRF Token |
| WebSocket | websocket-client | 控制台 WebSocket 连接 |
| 配置存储 | JSON | 本地配置文件 |
| 最低 Python | 3.10+ | 使用 `str | None` 类型语法 |

---

## 9. 注意事项

### 9.1 速率限制

- API 模块：40 请求/分钟（标准端点）
- API 模块：120 请求/分钟（`send_input` 端点）
- Crawler 模块：无官方限制，但建议控制频率

### 9.2 Crawler 稳定性

Crawler 依赖 Web 页面结构，如果 PythonAnywhere 更新页面，可能需要调整选择器。关键点：

- CSRF Token 提取方式
- 表单字段名称
- 页面跳转 URL 模式

### 9.3 安全考虑

- API Token 和密码存储在本地 JSON 文件中
- 建议设置适当的文件权限：`chmod 600 ~/.pa-cli/config.json`
- 不要将配置文件提交到版本控制
