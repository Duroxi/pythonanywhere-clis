# Databases 命令

数据库管理相关的命令，用于查看 MySQL 数据库信息。

---

## pa databases mysql

显示 MySQL 数据库信息。

### 语法

```bash
pa databases mysql
```

### 说明

获取当前账户关联的 MySQL 数据库信息。

### 示例

```bash
$ pa databases mysql
MySQL Databases:
  myuser$mydb: 10.5 MB
  myuser$testdb: 2.1 MB
```

**无数据库时：**

```bash
$ pa databases mysql
No MySQL databases found.
```

### 输出字段

| 字段 | 说明 |
|------|------|
| database_name | 数据库名称 |
| size | 数据库大小 |

### 前置条件

- 需先运行 `pa init` 完成账户配置
