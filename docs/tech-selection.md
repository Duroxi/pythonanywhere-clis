# 技术选型

## 核心选型

| 项目 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | Typer | 代码量最少，类型安全，自动帮助文档，与官方 helper_scripts 一致 |
| HTTP 客户端 | requests | PA API 是简单 REST 调用，不需要异步，requests 最简单可靠 |
| 配置存储 | JSON 文件（`~/.pa-cli/config.json`） | 零额外依赖，多账号用 JSON 数组管理，够用 |
| 自动注册 | requests + 必要的用户交互 | 验证码、邮箱验证码等环节由用户输入，不拒绝必要交互 |
| AI 集成 | Agent Skill（SKILL.md + 脚本） | 开放标准，Agent 无关，任何 AI Agent 都能调用 |

## 交付物

两个层面，分阶段交付：

1. **CLI 工具**（`pa` 命令）— 底层执行引擎，先做
2. **Agent Skill**（SKILL.md + 脚本）— AI Agent 操作手册，最后做

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
│   │   ├── tasks.py
│   │   ├── always_on.py
│   │   └── ...
│   ├── cli/                 # CLI 命令层（Typer）
│   │   ├── __init__.py
│   │   ├── main.py          # 入口 pa 命令
│   │   ├── files.py
│   │   ├── consoles.py
│   │   ├── webapps.py
│   │   ├── deploy.py        # 一键部署（组合多个原子操作）
│   │   └── ...
│   ├── config.py            # 配置管理
│   └── auth.py              # 注册、登录、Token 管理
├── skills/                  # Agent Skills（最后做）
├── docs/
├── tests/
├── pyproject.toml
└── README.md
```
