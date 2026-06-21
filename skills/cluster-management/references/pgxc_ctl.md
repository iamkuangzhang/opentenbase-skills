# pgxc_ctl

## DOCUMENTED

`pgxc_ctl` 是 OpenTenBase / Postgres-XC 风格环境中常见的交互式集群管理工具，通常依赖 `pgxc_ctl.conf`。

## 工作目录和配置

需要确认：

```bash
command -v pgxc_ctl
find "$HOME" /data /opt -maxdepth 5 -name pgxc_ctl.conf 2>/dev/null
```

目录存在不等于配置可用。必须确认 `pgxc_ctl.conf` 存在且内容结构合理。

## 进入控制台

常见形式：

```bash
pgxc_ctl
```

或：

```bash
pgxc_ctl --home <pgxc_ctl_home> -c <pgxc_ctl.conf>
```

实际参数以当前机器帮助和配置为准。

## 只读状态

允许在本轮只读测试中验证：

```text
monitor all
```

## 高风险命令

以下命令会改变集群状态或可能造成破坏，必须明确确认：

```text
start all
stop all -m fast
init all
clean all
kill all
failover
```

## 指定节点操作

`pgxc_ctl` 支持按节点类型或节点名操作时，必须先确认命令语法和目标节点。不要用猜测的节点名执行变更命令。

## 操作后验证

只读验证组合：

```bash
ps -ef
ss -lntp
psql -h <cn_host> -p <cn_port> -d postgres -U <user> -Atc 'SELECT 1;'
psql -h <cn_host> -p <cn_port> -d postgres -U <user> -Atc 'SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;'
```

## VERIFIED

- 当前仓库 evidence 已验证 130 / 132 可通过 CN 只读查询 `pgxc_node`。
- `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json` 验证了 `pgxc_ctl monitor all` 是可执行的只读状态查看。
- 同一证据显示本轮测试时 130 / 132 的 GTM、CN、DN 均为 Not running。

## UNVERIFIED

- 本轮尚未执行 `start all`、`stop all -m fast`、`init all`、`clean all`、`kill all` 或 `failover`。
