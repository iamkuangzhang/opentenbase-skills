# 当前状态

最后更新：2026-06-21 TDSQL 资料纠偏后

## 当前阶段目标

从单一 `system-entry` 环境探测，扩展为面向 OpenTenBase 使用的 Skills 包。

## 已完成并验证

- `VERIFIED`：最小项目骨架已存在。
- `VERIFIED`：`skills/system-entry/SKILL.md` 已完成。
- `VERIFIED`：所需 references 已存在。
- `VERIFIED`：`discover_environment.py` 可在本地使用 `--no-database` 运行。
- `VERIFIED`：`discover_environment.py` 已在真实主机 `192.168.244.130` 上以 `opentenbase` 用户运行，解释器为 `/opt/python3.11/bin/python3.11`。
- `VERIFIED`：真实运行检测到了 OpenTenBase v5.21.8.11、二进制目录、工具候选、进程、端口、可连接 CN 和 `pgxc_node` 拓扑。
- `VERIFIED`：证据文件已保存到 `dev/evidence/`。
- `VERIFIED`：技能通过 `quick_validate.py` 校验。
- `VERIFIED`：中文化后的最新脚本已在 `192.168.244.130` 重新只读运行，证据为 `dev/evidence/command-output/2026-06-21-072430-system-entry-130-cn.json`。
- `VERIFIED`：脚本已增强 OpenTenBase 检测置信度、版本字段拆分、统一命令证据记录和显式数据库连接参数。
- `VERIFIED`：新脚本已在 `192.168.244.130` 只读回归，证据为 `dev/evidence/command-output/2026-06-21-074548-system-entry-130.json`。
- `VERIFIED`：新脚本已在 `192.168.244.132` 只读回归，证据为 `dev/evidence/command-output/2026-06-21-074549-system-entry-132.json`。
- `VERIFIED`：已增加普通 PostgreSQL 误判测试，确认只有普通 PostgreSQL 版本信息时不会判定为 OpenTenBase。
- `VERIFIED`：已新增 `opentenbase-architecture` 技能。
- `VERIFIED`：已新增 `opentenbase-cluster-management` 技能。
- `VERIFIED`：开发材料已迁移到 `dev/`，正式技能保留在 `skills/`。
- `VERIFIED`：本轮只读测试执行了 `pgxc_ctl monitor all`，130 / 132 当前均显示 GTM、CN、DN Not running，证据为 `dev/evidence/command-output/2026-06-21-180007-cluster-readonly-130-132.json`。
- `VERIFIED`：本轮未继续扩展 `system-entry` 探测逻辑，只对 `architecture` 和 `cluster-management` 做内容纠偏。
- `VERIFIED`：本轮已读取用户提供的 3 份 TDSQL PostgreSQL PDF，并将相关内容仅作为 `TDSQL_CANDIDATE` 候选知识写入正式技能。
- `VERIFIED`：`cluster-management` 已改为面向工具使用的操作手册，覆盖 `pgxc_ctl`、`opentenbase_ctl`、shell/交互命令区分、状态判断、启停验证和高风险边界。
- `VERIFIED`：`architecture` 已补充 CN/DN/GTM、Share-Nothing、分布表、复制表、分布键、数据倾斜、Join 代价和分布式事务判断。

## 已记录但尚未全部验证

- `DOCUMENTED`：该技能只允许执行只读环境识别。
- `DOCUMENTED`：正式技能必须区分 `VERIFIED`、`DOCUMENTED`、`TDSQL_CANDIDATE`、`UNVERIFIED`。
- `TDSQL_CANDIDATE`：TDSQL 资料中的 Shell、SQL、SCP、GUC、分片键、hash 分片、Join 重分布、两阶段提交等内容只能作为 OpenTenBase 学习候选，尚未标记为 OpenTenBase 实测事实。

## 当前工作状态

`system-entry` 已冻结为正式技能；本轮聚焦 `architecture` 和 `cluster-management` 的内容纠偏，不新增技能。

## 已知问题

- 远端 `192.168.244.130` 的 `opentenbase` 用户缺少 `python3`，但 `/opt/python3.11/bin/python3.11` 可用。
- 管理工具选择为 `ambiguous`，因为同时存在 `opentenbase_ctl` 和 `pgxc_ctl` 相关证据。
- 多个配置候选导致 CN 数量一致性警告。
- 130 和 132 均存在配置候选与 `pgxc_node` 数量不一致的警告，当前只报告，不自动修复。
- 本轮测试时 130 / 132 集群处于 Not running 状态，因此不能把 SQL 连接验证标记为本轮 VERIFIED。

## 测试环境摘要

- `VERIFIED`：`192.168.244.130` / `otb130` / OpenTenBase v5.21.8.11 / 可连接 CN / `pgxc_node` 返回 2 CN 和 2 DN。
- `VERIFIED`：`192.168.244.132` / OpenTenBase v5.21.8.11 / 可连接 CN / `pgxc_node` 返回 2 CN 和 2 DN。

## 工作区提醒

根目录 OpenTenBase 工作区在本项目创建前已经存在修改和未跟踪文件。不要 reset，也不要覆盖无关内容。

## 安全限制

- 只读。
- 不启动或停止集群。
- 不执行数据库写操作。
- 不修改配置。

## 下一步唯一建议

下一步建议用 OpenTenBase 官方资料或当前集群只读 SQL 逐项验证 `TDSQL_CANDIDATE` 内容，再决定哪些可以提升为 `DOCUMENTED` 或 `VERIFIED`。
