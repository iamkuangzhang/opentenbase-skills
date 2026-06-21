# opentenbase_ctl

## DOCUMENTED

`opentenbase_ctl` 是 OpenTenBase 5 环境中可能存在的集群管理工具。不同安装中的配置路径和参数可能不同，不能根据命令名猜测用法。

## 配置和工作目录

识别时优先查找：

```bash
command -v opentenbase_ctl
find "$HOME" /data /opt -maxdepth 5 -name opentenbase_config.ini -o -name config.ini 2>/dev/null
```

不要无边界执行 `find /`。

## 状态查看

只读状态查看通常围绕：

```bash
opentenbase_ctl status -c <config>
```

执行前必须确认 `<config>` 是真实配置文件，而不是模板或旧文件。

## 启动和停止

以下属于高风险命令，本技能只能在用户明确确认后执行：

```bash
opentenbase_ctl start -c <config>
opentenbase_ctl stop -c <config>
```

## Shell、SQL、SCP、GUC

`opentenbase_ctl` 可能提供 shell、sql、scp、GUC 管理等能力。它们的参数和作用范围必须以当前机器 `--help` 输出为准。

在未确认作用范围前，不要假设：

- shell 默认操作哪些节点。
- scp 是否覆盖远端文件。
- sql 子命令是否连接 Master CN。
- GUC 修改是否立即影响运行集群。

## 操作后验证

只读验证顺序：

1. `opentenbase_ctl status -c <config>`
2. `ps -ef`
3. `ss -lntp`
4. `psql SELECT 1`
5. `SELECT * FROM pgxc_node`

## VERIFIED

- 当前仓库已有 evidence 证明 130 / 132 可以只读查询 `pgxc_node`。
- `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json` 显示 130 上 `opentenbase_ctl status --help` 可输出 status 用法。

## UNVERIFIED

- 本轮尚未验证 `opentenbase_ctl start` 或 `opentenbase_ctl stop`。
- 本轮尚未验证 shell、sql、scp、GUC 的完整行为。
- 132 上直接执行 `opentenbase_ctl status --help` 报 `libpqxx.so` 缺失，尚未验证正确环境变量下的行为。
