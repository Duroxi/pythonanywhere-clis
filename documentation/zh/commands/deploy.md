# Deploy 命令

一键部署命令，将本地项目自动部署到 PythonAnywhere。

---

## pa deploy

将本地项目目录一键部署到 PythonAnywhere。

### 语法

```bash
pa deploy <local_dir> [--domain <domain>] [--python <python_version>] [--dry-run]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `local_dir` | 是 | 本地项目目录路径 |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-d`, `--domain` | `{username}.pythonanywhere.com` | 目标域名 |
| `-p`, `--python` | `python310` | Python 版本 |
| `-n`, `--dry-run` | False | 预览部署，不实际执行 |

### 说明

一键部署命令自动执行以下步骤：

1. **上传文件** - 递归上传整个项目目录到 `/home/{username}/{dirname}`
2. **创建控制台** - 自动创建一个 Bash 控制台用于后续操作
3. **安装依赖** - 如果项目包含 `requirements.txt`，自动创建虚拟环境并安装依赖
4. **创建 Web 应用** - 创建或复用已有的 Web 应用
5. **配置应用** - 设置源码目录，如有 `static` 目录则自动添加静态文件映射
6. **重载应用** - 触发 Web 应用重载

### 示例

**部署到默认域名：**

```bash
$ pa deploy ./my-site
Uploading ./my-site to /home/myuser/my-site...
Uploaded 15 files.
Setting up environment...
Creating webapp myuser.pythonanywhere.com...
Reloading webapp...

Deployed! Visit: https://myuser.pythonanywhere.com
```

**部署到自定义域名：**

```bash
$ pa deploy ./my-site --domain mysite.pythonanywhere.com
Uploading ./my-site to /home/myuser/my-site...
Uploaded 8 files.
Setting up environment...
Creating webapp mysite.pythonanywhere.com...
Reloading webapp...

Deployed! Visit: https://mysite.pythonanywhere.com
```

**指定 Python 版本：**

```bash
$ pa deploy ./my-site --python python311
```

### 部署流程详解

#### 步骤 1: 文件上传

遍历 `local_dir` 下的所有文件，保持目录结构上传到远程 `/home/{username}/{dirname}/`。

#### 步骤 2: 环境配置

通过控制台执行命令：
- 切换到项目目录
- 如果存在 `requirements.txt`：
  - 使用 `mkvirtualenv` 创建虚拟环境
  - 使用 `pip install -r requirements.txt` 安装依赖

#### 步骤 3: Web 应用配置

- 创建 Web 应用（如已存在则跳过）
- 设置源码目录为上传路径
- 如果本地存在 `static` 目录，自动添加 `/static/` 的静态文件映射

#### 步骤 4: 重载

触发 Web 应用重载使其生效。

### 项目结构要求

部署命令对项目结构有以下假设：

```
my-site/
├── app.py              # 应用入口（可选）
├── requirements.txt    # Python 依赖（可选，自动安装）
├── static/             # 静态文件目录（可选，自动映射）
└── ...                 # 其他项目文件
```

### 错误场景

**本地目录不存在：**

```bash
Error: ./nonexistent is not a directory
```

**API 认证失败：**

```bash
Error: API error 401: Invalid token.
```

**控制台操作超时：**

部署过程中控制台命令的最大等待时间为 300 秒（5 分钟）。如果依赖安装等操作超时，部署可能不完整。

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 本地目录必须存在且包含项目文件

### 注意事项

- 部署会覆盖远程同名目录中的文件
- 虚拟环境名称使用项目目录名
- 如果 Web 应用已存在，不会重新创建，但会更新配置
- 部署完成后直接访问域名即可查看应用
- 整个部署过程中无进度条，只有阶段性的文本输出

---

## 与其他命令的关系

`pa deploy` 是一个便捷命令，等价于手动执行以下命令序列：

```bash
# 等价操作
pa files upload ./my-site /home/myuser/my-site -r
pa console create
pa console send <id> "cd /home/myuser/my-site"
pa console send <id> "mkvirtualenv my-site --python=/usr/bin/python310"
pa console send <id> "workon my-site && pip install -r requirements.txt"
pa webapp create myuser.pythonanywhere.com
pa webapp config myuser.pythonanywhere.com -s /home/myuser/my-site
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/my-site/static
pa webapp reload myuser.pythonanywhere.com
```

如果需要更精细的控制，可以使用上述单独命令逐步执行。
