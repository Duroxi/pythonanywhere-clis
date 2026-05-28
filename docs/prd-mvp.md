# PRD: pythonanywhere-cli MVP

## 1. 项目目标

实现本地 Web 项目的全自动化部署到 PythonAnywhere，返回一个可访问的网站地址。

MVP 聚焦最小闭环：**有账号 → 上传代码 → 创建网站 → 可访问**。

## 2. MVP 功能范围

### 2.1 包含

| 功能 | CLI 命令 | 说明 |
|------|----------|------|
| 账号配置 | `pa init` | 交互式输入用户名和 API Token，保存到 `~/.pa-cli/config.json` |
| 上传文件 | `pa files upload <本地路径> <远程路径> [-r]` | 单文件上传，`-r` 递归上传目录 |
| 创建 Console | `pa console create [--executable <路径>]` | 默认创建 Bash Console，可通过 `--executable` 指定 |
| 发送命令 | `pa console send <id> <命令>` | 向 Console 发送输入 |
| 获取输出 | `pa console output <id>` | 读取 Console 输出 |
| 销毁 Console | `pa console kill <id>` | 终止 Console |
| 创建 Webapp | `pa webapp create <域名> --python <版本>` | 创建 Web 应用 |
| 配置 Webapp | `pa webapp config <域名> --source-dir <路径> [--virtualenv <路径>]` | 设置源码目录（必需）和虚拟环境路径（可选） |
| 添加静态映射 | `pa webapp static <域名> --url --path` | 添加 URL 到目录的映射 |
| 重载 Webapp | `pa webapp reload <域名>` | 重新加载应用 |
| 一键部署 | `pa deploy <本地目录> [--domain <域名>]` | 自动完成上传+环境配置+Webapp创建+重载。域名默认 `{username}.pythonanywhere.com` |

### 2.2 不包含（后续迭代）

- 文件下载、目录浏览、删除
- 日志查看/删除
- Webapp 启用/禁用、SSL、删除
- Always-On 任务、定时任务
- 资源监控、系统配置
- 自动注册、自动延期
- 批量操作、多账号管理
- Agent Skill 集成

## 3. 架构设计

### 3.1 分层架构

```
┌──────────────────────────────────────────────┐
│  CLI 命令层                                    │
│  用户/AI Agent 入口，负责参数解析和输出格式化     │
│  pa_cli/cli/                                   │
├──────────────────────────────────────────────┤
│  编排层                                        │
│  组合多个原子操作完成复杂业务流程                 │
│  pa_cli/workflows/                             │
├──────────────────────────────────────────────┤
│  API 封装层                                    │
│  一对一映射 PA REST API 端点，每个方法 = 一次调用 │
│  pa_cli/api/                                   │
├──────────────────────────────────────────────┤
│  HTTP 客户端基类                               │
│  Token 认证、限速、重试、错误处理                │
│  pa_cli/api/client.py                          │
├──────────────────────────────────────────────┤
│  配置层                                        │
│  账号信息读写                                   │
│  pa_cli/config.py                              │
└──────────────────────────────────────────────┘
```

### 3.2 目录结构（含扩展点）

```
pythonanywhere-cli/
├── pa_cli/
│   ├── __init__.py
│   ├── config.py                 # 配置管理
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py             # HTTP 客户端基类（所有 API 模块的父类）
│   │   ├── files.py              # 文件 API    [MVP: upload]  [扩展: download, list, delete, share]
│   │   ├── consoles.py           # Console API [MVP: 全部]
│   │   ├── webapps.py            # Webapp API  [MVP: create, update, static, reload]
│   │   ├── tasks.py              # 定时任务 API [扩展]
│   │   ├── always_on.py          # Always-On API [扩展]
│   │   └── system.py             # 系统 API    [扩展: CPU, Python版本, 镜像]
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py               # Typer 入口，注册所有子命令组
│   │   ├── init.py               # pa init
│   │   ├── files.py              # pa files
│   │   ├── consoles.py           # pa console
│   │   ├── webapps.py            # pa webapp
│   │   └── deploy.py             # pa deploy
│   └── workflows/
│       ├── __init__.py
│       └── deploy.py             # 一键部署编排逻辑
├── docs/
│   ├── feature-list.md
│   ├── tech-selection.md
│   └── prd-mvp.md
├── tests/
├── pyproject.toml
└── README.md
```

### 3.3 扩展点设计

**新增 API 端点**：在 `pa_cli/api/` 下新建模块，继承 `BaseClient`，实现方法即可。

**新增 CLI 命令组**：在 `pa_cli/cli/` 下新建模块，创建 Typer app，在 `main.py` 中 `app.add_typer()` 注册。

**新增编排流程**：在 `pa_cli/workflows/` 下新建模块，组合 API 层方法。

```python
# 扩展示例：新增 always_on 模块
# 1. pa_cli/api/always_on.py
class AlwaysOnClient(BaseClient):
    def list(self): ...
    def create(self, command, description): ...

# 2. pa_cli/cli/always_on.py
app = typer.Typer()
@app.command()
def ls(): ...

# 3. pa_cli/cli/main.py
from cli import always_on
app.add_typer(always_on.app, name="always-on", help="...")
```

## 4. 核心流程：一键部署（`pa deploy`）

输入：本地项目目录路径（必需）+ 目标域名（可选，默认 `{username}.pythonanywhere.com`）

```bash
pa deploy ./my-site                              # 使用默认域名
pa deploy ./my-site --domain mysite.pythonanywhere.com  # 指定域名
```

执行流程：

```
1. 读取配置，获取 token 和 username
2. 上传整个目录到 PA
   pa_cli.api.files.upload_directory(local_dir, remote_dir)
3. 创建 Bash Console
   pa_cli.api.consoles.create()
4. 通过 Console 执行环境配置
   - 创建虚拟环境（如目录中存在 requirements.txt）
   - pip install -r requirements.txt（如目录中存在该文件）
5. 创建 Webapp（如不存在）
   pa_cli.api.webapps.create(domain, python_version)
6. 配置 Webapp
   pa_cli.api.webapps.update(domain, source_dir, virtualenv_path)
7. 添加静态文件映射
   pa_cli.api.webapps.add_static_file(domain, url="/static/", path=".../static/")
   pa_cli.api.webapps.add_static_file(domain, url="/", path=".../media/")  # 如需要
8. 重载 Webapp
   pa_cli.api.webapps.reload(domain)
9. 输出结果
   "部署成功！访问地址: https://mysite.pythonanywhere.com"
```

## 5. 配置格式

`~/.pa-cli/config.json`：

```json
{
  "accounts": [
    {
      "username": "myusername",
      "token": "abc123...",
      "host": "www.pythonanywhere.com"
    }
  ],
  "default_account": "myusername"
}
```

MVP 阶段只支持单账号，但格式预留 `accounts` 数组，方便后续扩展多账号。

## 6. 依赖

```
typer
requests
```

Python >= 3.10

## 7. 验收标准

1. `pa init` 能保存账号配置
2. `pa files upload` 能上传文件到 PA
3. `pa console create/send/output/kill` 能完整操作 Console
4. `pa webapp create/config/static/reload` 能创建和管理 Webapp
5. `pa deploy ./test-site` 能一键部署并返回可访问的 URL
6. 所有 API 调用带有 Token 认证
7. 错误情况有清晰的提示信息
