---
name: opentenbase-architecture
description: >
  用于 AI Agent 解释或判断 OpenTenBase 分布式架构时使用，覆盖 CN、DN、GTM、
  分布式查询、表分布、复制表、分布键、数据倾斜和分布式事务。Use when an agent
  needs OpenTenBase architecture knowledge before troubleshooting, SQL design,
  plugin adaptation, or cluster reasoning.
---

# OpenTenBase Architecture

## 触发场景

当用户询问 OpenTenBase 的 CN / DN / GTM、分布式 SQL、表分布、分布式事务，或需要判断“为什么不能按单机 PostgreSQL 理解 OpenTenBase”时，使用本技能。

## 任务目标

帮助 AI Agent 用分布式数据库视角理解 OpenTenBase，并在回答中区分：

- `VERIFIED`：当前环境只读 SQL 或命令验证过。
- `DOCUMENTED`：来自项目文档、源码语义或通用 OpenTenBase 知识，但本次未验证。
- `UNVERIFIED`：推断或当前环境无法验证。

## 标准步骤

1. 如果需要确认当前集群拓扑，先使用 `opentenbase-system-entry` 做只读识别。
2. 解释架构问题时，优先确认用户关心的是 CN、DN、GTM、SQL 路由、表分布还是事务。
3. 按需读取 references：
   - `references/cn-dn-gtm.md`
   - `references/distributed-query.md`
   - `references/table-distribution.md`
   - `references/distributed-transaction.md`
4. 不把普通 PostgreSQL 单机结论直接套用到 OpenTenBase。
5. 对无法在当前环境验证的内容标记 `DOCUMENTED` 或 `UNVERIFIED`。

## 安全边界

本技能只解释架构和做只读验证。禁止启停集群、修改配置、写数据库、创建表、插入数据或执行插件操作。

## 结果验证

如果需要真实验证，只允许使用：

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## 停止并请求确认的条件

如果用户要求创建表、写入数据、修改分布策略、启停节点或执行压测，停止并请求明确确认或切换到其他技能。
