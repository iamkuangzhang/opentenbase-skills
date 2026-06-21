---
name: opentenbase-system-entry
description: >
  用于 AI Agent 第一次进入已有 OpenTenBase 环境时，安全识别版本、安装目录、
  管理工具、GTM/CN/DN 拓扑、进程、端口和可连接 CN。Use when an agent first
  enters an existing OpenTenBase system and needs read-only environment
  discovery before any operational change, plugin deployment, or database write.
---

# OpenTenBase System Entry

## 触发场景

当 AI Agent 第一次进入一台可能已经安装 OpenTenBase 的服务器，且尚未确认版本、管理工具和集群拓扑时，使用本技能。

## 任务目标

只读识别当前环境，回答：

- 是否存在 OpenTenBase。
- OpenTenBase 检测证据和置信度。
- `server_version`、`psql_version`、`postgres_binary_version`、`pg_config_version`。
- `psql`、`postgres`、`pg_config`、`opentenbase_ctl`、`pgxc_ctl` 的路径。
- 可连接 CN。
- GTM / CN / DN 拓扑。
- 当前更像由 `opentenbase_ctl`、`pgxc_ctl` 还是手工方式管理。
- 配置、进程、监听端口和 `pgxc_node` 是否存在明显不一致。

## 标准步骤

1. 先确认 OS 用户、主机名、IP、当前目录和内核信息。
2. 查找 `opentenbase_ctl`、`pgxc_ctl`、`psql`、`postgres`、`pg_config`。
3. 分别读取 `psql`、`postgres`、`pg_config` 的版本，不要只因工具存在就判断为 OpenTenBase。
4. 有边界地查找 `opentenbase_config.ini`、`config.ini`、`pgxc_ctl.conf`。
5. 查看 OpenTenBase / PostgreSQL / GTM / pgxc 相关进程和监听端口。
6. 只使用显式 CN 参数或配置文件中的 CN 候选连接数据库；不要根据端口号前缀猜测 CN。
7. 成功连接 CN 后，只执行只读 SQL：
   - `SELECT 1;`
   - `SELECT version();`
   - `SELECT current_database();`
   - `SELECT current_user;`
   - `SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;`
8. 对比配置、进程、监听端口和 `pgxc_node`，只报告不一致，不自动修复。

## 安全边界

禁止执行：

- `start`、`stop`、`restart`、`init`、`clean`、`kill`、`failover`。
- 节点增加、删除、切换或配置修改。
- `CREATE`、`ALTER`、`DROP`、`INSERT`、`UPDATE`、`DELETE`、`TRUNCATE`、`COPY`、`CREATE EXTENSION`。
- `sudo`。
- 无边界 `find /`。
- 读取私钥、密码、token 或无关敏感文件。

## 需要按需读取的 references

- `references/discovery-checklist.md`：手工只读检查命令。
- `references/management-tool-detection.md`：管理工具判断规则。
- `references/topology-validation.md`：拓扑一致性判断。
- `references/output-format.md`：最终结果格式。

## 结果验证

最终输出必须区分：

- `VERIFIED`：当前环境真实验证过。
- `DOCUMENTED`：来自文档或已有材料，但本次未验证。
- `UNVERIFIED`：仍不明确或未验证。

无法确认时写 `unknown`，不要猜。

## 停止并请求确认的条件

如果用户要求启停集群、修改配置、写数据库、部署插件、删除文件、提权或执行高风险命令，立即停止并请求明确确认或切换到更合适的技能。
