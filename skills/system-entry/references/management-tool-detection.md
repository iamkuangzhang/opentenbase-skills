# 管理工具识别

不要只因为 `command -v` 找到了某个命令，就直接认定当前集群由它管理。
也不要只因为存在 `psql`、`postgres`、`pg_config`，就认定当前环境是 OpenTenBase。

需要综合以下证据：

- 工具二进制路径。
- 配置文件。
- 进程命令行。
- 数据目录路径。
- 已知安全且配置明确时的 `opentenbase_ctl status` 输出。
- `pgxc_ctl.conf`。
- 数据库中的 `pgxc_node`。
- `server_version` 是否包含 OpenTenBase。
- `postgres_binary_version`、`pg_config_version` 是否包含 OpenTenBase。

## 选择规则

- 只有当 `opentenbase_ctl` 的二进制、配置或 status 输出与运行进程和数据库拓扑相互印证时，才高置信度选择 `opentenbase_ctl`。
- 只有当 `pgxc_ctl.conf` 与运行进程和数据库拓扑相互印证时，才高置信度选择 `pgxc_ctl`。
- 当两类工具都存在且证据冲突或不完整时，输出 `ambiguous`。
- 当安全证据无法识别管理工具时，输出 `unknown`。

普通 PostgreSQL 工具版本只能说明 PostgreSQL 工具存在，不能证明 OpenTenBase 存在。

## 配置说明

- `opentenbase_ctl` 通常使用 INI 风格的集群配置。
- `pgxc_ctl` 通常使用 `pgxc_ctl.conf` 和交互式 shell。
- 仅存在名为 `pgxc_ctl` 的目录不够，必须存在可用且结构合理的配置文件。

本技能中禁止运行 `start all`、`stop all`、`init all`、`clean all`。
