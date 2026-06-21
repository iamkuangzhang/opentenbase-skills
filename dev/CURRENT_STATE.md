# 当前状态

最后更新：2026-06-21 本轮结构调整后

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

## 已记录但尚未全部验证

- `DOCUMENTED`：该技能只允许执行只读环境识别。
- `DOCUMENTED`：该技能必须保存证据，并使用 `VERIFIED`、`DOCUMENTED`、`UNVERIFIED` 标签。

## 当前工作状态

`system-entry` 已冻结为正式技能；本轮新增架构知识和集群管理技能。

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

下一步建议补充 `basic-usage` 技能，覆盖连接数据库、基础 SQL、查看表和只读排查。
