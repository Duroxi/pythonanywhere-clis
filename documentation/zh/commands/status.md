# Status 命令

系统状态查询相关的命令，用于查看 CPU 和磁盘使用情况。

---

## pa status cpu

查看 CPU 使用情况。

### 语法

```bash
pa status cpu
```

### 说明

通过 REST API 查询每日 CPU 使用量、限额和重置时间。

### 示例

```bash
$ pa status cpu
[account: myuser]
CPU Usage:
  Used: 45.2 seconds
  Limit: 100 seconds
  Reset: 2026-06-21T07:00:00
```

### 输出字段

| 字段 | 说明 |
|------|------|
| Used | 今日已使用的 CPU 时间（秒） |
| Limit | 每日 CPU 时间限额（秒） |
| Reset | 限额重置时间 |

### 错误场景

**API 认证失败：**

```bash
Auth error: Invalid token.
```

**解决方案**：运行 `pa account token` 重新获取 token。

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa status disk

查看磁盘使用情况。

### 语法

```bash
pa status disk
```

### 说明

通过爬虫查询磁盘使用量和限额。此命令需要存储密码（Session 认证）。

### 示例

```bash
$ pa status disk
[account: myuser]
Disk Usage:
  Used: 20.1 MB
  Total: 512.0 MB
  Usage: 4%
```

### 输出字段

| 字段 | 说明 |
|------|------|
| Used | 已使用的磁盘空间 |
| Total | 磁盘空间总额 |
| Usage | 使用百分比 |

### 错误场景

**密码未存储：**

```bash
Auth error: Password not found in config.
```

**解决方案**：运行 `pa account login` 存储密码。

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## 命令对比

| 命令 | 认证方式 | 数据来源 | 说明 |
|------|---------|---------|------|
| `pa status cpu` | Token | REST API | 实时查询 |
| `pa status disk` | 密码 | 爬虫 | 需要登录 |
| `pa status system-image` | Token | REST API | 获取/设置系统镜像 |

---

## pa status system-image

获取或设置系统镜像。

### 语法

```bash
pa status system-image [<image>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `image` | 否 | 要设置的系统镜像 |

### 说明

如果未指定镜像，显示当前系统镜像和可用镜像。如果指定了镜像，设置系统镜像。

### 示例

**获取当前系统镜像：**

```bash
$ pa status system-image
Current system image: ubuntu-20.04
Available images: ubuntu-20.04, ubuntu-22.04
```

**设置系统镜像：**

```bash
$ pa status system-image ubuntu-22.04
System image set to ubuntu-22.04
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

