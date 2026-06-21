# 启停和验证流程

## 总原则

启停集群是高风险操作。只有用户明确授权后才能执行。执行前先给出计划，执行后必须验证。

## 启动前计划

1. 只读确认候选管理工具和配置文件。
2. 如果多份配置同时存在，列出候选并让用户确认活跃配置。
3. 只读确认当前状态：管理工具状态、进程、端口、可连接 CN。
4. 向用户说明准备执行的命令、目标节点、影响范围。
5. 说明失败后处理方式：保留输出、停止继续操作、不要自动 clean/kill/failover。

## pgxc_ctl 启动草案

需要用户确认后才可执行：

```bash
pgxc_ctl --home <pgxc_ctl_home> -c <pgxc_ctl.conf>
```

进入控制台后：

```text
start all
quit
```

## opentenbase_ctl 启动草案

需要用户确认后才可执行：

```bash
opentenbase_ctl start -c <config>
```

## 启动后验证

1. 管理工具状态：`monitor all` 或 `opentenbase_ctl status -c <config>`。
2. 进程：`ps -ef`。
3. 端口：`ss -lntp`。
4. 两个或多个候选 CN 的 `SELECT 1;`。
5. `SELECT version();`。
6. `SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;`。

## 停止前计划

停止会影响服务可用性。必须确认：

- 停止整个集群还是指定节点。
- 是否允许业务中断。
- 使用 fast、immediate 还是其他模式。
- 停止后如何验证。

## pgxc_ctl 停止草案

需要用户确认后才可执行：

```text
stop all -m fast
quit
```

## opentenbase_ctl 停止草案

需要用户确认后才可执行：

```bash
opentenbase_ctl stop -c <config>
```

## 禁止自动升级为破坏性操作

启动或停止失败时，不要自动执行：

```text
init all
clean all
kill all
failover
节点增删
配置修改
```

## DOCUMENTED

- 本文件给出启停前计划和启停后验证流程。

## UNVERIFIED

- 当前仓库最近一轮只读测试没有执行 start/stop。
- 停机恢复、失败重试和节点级启停尚未在本仓库 evidence 中验证。
