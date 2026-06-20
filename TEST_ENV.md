# 测试环境

当前环境事实以证据文件为准，不以聊天记忆为准。

## VERIFIED：2026-06-21 在 192.168.244.130 执行 system-entry

- 证据：
  - `evidence/command-output/2026-06-21-072430-system-entry-130-cn.json`
  - `evidence/sql-results/2026-06-21-072430-system-entry-130-topology.txt`
  - `evidence/session-notes/2026-06-21-072430-system-entry-130-cn.md`
- 早期证据：
  - `evidence/command-output/2026-06-21-071244-system-entry-130.json`
  - `evidence/sql-results/2026-06-21-071244-system-entry-130-topology.txt`
  - `evidence/session-notes/2026-06-21-071244-system-entry-130.md`
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

## VERIFIED：解释器失败尝试

- 证据：
  - `evidence/command-output/2026-06-21-071043-system-entry-130.json`
  - `evidence/session-notes/2026-06-21-071043-system-entry-130.md`
- `opentenbase` 用户下没有可用的 `python3`。
- `/opt/python3.11/bin/python3.11` 可用，并用于成功执行。

## UNVERIFIED

- 本项目尚未测试 `192.168.244.132`。
- 没有测试或批准任何写操作。
