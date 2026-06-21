# 启停和验证流程

## DOCUMENTED

启停集群是高风险操作。执行前必须确认：

- 当前管理工具。
- 活跃配置文件。
- 操作目标节点。
- 是否允许影响业务。
- 是否有回滚或恢复方案。

## 启动前计划

1. 只读确认配置和节点。
2. 只读确认当前状态。
3. 向用户说明将执行的命令。
4. 等待用户明确确认。

## 启动后验证

1. 管理工具 status。
2. `ps -ef`。
3. `ss -lntp`。
4. `SELECT 1;`
5. `SELECT version();`
6. `SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;`

## 停止前计划

停止会影响服务可用性。必须确认：

- 是否停止整个集群还是指定节点。
- 是否使用 fast / immediate 等模式。
- 是否有业务连接。
- 停止后如何验证。

## UNVERIFIED

- 本轮没有执行任何 start / stop。
- 本轮没有验证停机恢复流程。
