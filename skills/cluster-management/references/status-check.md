# 状态检查

## 允许的只读检查

```bash
command -v opentenbase_ctl
command -v pgxc_ctl
ps -ef
ss -lntp
```

只读 SQL：

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## 判断点

- 是否有 OpenTenBase 相关进程。
- 是否有 CN / DN / GTM 监听端口。
- 是否至少一个 CN 可连接。
- `pgxc_node` 是否能返回 CN / DN 拓扑。
- 配置、进程、端口和 `pgxc_node` 是否一致。

## VERIFIED

- 130 / 132 已通过 system-entry evidence 验证可读 `pgxc_node`。
- 2026-06-21 的 cluster-management 只读测试显示，当前 130 / 132 的 `pgxc_ctl monitor all` 返回 GTM、CN、DN Not running。

## UNVERIFIED

- 当前 evidence 不能证明所有节点都完全健康，只能证明只读拓扑可见和至少一个 CN 可连接。
- 当前 cluster-management evidence 不能验证 SQL 连接，因为测试时集群处于 Not running。
