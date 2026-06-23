# Account 命令

账户管理相关的命令，包括初始化配置、注册新账户、存储密码、获取 API Token 以及延长账户有效期。

---

## pa init

配置 PythonAnywhere 账户。支持交互式和命令行两种模式。

### 语法

```bash
pa init [-u <username>] [-p <password>] [-h <host>]
```

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-u`, `--username` | 无（交互式提示） | PythonAnywhere 用户名 |
| `-p`, `--password` | 无（交互式提示） | 账户密码 |
| `-h`, `--host` | `www.pythonanywhere.com` | PythonAnywhere 主机地址 |

### 说明

配置完成后，自动通过爬虫登录并获取 API Token，保存到 `~/.pa-cli/config.json`。

如果 Token 不存在，会自动创建一个新 Token。

### 示例

**交互式模式：**

```bash
$ pa init
PythonAnywhere username: myuser
Password: ********
Account 'myuser' configured successfully.
API token: abc123def456
```

**命令行模式：**

```bash
$ pa init -u myuser -p mypassword
Account 'myuser' configured successfully.
API token: abc123def456
```

**指定主机：**

```bash
$ pa init -u myuser -p mypassword -h eu.pythonanywhere.com
Account 'myuser' configured successfully.
API token: abc123def456
```

### 错误场景

**用户名或密码错误：**

```bash
$ pa init -u wronguser -p wrongpass
Auth error: Login failed. Please check your username and password.
Don't have an account? Register with: pa register
```

**网络异常：**

```bash
Network error: Failed to fetch login page: Connection refused
```

### 前置条件

- 无需预先配置，首次使用 CLI 时运行即可
- 需要有效的 PythonAnywhere 账户（没有账户请先运行 `pa register`）

---

## pa register

注册新的 PythonAnywhere 账户。

### 语法

```bash
pa register
```

### 说明

通过爬虫模拟浏览器完成注册流程。依次提示输入：
1. 用户名（仅限字母和数字）
2. 邮箱地址
3. 密码（隐藏输入）
4. 确认密码（隐藏输入）

### 示例

```bash
$ pa register
Username (letters and numbers only): newuser
Email: user@example.com
Password: ********
Confirm password: ********
Account 'newuser' registered successfully!
Please check your email to verify your account.
Then run: pa init
```

### 错误场景

**两次密码不一致：**

```bash
$ pa register
Username (letters and numbers only): newuser
Email: user@example.com
Password: ********
Confirm password: ********
Passwords do not match.
```

**注册失败（用户名已存在等）：**

```bash
Registration failed. Please check your inputs.
```

**网络异常：**

```bash
Error: Failed to fetch registration page: Connection refused
```

### 后续步骤

注册成功后：
1. 检查邮箱完成验证
2. 运行 `pa init` 配置账户

---

## pa account list

列出所有已配置的账户。

### 语法

```bash
pa account list
```

### 示例

```bash
$ pa account list
* myuser    www.pythonanywhere.com    token: abc12345...
  workuser  www.pythonanywhere.com    token: def67890...
```

**无账户时：**

```bash
$ pa account list
No accounts configured. Run 'pa init' to add one.
```

### 输出说明

- `*` 标记表示当前默认账户
- Token 只显示前 8 位，其余用 `...` 替代

### 前置条件

- 无

---

## pa account switch

切换默认账户。

### 语法

```bash
pa account switch <username>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `username` | 是 | 要切换到的用户名 |

### 示例

```bash
$ pa account switch workuser
Switched to account 'workuser'.
```

### 错误场景

**账户不存在：**

```bash
$ pa account switch nonexistent
Error: Account 'nonexistent' not found in config.
```

### 前置条件

- 需先运行 `pa init` 添加账户

---

## pa account remove

删除一个已配置的账户。

### 语法

```bash
pa account remove <username>
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `username` | 是 | 要删除的用户名 |

### 示例

```bash
$ pa account remove workuser
Removed account 'workuser'.
Switched to account 'myuser'.
```

**删除当前默认账户：**

```bash
$ pa account remove myuser
Removed account 'myuser'.
Switched to account 'workuser'.
```

### 错误场景

**账户不存在：**

```bash
$ pa account remove nonexistent
Error: Account 'nonexistent' not found in config.
```

### 前置条件

- 需先运行 `pa init` 添加账户

---

## pa account login

存储当前账户的密码到本地配置文件。

### 语法

```bash
pa account login
```

### 说明

部分命令（如 `pa account token`、`pa account extend`、`pa console activate`、`pa console get-or-create`）需要通过爬虫模拟登录，因此需要在本地保存密码。此命令仅将密码保存到 `~/.pa-cli/config.json`，不会执行登录操作。

密码以明文形式存储在配置文件中。

### 示例

```bash
$ pa account login
Password: ********
Password saved successfully.
```

### 前置条件

- 需先运行 `pa init` 完成账户配置

---

## pa account token

通过爬虫登录并获取 API Token。

### 语法

```bash
pa account token [-r | --revoke]
```

### 选项

| 选项 | 说明 |
|------|------|
| `-r`, `--revoke` | 撤销当前 Token 并创建新的 |

### 说明

使用配置文件中的用户名和密码，模拟浏览器登录 PythonAnywhere，从账户页面抓取 API Token 并保存到配置文件。

如果 Token 不存在，会自动创建一个新 Token。

### 示例

**获取现有 Token：**

```bash
$ pa account token
[account: myuser]
API token: abc123def456ghi789
```

**撤销并创建新 Token：**

```bash
$ pa account token --revoke
[account: myuser]
Token revoked. New token: xyz789newtoken
```

### 错误场景

**密码未存储：**

```bash
$ pa account token
Error: Password not found in config. Run 'pa account login' to store it.
```

**登录失败：**

```bash
Login failed. Check your credentials.
```

**页面结构变更导致 Token 抓取失败：**

```bash
Error: API token not found on account page
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## pa account extend

延长免费账户的有效期。

### 语法

```bash
pa account extend
```

### 说明

免费账户有使用期限，到期后会被删除。此命令通过爬虫模拟浏览器操作，自动延长账户有效期。具体实现是在 Web Apps 页面找到 "extend" 表单并提交。

### 示例

```bash
$ pa account extend
Account expiry extended successfully.
```

### 错误场景

**密码未存储：**

```bash
$ pa account extend
Error: Password not found in config. Run 'pa account login' to store it.
```

**登录失败：**

```bash
Login failed. Check your credentials.
```

**延长失败（页面结构变更等）：**

```bash
Failed to extend account expiry.
```

**找不到延长表单：**

```bash
Error: Extend form not found on webapps page
```

### 前置条件

- 需先运行 `pa init` 完成账户配置
- 需先运行 `pa account login` 存储密码

---

## 认证方式说明

本 CLI 使用两种认证方式：

| 认证方式 | 说明 | 适用命令 |
|---------|------|---------|
| Token 认证 | 通过 API Token 调用 REST API | `pa files`、`pa console list/create/send/kill`、`pa webapp create/config/static/reload`、`pa deploy` |
| Session 认证 | 通过密码模拟浏览器登录 | `pa account token`、`pa account extend`、`pa console activate/get-or-create`、`pa webapp reload-crawler/hits` |

Token 认证方式标准 API 请求频率限制为 40 次/分钟，`send_input` 端点限制为 120 次/分钟。
