# 技术选型

## 核心选型

| 项目 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | Typer | 代码量最少，类型安全，自动帮助文档，与官方 helper_scripts 一致 |
| HTTP 客户端 | requests | PA API 是简单 REST 调用，不需要异步，requests 最简单可靠 |
| 配置存储 | JSON 文件（`~/.pa-cli/config.json`） | 零额外依赖，多账号用 JSON 数组管理，够用 |
| 自动注册 | requests + 必要的用户交互 | 验证码、邮箱验证码等环节由用户输入，不拒绝必要交互 |
| HTML 解析 | BeautifulSoup4 | 用于爬虫操作（登录、获取 CSRF token、解析页面） |
| WebSocket | websocket-client | 用于 Console 激活功能 |
| 进度条 | rich | 用于 deploy 命令的文件上传进度显示 |
| AI 集成 | Agent Skill（SKILL.md + 脚本） | 开放标准，Agent 无关，任何 AI Agent 都能调用 |

## 交付物

两个层面，分阶段交付：

1. **CLI 工具**（`pa` 命令）— 底层执行引擎，已完成
2. **Agent Skill**（SKILL.md + 脚本）— AI Agent 操作手册，待实现

## 项目结构

```
pythonanywhere-cli/
├── pa_cli/                  # 核心包
│   ├── __init__.py
│   ├── api/                 # API 封装层（对应 PA REST API 各端点）
│   │   ├── __init__.py
│   │   ├── client.py        # HTTP 客户端基类（token、限速、重试）
│   │   ├── files.py
│   │   ├── consoles.py
│   │   ├── webapps.py
│   │   ├── system.py
│   │   ├── tasks.py
│   │   └── always_on.py
│   ├── cli/                 # CLI 命令层（Typer）
│   │   ├── __init__.py
│   │   ├── main.py          # 入口 pa 命令
│   │   ├── utils.py         # 公共工具函数
│   │   ├── init_cmd.py
│   │   ├── register_cmd.py
│   │   ├── account_cmd.py
│   │   ├── files_cmd.py
│   │   ├── consoles_cmd.py
│   │   ├── webapps_cmd.py
│   │   ├── deploy_cmd.py
│   │   ├── status_cmd.py
│   │   ├── tasks_cmd.py
│   │   └── always_on_cmd.py
│   ├── crawler/             # 爬虫层（浏览器模拟）
│   │   ├── account_crawler.py
│   │   └── console_crawler.py
│   ├── workflows/           # 编排层
│   │   └── deploy.py
│   ├── config.py            # 配置管理
│   └── exceptions.py        # 异常层级
├── docs/
├── tests/
├── pyproject.toml
└── README.md
```
