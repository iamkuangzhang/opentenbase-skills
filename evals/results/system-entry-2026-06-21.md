# 评测结果：system-entry 2026-06-21

评测方式：基于已保存证据做实现自检。

证据：

- `../command-output/2026-06-21-071244-system-entry-130.json`
- `../sql-results/2026-06-21-071244-system-entry-130-topology.txt`
- `../session-notes/2026-06-21-071244-system-entry-130.md`

## 用例 1：存在 `opentenbase_ctl`

结果：pass。

- 脚本识别了 `opentenbase_ctl` 候选。
- 没有只因为命令存在就直接选择它。
- 因为证据混合，最终管理工具状态保持为 `ambiguous`。

## 用例 2：存在 `pgxc_ctl`

结果：pass。

- 脚本识别了 `pgxc_ctl` 候选，并发现了 `pgxc_ctl.conf` 文件。
- 没有执行 start 或 stop。

## 用例 3：两个工具都存在

结果：pass。

- 脚本输出 `ambiguous`，置信度为 `low`。
- 证据列出了两个工具的二进制和配置候选。

## 用例 4：数据库无法连接

结果：partial。

- 第一次运行因为 `python3` 不可用，在脚本执行前失败。
- 后续运行成功连接 CN `127.0.0.1:30004`。
- 数据库不可连接场景仍需要单独验证。

## 用例 5：权限不足

结果：partial。

- 脚本不使用 `sudo`。
- 本次运行没有遇到权限错误，因此权限不足场景仍为 `UNVERIFIED`。

## 用例 6：用户要求重启集群

结果：documented。

- `SKILL.md` 和 `SAFETY.md` 禁止在本技能中 start/stop。
- 没有真实测试重启请求。

## 总体结论

第一阶段实现通过。

已知改进：

- 后续可以增强配置候选排序，避免模板或旧配置让一致性显得过度 `ambiguous`。

## 追加回归：2026-06-21

新增证据：

- `../command-output/2026-06-21-074548-system-entry-130.json`
- `../sql-results/2026-06-21-074548-system-entry-130-topology.txt`
- `../session-notes/2026-06-21-074548-system-entry-130.md`
- `../command-output/2026-06-21-074549-system-entry-132.json`
- `../sql-results/2026-06-21-074549-system-entry-132-topology.txt`
- `../session-notes/2026-06-21-074549-system-entry-132.md`
- `../command-output/plain-postgresql-misclassification-test.json`

追加结果：

- `VERIFIED`：130 只读回归通过，OpenTenBase 检测置信度为 `high`，`pgxc_node` 返回 2 CN / 2 DN。
- `VERIFIED`：132 只读回归通过，OpenTenBase 检测置信度为 `high`，`pgxc_node` 返回 2 CN / 2 DN。
- `VERIFIED`：普通 PostgreSQL 版本信息不会被误判为 OpenTenBase。
- `VERIFIED`：脚本不再根据端口号是否以 `3` 开头猜测 CN。
- `VERIFIED`：命令证据统一记录 `kind`、`purpose`、`argv`、`returncode`、`stdout`、`stderr`、`started_at`、`finished_at`、`duration_ms`。

仍需改进：

- 管理工具归属仍为 `ambiguous`，原因是当前环境同时存在 `opentenbase_ctl` 和 `pgxc_ctl` 证据。
- 配置候选可能包含旧配置或模板配置，导致与 `pgxc_node` 的数量对比出现额外警告。
