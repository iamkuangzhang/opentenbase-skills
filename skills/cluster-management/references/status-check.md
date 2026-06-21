# 状态检查

## 目标

状态检查不是为了“自动修复”，而是用只读证据回答：

- 集群组件是否有进程。
- CN/DN/GTM 是否监听预期端口。
- 是否至少有一个 CN 可连接。
- `pgxc_node` 中的拓扑是否与配置、进程、端口大体一致。
- 当前推荐使用哪种管理工具。

## 允许的只读检查

```bash
command -v opentenbase_ctl
command -v pgxc_ctl
ps -ef
ss -lntp
```

候选配置查找必须限制范围：

```bash
find "$HOME" /data /opt -maxdepth 6 -name pgxc_ctl.conf 2>/dev/null
find "$HOME" /data /opt -maxdepth 6 \( -name opentenbase_config.ini -o -name config.ini \) 2>/dev/null
```

只读 SQL：

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## postmaster.pid

如果需要判断数据目录状态，可以只读查看 `postmaster.pid` 是否存在，并核对其中 PID 是否仍有进程。不要自动删除 `postmaster.pid`。

## 判断管理工具

不要仅根据 `command -v` 判定。综合：

- 是否存在对应配置文件。
- 配置中的节点和端口是否接近当前进程、端口、`pgxc_node`。
- 管理工具 status/monitor 是否能读取该配置。
- 当前环境变量是否足以运行工具。

证据不足时输出 `ambiguous`，不要强行选择。

## 输出判断

- 一个 CN 可连接，不代表所有 CN/DN/GTM 正常。
- `pgxc_node` 是数据库视角拓扑，不等同于操作系统进程状态。
- 端口监听说明进程可能存在，但仍需 SQL 连接验证。
- 配置文件存在不代表它是活跃配置。

## VERIFIED

- 130 / 132 曾通过 system-entry evidence 验证可读 `pgxc_node`。
- 2026-06-21 的 cluster-management 只读测试显示，测试当时 130 / 132 的 `pgxc_ctl monitor all` 返回 GTM、CN、DN `Not running`。

## TDSQL_CANDIDATE

- TDSQL PostgreSQL 资料中将进程、组件状态和配置结合用于判断集群状态。该方法可作为 OpenTenBase 排查思路，具体字段和路径必须另行验证。

## UNVERIFIED

- 当前 cluster-management evidence 不能证明所有节点健康。
- 当前 cluster-management evidence 不能证明启停后的恢复流程。
