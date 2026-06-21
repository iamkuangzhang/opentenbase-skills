# 测试环境

当前环境事实以证据文件为准，不以聊天记忆为准。

## VERIFIED：2026-06-21 在 192.168.244.130 执行 system-entry

- 证据：
  - `dev/evidence/command-output/2026-06-21-074548-system-entry-130.json`
  - `dev/evidence/sql-results/2026-06-21-074548-system-entry-130-topology.txt`
  - `dev/evidence/session-notes/2026-06-21-074548-system-entry-130.md`
- 早期证据：
  - `dev/evidence/command-output/2026-06-21-072430-system-entry-130-cn.json`
  - `dev/evidence/sql-results/2026-06-21-072430-system-entry-130-topology.txt`
  - `dev/evidence/session-notes/2026-06-21-072430-system-entry-130-cn.md`
  - `dev/evidence/command-output/2026-06-21-071244-system-entry-130.json`
  - `dev/evidence/sql-results/2026-06-21-071244-system-entry-130-topology.txt`
  - `dev/evidence/session-notes/2026-06-21-071244-system-entry-130.md`
- 远端 OS 用户：`opentenbase`
- 主机名：`otb130`
- 主机上报地址：`192.168.244.130 192.168.244.131`
- 检测到 OpenTenBase：true
- OpenTenBase 版本：`PostgreSQL 11.0 @ OpenTenBase_v5.21.8.11 (commit: 760b03096) 2025-10-12 21:07:13`
- 二进制目录：`/data/opentenbase/install/opentenbase_bin_v2.0/bin`
- `pg_config`：`/data/opentenbase/install/opentenbase_bin_v2.0/bin/pg_config`
- 管理工具结果：`ambiguous`，置信度 `low`
- 原因：同时发现了 `opentenbase_ctl` 和 `pgxc_ctl` 的二进制/配置线索，并发现多个配置候选。
- 可连接 CN：`127.0.0.1:30004`
- `pgxc_node`：2 个 CN，2 个 DN
- 一致性状态：`ambiguous`
- 警告：配置候选中的 CN 数量与 `pgxc_node` 查询结果不同。

## VERIFIED：2026-06-21 在 192.168.244.132 执行 system-entry

- 证据：
  - `dev/evidence/command-output/2026-06-21-074549-system-entry-132.json`
  - `dev/evidence/sql-results/2026-06-21-074549-system-entry-132-topology.txt`
  - `dev/evidence/session-notes/2026-06-21-074549-system-entry-132.md`
- OpenTenBase detected：true
- Detection confidence：`high`
- OpenTenBase 版本：`PostgreSQL 11.0 @ OpenTenBase_v5.21.8.11 (commit: 760b03096) 2025-10-12 21:07:13`
- 管理工具结果：`ambiguous`
- 可连接 CN：1 个
- `pgxc_node`：2 个 CN，2 个 DN
- 一致性状态：`ambiguous`
- 备注：`127.0.0.1:30004` 在 132 上不可连接，但脚本继续尝试配置候选并找到可达 CN。

## VERIFIED：普通 PostgreSQL 误判测试

- 证据：
  - `dev/evidence/command-output/plain-postgresql-misclassification-test.json`
- 单元测试确认：只有普通 PostgreSQL 版本信息时，`detected=false`，`confidence=none`。

## VERIFIED：解释器失败尝试

- 证据：
  - `dev/evidence/command-output/2026-06-21-071043-system-entry-130.json`
  - `dev/evidence/session-notes/2026-06-21-071043-system-entry-130.md`
- `opentenbase` 用户下没有可用的 `python3`。
- `/opt/python3.11/bin/python3.11` 可用，并用于成功执行。

## UNVERIFIED

- 没有测试或批准任何写操作。

## VERIFIED：2026-06-21 cluster-management 只读测试

- 证据：
  - `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json`
  - `dev/evidence/session-notes/2026-06-21-180007-cluster-readonly-130-132.md`
- 130 / 132 均存在 `opentenbase_ctl`、`pgxc_ctl`、`psql`。
- 130 / 132 均执行了 `pgxc_ctl monitor all`。
- `monitor all` 显示 GTM、CN、DN 均为 Not running。
- `ps -ef` 未发现运行中的 OpenTenBase postgres / gtm 进程。
- `ss -lntp` 未发现 OpenTenBase 业务端口监听。
- 本轮未执行任何启停、初始化、清理、failover、配置修改或数据库写操作。

## UNVERIFIED：2026-06-21 cluster-management 只读测试

- 因当前集群 Not running，本轮无法验证 `SELECT 1`、`SELECT version()`、`pgxc_node`。
- 未验证任何 start / stop 命令。
