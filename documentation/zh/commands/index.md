# 命令

## 命令组

| 命令组 | 用途 |
|--------|------|
| [Account](account.md) | 账户管理 |
| [Console](console.md) | 控制台操作 |
| [Deploy](deploy.md) | 一键部署 |
| [Files](files.md) | 文件管理 |
| [Status](status.md) | 系统状态 |
| [Tasks](tasks.md) | 定时任务 |
| [Always-on](always-on.md) | 常驻任务 |
| [Webapp](webapp.md) | Web 应用管理 |

## 快速参考

### 账户管理
- `pa init` - 配置账户
- `pa register` - 注册新账户
- `pa account list` - 列出账户
- `pa account switch` - 切换账户
- `pa account token` - 获取 API token

### 部署
- `pa deploy <dir>` - 一键部署
- `pa deploy <dir> --dry-run` - 预览部署

### 文件管理
- `pa files ls` - 列出文件
- `pa files upload` - 上传文件
- `pa files download` - 下载文件

### 控制台管理
- `pa console list` - 列出控制台
- `pa console create` - 创建控制台
- `pa console send <id> <cmd>` - 发送命令

### Web 应用管理
- `pa webapp create` - 创建 Web 应用
- `pa webapp config` - 配置 Web 应用
- `pa webapp reload` - 重载 Web 应用
