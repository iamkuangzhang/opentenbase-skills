---
name: opentenbase-architecture
description: >
  用于 AI Agent 解释或判断 OpenTenBase 分布式架构时使用，覆盖 CN、DN、GTM、
  Share-Nothing、分布式查询、分布表、复制表、分布键、数据倾斜、Join 代价和分布式事务。
  Use when an agent needs OpenTenBase architecture knowledge before troubleshooting,
  SQL design, plugin adaptation, or cluster reasoning.
---

# OpenTenBase Architecture

## 触发场景

当用户询问 OpenTenBase 的 CN / DN / GTM、分布式 SQL、表分布、分布式事务，或需要判断“为什么不能按单机 PostgreSQL 理解 OpenTenBase”时，使用本技能。

## 任务目标

帮助 AI Agent 用分布式数据库视角理解 OpenTenBase，并在回答中区分：

- `VERIFIED`：已在当前 OpenTenBase 环境只读 SQL 或命令验证。
- `DOCUMENTED`：来自 OpenTenBase 文档、源码语义、工具帮助或项目可信资料。
- `TDSQL_CANDIDATE`：来自 TDSQL PostgreSQL 资料，可作为理解候选，尚待 OpenTenBase 验证。
- `UNVERIFIED`：推断、类比或当前环境无法验证。

## 标准步骤

1. 先确认用户关心的是组件职责、SQL 路由、表分布、Join、事务，还是插件/SQL 迁移判断。
2. 按需读取 references：
   - `references/cn-dn-gtm.md`
   - `references/distributed-query.md`
   - `references/table-distribution.md`
   - `references/distributed-transaction.md`
3. 不把普通 PostgreSQL 单机结论直接套用到 OpenTenBase。
4. 不把 TDSQL 的 OSS、TStudio、固定路径、固定用户、默认密码、商业组件或版本专属命令写成 OpenTenBase 事实。
5. 如果需要真实验证，只做只读 SQL；需要建表、写入或压测时先请求用户确认。

## 安全边界

本技能只解释架构和做只读验证。禁止自动执行：

- 启停集群
- 修改配置
- 写数据库
- 创建表或插入数据
- 执行插件部署、注册、回滚
- 压测或故障注入

## 可用只读验证

```sql
SELECT 1;
SELECT version();
SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;
```

## 输出要求

回答时把“已验证事实”和“候选知识”分开。尤其是来自 TDSQL 课件的内容，只能标记为 `TDSQL_CANDIDATE`，除非已经通过 OpenTenBase 文档或当前环境验证。
