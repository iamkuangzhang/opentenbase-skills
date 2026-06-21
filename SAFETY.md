# 安全边界

默认只允许只读识别。涉及启停、配置修改、数据库写入、节点操作时，必须先停止并请求用户明确确认。

## 允许的命令示例

- 操作系统身份：`whoami`、`id`、`hostname`、`hostname -I`、`pwd`、`date`、`uname -a`
- 工具发现：`command -v`、`type -a`、`readlink`、`ls`、`stat`
- 有边界搜索：`find <known-root> -maxdepth <small-number> ...`
- 进程和端口查看：`ps`、`pgrep`、`ss`、`netstat`、`lsof`
- 有边界读文件：`cat`、`sed`、`awk`、`grep`、`head`、`tail`
- 只读 SQL：`SELECT 1`、`SELECT version()`、`SELECT current_database()`、`SELECT current_user`、`SELECT ... FROM pgxc_node`

## 未经确认时禁止

- 启动、停止、初始化、清理或切换集群。
- 增加、删除或修改节点。
- 修改配置文件或 GUC。
- 创建、修改、截断、插入、更新、删除、复制写入或删除数据库对象。
- 执行 `CREATE EXTENSION`。
- 读取密码、私钥、token 或无关敏感文件。
- 执行无边界的 `find /` 或大范围敏感信息扫描。

如果任务需要写权限，先停止在本技能内继续执行，并要求用户明确确认或切换到其他技能。
