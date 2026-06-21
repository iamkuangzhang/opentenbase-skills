# opentenbase_ctl

## 用途

`opentenbase_ctl` 是部分 OpenTenBase 5 环境中存在的集群管理工具。它可能提供 status、start、stop、shell、sql、scp、GUC 等能力，但不同安装包和版本的参数可能不同，不能按名字猜测用法。

## 查找命令和配置

只读查找：

```bash
command -v opentenbase_ctl
find "$HOME" /data /opt -maxdepth 6 \( -name opentenbase_config.ini -o -name config.ini \) 2>/dev/null
```

如果发现多份配置，只列出候选并请求用户确认。不要把 TDSQL 资料中的固定路径、固定用户或默认密码当作 OpenTenBase 事实。

## 查看帮助

先读当前机器真实帮助：

```bash
opentenbase_ctl --help
opentenbase_ctl status --help
opentenbase_ctl start --help
opentenbase_ctl stop --help
opentenbase_ctl shell --help
opentenbase_ctl sql --help
opentenbase_ctl scp --help
```

如果缺少动态库或环境变量，记录错误，不要自行修改系统环境。

## 状态查看

常见形式：

```bash
opentenbase_ctl status -c <config>
```

执行前确认 `<config>` 是用户认可的真实配置文件。输出中重点读取：

- 实例名称、版本。
- GTM、CN、DN 节点。
- 节点 IP、端口、主从角色。
- Running、Stopped、Unknown 等状态。
- Master CN connection info。
- PATH / LD_LIBRARY_PATH 提示。
- 可直接使用的 `psql` 连接命令。

## 启动和停止

以下命令会改变集群状态，不能自动执行：

```bash
opentenbase_ctl start -c <config>
opentenbase_ctl stop -c <config>
```

执行前必须向用户说明影响范围、目标配置、预计验证步骤和失败处理方式。

## Shell / SQL / SCP / GUC

这些能力的真实语法必须以当前机器 `--help` 为准：

- `shell`：可能用于在节点上执行 shell 命令。
- `sql`：可能用于向集群或 CN 执行 SQL。
- `scp`：可能用于分发文件。
- `GUC`：可能用于配置参数管理。

在未确认作用范围前，不要假设：

- shell 默认作用于哪些节点。
- scp 是否覆盖已有文件。
- sql 是否连接 Master CN。
- GUC 修改是否立即影响运行集群。
- 部分节点失败时退出码如何表现。

## 操作后验证

操作后至少交叉验证：

1. `opentenbase_ctl status -c <config>`
2. `ps -ef`
3. `ss -lntp`
4. `psql SELECT 1`
5. `SELECT version()`
6. `SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name`

## 常见错误排查

- `command not found`：工具未加入 PATH，先用 `find` 或安装目录定位，不要直接改环境。
- 动态库缺失：记录缺失库和当前 `LD_LIBRARY_PATH`，让用户确认是否加载安装环境。
- 配置不存在：列出候选配置，不要自动创建。
- 状态与端口不一致：同时检查进程、监听端口和只读 SQL。

## VERIFIED

- `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json` 显示 `192.168.244.130` 上 `opentenbase_ctl status --help` 可输出 status 用法。
- 同一 evidence 显示 `192.168.244.132` 直接执行 `opentenbase_ctl status --help` 时出现 `libpqxx.so` 缺失，需要环境确认。

## DOCUMENTED

- `opentenbase_ctl status -c <config>` 可作为状态查看入口，具体字段以当前机器输出为准。
- start/stop/shell/sql/scp/GUC 是需要逐项确认帮助和作用范围的管理能力。

## TDSQL_CANDIDATE

- TDSQL PostgreSQL 资料中包含组件管理、Shell、SQL、SCP、GUC、配置和启停流程的讲解，可用于形成检查思路。
- TDSQL 的 OSS、TStudio、固定目录、固定用户、默认密码、商业组件和版本专属命令不得写成 OpenTenBase 事实。

## UNVERIFIED

- 本仓库当前未完成 `opentenbase_ctl start`、`opentenbase_ctl stop`、shell、sql、scp、GUC 的真实 OpenTenBase 行为验证。
