---
name: opentenbase-cluster-management
description: >
  用于 AI Agent 管理或指导 OpenTenBase 集群状态检查、启停流程和管理工具选择时使用。
  Covers opentenbase_ctl, pgxc_ctl, read-only status checks, start/stop workflow,
  verification, and high-risk command boundaries.
---

# OpenTenBase Cluster Management

## 触发场景

当用户询问如何查看、启动、停止或验证 OpenTenBase 集群，或要求判断当前应该使用 `opentenbase_ctl` 还是 `pgxc_ctl` 时，使用本技能。

## 任务目标

- 判断当前集群可能由 `opentenbase_ctl`、`pgxc_ctl` 还是手工方式管理。
- 给出状态检查、启停和验证流程。
- 明确哪些命令只读，哪些命令高风险。
- 在执行高风险命令前停止并要求用户明确确认。

## 标准步骤

1. 先使用 `opentenbase-system-entry` 只读识别环境。
2. 根据证据选择 reference：
   - `opentenbase_ctl` 明确可用时，读取 `references/opentenbase_ctl.md`。
   - `pgxc_ctl.conf` 明确可用时，读取 `references/pgxc_ctl.md`。
   - 只做状态确认时，读取 `references/status-check.md`。
   - 用户要求启停时，读取 `references/start-stop-verify.md`。
3. 只读阶段可执行状态查看、进程检查、端口检查和只读 SQL。
4. 启动、停止、初始化、清理、kill、failover、配置修改均属于高风险，必须先请求用户确认。

## 安全边界

本技能允许描述启停流程，但默认不得执行：

- `start`
- `stop`
- `restart`
- `init`
- `clean`
- `kill`
- `failover`
- 配置修改
- 数据库写操作
- 节点增删

## 结果验证

只读验证优先使用：

```bash
ps -ef
ss -lntp
```

以及：

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## 停止并请求确认的条件

如果下一步会改变集群状态、配置、数据、节点或服务进程，必须停止并请求用户明确确认。确认前只允许给出计划和风险说明。
