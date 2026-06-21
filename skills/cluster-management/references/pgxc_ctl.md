# pgxc_ctl

## 用途

`pgxc_ctl` 是 OpenTenBase / Postgres-XC 风格环境中常见的交互式集群管理工具，通常依赖 `pgxc_ctl.conf`。它可以查看、启动、停止和维护 GTM、CN、DN，但其中许多命令会直接影响集群状态。

## 查找命令和配置

只读查找：

```bash
command -v pgxc_ctl
find "$HOME" /data /opt -maxdepth 6 -name pgxc_ctl.conf 2>/dev/null
```

如果出现多份 `pgxc_ctl.conf`，不要自动选第一份。应列出候选路径，并结合以下证据让用户确认：

- 配置文件所在目录是否与当前安装目录一致。
- 配置中的节点名、IP、端口是否与进程、监听端口、`pgxc_node` 接近。
- 该配置是否是模板、测试文件或旧版本残留。

## Shell 命令与交互命令

`pgxc_ctl` 本身是 shell 命令；`monitor all`、`start all`、`stop all -m fast`、`quit` 是进入 `pgxc_ctl` 控制台之后输入的交互命令。

常见进入方式：

```bash
pgxc_ctl
```

或显式指定 home 和配置：

```bash
pgxc_ctl --home <pgxc_ctl_home> -c <pgxc_ctl.conf>
```

进入后才输入：

```text
monitor all
quit
```

不要在普通 shell 中直接执行 `monitor all`。

## 状态查看

`monitor all` 是首选只读状态命令。输出中常见判断点：

- `Running`、`Not running`、`Stopped` 等状态。
- GTM、CN、DN 是否都出现。
- 节点名是否与配置文件和 `pgxc_node` 一致。
- 是否有 `ssh`、hostname、权限、配置数组长度不一致等错误。

## 启动与停止

以下是操作流程，不代表可以自动执行：

```text
start all
stop all -m fast
quit
```

执行前必须确认活跃配置、目标节点和影响范围。停止会影响业务可用性，启动可能拉起多个远端节点进程。

## 指定节点操作

如果需要指定节点操作，必须先从当前 `pgxc_ctl --help`、配置文件或交互帮助确认真实语法。不要猜测节点名，不要把 CN/DN 的数据库名、主机名和 `pgxc_ctl` 节点名混用。

## 常见错误排查

- `pgxc_ctl.conf not found`：`--home` 或 `-c` 指向的配置不存在，或目录只有控制台脚本没有配置。
- `Number of elements ... are different`：配置数组数量不一致，例如节点名数量与端口数量不匹配。
- `Could not resolve hostname`：配置里的主机名不能解析，需检查 hosts/DNS/节点名。
- `Permission denied` 或 ssh 失败：远端免密、用户、权限不满足。
- `Connection refused`：目标 CN/DN 未监听该端口，或服务未启动。
- `postmaster.pid` 存在但进程不存在：可能是异常残留，不能直接删除，需先让用户确认。

## 操作后验证

用多种证据交叉验证，不要只看一条命令：

```bash
ps -ef
ss -lntp
psql -h <cn_host> -p <cn_port> -d postgres -U <user> -Atc 'SELECT 1;'
psql -h <cn_host> -p <cn_port> -d postgres -U <user> -Atc 'SELECT version();'
psql -h <cn_host> -p <cn_port> -d postgres -U <user> -Atc 'SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;'
```

## 高风险命令

以下命令可能破坏集群、清理数据或触发主备切换，不得自动执行：

```text
init all
clean all
kill all
failover
节点增删
配置修改
```

## VERIFIED

- 当前仓库 evidence 已验证 `192.168.244.130` / `192.168.244.132` 可执行 `pgxc_ctl monitor all`。
- `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json` 显示该轮测试时 GTM、CN、DN 均为 `Not running`。

## DOCUMENTED

- `start all`、`stop all -m fast` 是 `pgxc_ctl` 控制台中的集群启停操作，应在用户授权后执行。

## TDSQL_CANDIDATE

- TDSQL PostgreSQL 资料中提到通过进程、配置和组件状态综合判断 GTM/CN/DN。该思路可作为 OpenTenBase 排查参考，但具体路径、用户、命令参数不能直接套用。

## UNVERIFIED

- 本仓库当前未把 `start all`、`stop all -m fast`、`init all`、`clean all`、`kill all` 或 `failover` 标记为已验证。
