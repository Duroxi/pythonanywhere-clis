# Files 命令

文件管理相关的命令，用于将本地文件上传到 PythonAnywhere 服务器。

---

## pa files upload

上传文件或目录到 PythonAnywhere。

### 语法

```bash
pa files upload <local_path> <remote_path> [-r | --recursive]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `local_path` | 是 | 本地文件或目录路径 |
| `remote_path` | 是 | PythonAnywhere 上的远程路径 |

### 选项

| 选项 | 说明 |
|------|------|
| `-r`, `--recursive` | 递归上传目录及其所有内容 |

### 说明

- 使用 Token 认证，通过 REST API 上传
- 远程路径以 `/home/{username}/` 为根目录
- 单文件上传返回 HTTP 状态码
- 目录上传时自动遍历所有子文件，路径分隔符统一转换为 `/`

### 示例

**上传单个文件：**

```bash
$ pa files upload ./app.py /home/myuser/myproject/app.py
Uploaded ./app.py -> /home/myuser/myproject/app.py (HTTP 200)
```

**上传整个目录：**

```bash
$ pa files upload ./myproject /home/myuser/myproject -r
Uploaded 15 files to /home/myuser/myproject
```

**上传到用户根目录：**

```bash
$ pa files upload ./config.json /home/myuser/config.json
Uploaded ./config.json -> /home/myuser/config.json (HTTP 200)
```

### 错误场景

**本地路径不存在：**

```bash
$ pa files upload ./nonexistent /home/myuser/test
Error: ./nonexistent does not exist
```

**上传目录时未指定 `-r`：**

```bash
$ pa files upload ./myproject /home/myuser/myproject
Error: Use -r/--recursive to upload directories
```

**API 认证失败（Token 无效）：**

```bash
Error: API error 401: Invalid token.
```

**远程路径无写入权限：**

```bash
Error: API error 403: You do not have permission to write to this path.
```

**上传失败：**

```bash
Error: Upload failed: 500 Internal Server Error
```

### 前置条件

- 需先运行 `pa init` 完成账户配置（包含有效的 API Token）

### 注意事项

- 上传操作会覆盖远程同名文件
- 目录上传时保持本地目录结构，`local_path` 的最后一级目录名会作为远程目录名
- 大量文件上传时显示进度条

---

## pa files ls

列出远程目录内容。

### 语法

```bash
pa files ls [<remote_path>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 否 | 远程路径（默认：用户根目录） |

### 示例

**列出根目录：**

```bash
$ pa files ls
  .bashrc
  .profile
  myproject/
  README.txt
```

**列出子目录：**

```bash
$ pa files ls myproject
  app.py
  requirements.txt
  static/
  templates/
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa files download

下载文件或目录到本地。

### 语法

```bash
pa files download <remote_path> [<local_path>] [-r | --recursive]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 是 | 远程文件或目录路径 |
| `local_path` | 否 | 本地目标路径（默认：当前目录） |

### 选项

| 选项 | 说明 |
|------|------|
| `-r`, `--recursive` | 递归下载目录 |

### 示例

**下载单个文件：**

```bash
$ pa files download /home/myuser/app.py ./app.py
Downloaded /home/myuser/app.py -> app.py
```

**下载目录：**

```bash
$ pa files download /home/myuser/myproject ./myproject -r
Downloaded 15 files to myproject
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa files rm

删除远程文件或目录。

### 语法

```bash
pa files rm <remote_path> [-r | --recursive] [-f | --force]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 是 | 远程文件或目录路径 |

### 选项

| 选项 | 说明 |
|------|------|
| `-r`, `--recursive` | 递归删除目录 |
| `-f`, `--force` | 跳过确认提示 |

### 示例

**删除文件（带确认）：**

```bash
$ pa files rm /home/myuser/old.txt
Are you sure you want to delete '/home/myuser/old.txt'? [y/N]: y
Deleted /home/user/old.txt
```

**强制删除目录：**

```bash
$ pa files rm /home/myuser/old_project -r -f
Deleted /home/myuser/old_project (recursive)
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa files share

分享文件并获取分享链接。

### 语法

```bash
pa files share <remote_path>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 是 | 远程文件路径 |

### 示例

```bash
$ pa files share /home/myuser/data.csv
Share link: https://www.pythonanywhere.com/user/myuser/shares/abc123/
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa files unshare

取消文件分享。

### 语法

```bash
pa files unshare <remote_path>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 是 | 远程文件路径 |

### 示例

```bash
$ pa files unshare /home/myuser/data.csv
Stopped sharing: /home/myuser/data.csv
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa files share-status

查询文件的分享状态。

### 语法

```bash
pa files share-status <remote_path>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `remote_path` | 是 | 远程文件路径 |

### 示例

**文件已分享：**

```bash
$ pa files share-status /home/myuser/data.csv
File is shared: https://www.pythonanywhere.com/user/myuser/shares/abc123/
```

**文件未分享：**

```bash
$ pa files share-status /home/myuser/other.txt
File is not shared: /home/myuser/other.txt
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## 典型工作流

### 文件分享

```bash
# 1. 分享文件
$ pa files share /home/myuser/report.pdf
Share link: https://www.pythonanywhere.com/user/myuser/shares/abc123/

# 2. 查询分享状态
$ pa files share-status /home/myuser/report.pdf
File is shared: https://www.pythonanywhere.com/user/myuser/shares/abc123/

# 3. 取消分享
$ pa files unshare /home/myuser/report.pdf
Stopped sharing: /home/myuser/report.pdf
```

### 文件备份

```bash
# 1. 下载整个项目
$ pa files download /home/myuser/myproject ./backup/myproject -r
Downloaded 50 files to backup/myproject

# 2. 下载单个文件
$ pa files download /home/myuser/config.json ./config.json
Downloaded /home/myuser/config.json -> config.json
```
