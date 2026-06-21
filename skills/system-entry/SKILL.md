---
name: opentenbase-system-entry
description: >
  用于 AI Agent 第一次进入已有 OpenTenBase 环境时，安全识别版本、安装目录、
  管理工具、GTM/CN/DN 拓扑、进程、端口和可连接 CN。Use when an agent first
  enters an existing OpenTenBase system and needs read-only environment
  discovery before any operational change, plugin deployment, or database write.
---

# OpenTenBase System Entry

当当前会话尚未识别 OpenTenBase 环境时，先使用本技能，再考虑任何后续操作。

## 目标

生成一份有证据支撑的环境摘要，且不修改系统、数据库或集群状态。

## 强制安全边界

不要启动、停止、初始化、清理、切换、增加、删除或重新配置节点。
不要执行 `CREATE`、`ALTER`、`DROP`、`INSERT`、`UPDATE`、`DELETE`、`TRUNCATE`、`COPY`、`CREATE EXTENSION`。
不要使用 `sudo`。
不要读取私钥、密码、token 或无关敏感信息。

如果用户在本技能执行期间要求写操作，先完成只读识别，然后要求明确确认或切换到其他技能。

## 默认流程

1. 如果还没有读过，先读 `../../SAFETY.md` 和 `../../shared/readonly-commands.md`。
2. 优先运行 `scripts/discover_environment.py`。
3. 将原始输出保存到 `evidence/command-output/`，SQL/拓扑输出保存到 `evidence/sql-results/`。
4. 如果脚本输出不完整，只能按 `references/discovery-checklist.md` 做有边界的手工检查。
5. 按 `references/management-tool-detection.md` 识别管理工具候选。
6. 按 `references/topology-validation.md` 交叉校验配置、进程、端口和 `pgxc_node`。
7. 按 `references/output-format.md` 输出最终摘要。
8. 结束前更新 `CURRENT_STATE.md`，并写入 session note。

## 必须回答的问题

- 当前 OS 用户、主机名和 IP 地址。
- 是否检测到 OpenTenBase、检测置信度和检测证据。
- OpenTenBase 二进制目录。
- 分开报告 `server_version`、`psql_version`、`postgres_binary_version`、`pg_config_version`。
- `psql`、`postgres`、`pg_config`、`opentenbase_ctl`、`pgxc_ctl` 的位置。
- 管理工具结论：selected、candidate、ambiguous 或 unknown，并给出证据。
- GTM / CN / DN 相关进程。
- 相关监听端口。
- 可连接 CN。
- 能连接时的 `pgxc_node` 拓扑。
- 配置、进程、监听端口和数据库拓扑之间是否一致；只报告不一致，不自动修复。
- 所有 shell 命令和 SQL 都要记录用途、命令、退出码、stdout、stderr、耗时和时间戳。
- 未知项、警告、权限限制，以及是否允许写操作。

## 事实标签

只能使用以下标签：

- `VERIFIED`：已在当前真实环境测试，并保存证据。
- `DOCUMENTED`：来自文档、源码或可信资料，但未在当前环境测试。
- `UNVERIFIED`：推断、不可用、不明确或尚未测试。

不要把 `DOCUMENTED` 或 `UNVERIFIED` 写成 `VERIFIED`。

## 参考文件

- 手工检查顺序：`references/discovery-checklist.md`
- 管理工具判断：`references/management-tool-detection.md`
- 拓扑一致性判断：`references/topology-validation.md`
- 最终输出格式：`references/output-format.md`
