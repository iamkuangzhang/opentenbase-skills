---
name: opentenbase-cluster-management
description: >
  用于 AI Agent 指导 OpenTenBase 集群管理工具使用、状态检查、启停流程和风险判断时使用。
  Covers pgxc_ctl, opentenbase_ctl, management tool selection, read-only health checks,
  start/stop workflow, verification steps, and high-risk command boundaries.
---

# OpenTenBase Cluster Management

## 触发场景

当用户询问如何查看、启动、停止、验证 OpenTenBase 集群，或要求判断当前应该使用 `opentenbase_ctl`、`pgxc_ctl` 还是手工命令时，使用本技能。

## 任务目标

- 找到当前机器上的 `pgxc_ctl`、`opentenbase_ctl` 和候选配置文件。
- 区分 shell 命令和交互控制台命令，避免把 `monitor all` 等交互命令直接当作系统命令执行。
- 根据配置、进程、端口、只读连接和 `pgxc_node` 综合判断管理工具，而不是只看命令是否存在。
- 指导用户执行状态检查、启停计划和启停后的验证。
- 明确高风险命令，执行前必须停止并请求用户确认。

## 标准步骤

1. 先做只读识别：`command -v`、候选配置文件、进程、端口、可连接 CN、`pgxc_node`。
2. 如果存在多份配置文件，只列出候选、说明差异，并请用户确认活跃配置；不要自行猜测。
3. 根据证据选择 reference：
   - 需要使用 `pgxc_ctl` 时，读取 `references/pgxc_ctl.md`。
   - 需要使用 `opentenbase_ctl` 时，读取 `references/opentenbase_ctl.md`。
   - 只做状态确认时，读取 `references/status-check.md`。
   - 用户明确要求启动或停止时，读取 `references/start-stop-verify.md`。
4. 启动或停止前，先向用户汇报：当前真实状态、推荐工具、准备执行的命令、影响范围、验证步骤、失败处理方式。
5. 未获得明确授权前，不执行 `start`、`stop` 或任何会改变集群状态的命令。

## 只读检查

允许执行：

```bash
command -v opentenbase_ctl
command -v pgxc_ctl
ps -ef
ss -lntp
```

允许执行只读 SQL：

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## 高风险边界

以下命令或行为不得自动执行，必须先请求用户明确确认：

- `start`、`stop`、`restart`
- `init`、`clean`、`kill`、`failover`
- 节点增删、主备切换、配置修改
- 数据库写操作
- 无边界扫描，例如 `find /`
- 使用固定路径、固定用户、默认密码作为事实

## 结果输出

回答时按证据标注：

- `VERIFIED`：已在当前 OpenTenBase 环境只读验证。
- `DOCUMENTED`：来自 OpenTenBase 文档、工具帮助或已确认语义，但当前未执行。
- `TDSQL_CANDIDATE`：来自 TDSQL PostgreSQL 资料，可作为理解参考，尚待 OpenTenBase 验证。
- `UNVERIFIED`：证据不足或仍不确定。

## 停止并请求确认的条件

如果下一步会改变集群状态、配置、数据、节点或服务进程，必须停止并请求用户明确确认。确认前只允许给出计划、命令草案和风险说明。
