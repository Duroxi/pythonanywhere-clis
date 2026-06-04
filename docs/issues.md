# PA-CLI 问题清单 & 待修复列表

> 基于 2026-06-04 代码审查，按优先级排列
> 状态：🔲 待修 | 🟡 进行中 | ✅ 已修

---

## 🔴 P0 - 必须修复

### 1. 密码明文存储
- **文件**：`pa_cli/config.py`
- **问题**：密码和 Token 明文写入 `~/.pa-cli/config.json`，泄露即账户被接管
- **方案**：
  - Token 用 `keyring` 库存系统密钥环，或至少 `chmod 600`
  - 密码不应该持久化存储，用完即弃或用 session cookie
  - 添加 `.gitignore` 提示
- **状态**：🔲

### 2. 异常体系缺失
- **文件**：全局（`api/client.py`、`crawler/account_crawler.py` 等）
- **问题**：所有错误都用 `raise Exception(...)`，上层无法区分错误类型
- **方案**：定义异常层级
  ```python
  class PACliError(Exception): pass
  class AuthError(PACliError): pass
  class APIError(PACliError): pass
  class NetworkError(PACliError): pass
  class NotFoundError(APIError): pass
  ```
- **状态**：🔲

---

## 🟠 P1 - 重要改进

### 3. API/Crawler 双轨制需收敛
- **文件**：`pa_cli/cli/webapps_cmd.py`、`pa_cli/cli/consoles_cmd.py`
- **问题**：同一个命令有两个版本（如 `reload` 和 `reload-crawler`），用户困惑，维护成本翻倍
- **方案**：
  - API 能完成的，删除 crawler 版本
  - crawler 仅用于 API 不支持的操作（`extend expiry`、`get token`、`get hits`）
  - 在命令帮助中标注认证方式（Token vs Password）
- **状态**：🔲

### 4. `pa console send` 输出等待逻辑有 bug
- **文件**：`pa_cli/cli/consoles_cmd.py`（第 62 行）
- **问题**：用 `time.sleep(1)` 硬编码等待，且通过检测 `$` 或 `>>>` 结尾判断完成，如果命令输出本身就包含这些字符会误判
- **方案**：
  - 参考 `deploy.py` 的 `_wait_for_console` 做轮询 + 超时
  - 检测新 prompt 出现（记录上一次输出位置），而非内容包含
- **状态**：🔲

### 5. deploy 没有错误恢复
- **文件**：`pa_cli/workflows/deploy.py`
- **问题**：上传到一半失败后，已上传文件不清理，webapp 状态不确定
- **方案**：
  - 添加 rollback 逻辑（至少清理已上传文件）
  - 或者在开头提示用户当前状态
- **状态**：🔲

### 6. 缺少 `--output json` 支持
- **文件**：全局
- **问题**：所有输出都是人类可读格式，无法被脚本/其他工具消费
- **方案**：Typer 支持 `--output` 选项（`human` / `json`），json 模式输出结构化数据
- **状态**：🔲

### 7. 缺少 `--dry-run`
- **文件**：`pa_cli/cli/deploy_cmd.py`
- **问题**：部署是不可逆操作，无法预览
- **方案**：添加 `--dry-run` 标志，只打印将要执行的步骤
- **状态**：🔲

---

## 🟡 P2 - 体验优化

### 8. 重复的客户端创建模式
- **文件**：`pa_cli/cli/webapps_cmd.py`、`pa_cli/cli/consoles_cmd.py`、`pa_cli/cli/files_cmd.py`
- **问题**：每个 cmd 文件都有 `_get_client()` 函数，逻辑相同
- **方案**：抽成公共装饰器或工具函数
- **状态**：🔲

### 9. 缺少进度条
- **文件**：`pa_cli/workflows/deploy.py`
- **问题**：上传大量文件时只有一行行 `Uploaded X files.`，无进度反馈
- **方案**：用 `rich.progress` 显示进度条
- **状态**：🔲

### 10. `pa console send` 没有超时控制
- **文件**：`pa_cli/cli/consoles_cmd.py`
- **问题**：`time.sleep(1)` 后如果命令还在执行，拿到的是不完整输出
- **方案**：添加 `--timeout` 参数，轮询等待输出稳定
- **状态**：🔲

### 11. Roadmap 优先级不合理
- **文件**：`README.md`
- **问题**：P3 有"数据库管理"、"Always-on tasks"，但 P1 连 `pa files ls`、`pa status` 都没有
- **方案**：
  - `pa status`（CPU/内存/磁盘）升到 P1
  - `pa files ls` 升到 P1
  - 数据库管理降到 P3
- **状态**：🔲

---

## 🟢 P3 - 远期改进

### 12. 多账号切换
- **文件**：`pa_cli/config.py`
- **问题**：config 支持多 accounts 但没有 `pa account switch` 命令
- **方案**：添加 `pa account list` + `pa account switch <username>`
- **状态**：🔲

### 13. 测试覆盖率不足
- **文件**：`tests/`
- **问题**：`test_account_crawler.py` 681 行，大量 mock 可能不覆盖真实场景
- **方案**：添加集成测试（需要真实 PA 账号），标记 `@pytest.mark.integration`
- **状态**：🔲

### 14. 配置文件无校验
- **文件**：`pa_cli/config.py`
- **问题**：`Config.load()` 直接读 JSON，格式错误会抛不明异常
- **方案**：用 pydantic 或 dataclass 做 schema 校验
- **状态**：🔲

---

## 📝 修复顺序建议

1. **P0 先修**：安全问题（#1）+ 异常体系（#2）— 这两个是其他修复的基础
2. **P1 跟进**：收敛双轨制（#3）+ 修复 console send bug（#4）+ deploy rollback（#5）
3. **P2 体验**：json 输出（#6）+ dry-run（#7）+ 进度条（#9）
4. **P3 远期**：多账号（#12）+ 测试（#13）+ 配置校验（#14）
