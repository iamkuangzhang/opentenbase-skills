# CN、DN、GTM

## 核心概念

- CN，即 Coordinator，是应用通常连接的 SQL 入口。
- DN，即 DataNode，负责存储数据并执行被下发到数据节点上的本地访问任务。
- GTM 负责全局事务相关协调，是分布式一致性语义中的关键组件。

## 协作关系

典型查询路径是：应用连接 CN，CN 解析 SQL、生成分布式执行计划，把可下推任务发送到 DN，DN 返回局部结果，CN 汇总后返回给应用。

这意味着 OpenTenBase 不能只按单机 PostgreSQL 理解：SQL 能在单机执行，不代表它在分布式表、跨 DN Join、分布式事务或插件函数下推场景中成本和语义完全相同。

## 应用为什么通常连接 CN

CN 承担 SQL 入口、解析、计划、路由、结果汇总等职责。应用直接连接 DN 通常无法获得完整的分布式 SQL 语义，也可能绕开 CN 的元数据和执行协调。

## 一个 CN 可连接不等于集群完全正常

原因包括：

- 其他 CN 可能不可连接。
- 某些 DN 可能不可达或状态异常。
- 配置文件、进程、监听端口和 `pgxc_node` 可能不一致。
- GTM 或事务协调组件异常可能影响写入或跨节点事务。

## Agent 判断影响

- 不要只凭 `SELECT 1` 成功就判断集群健康。
- 判断可用性时同时看 CN、DN、GTM、端口、进程和 `pgxc_node`。
- 对插件、SQL 或迁移问题，先问它是否依赖分布式执行、跨节点数据访问或事务协调。

## VERIFIED

- 当前 evidence 曾通过只读 `pgxc_node` 查询验证测试环境存在 CN/DN 拓扑。
- `dev/evidence/command-output/2026-06-21-074548-system-entry-130.json` 和 `dev/evidence/command-output/2026-06-21-074549-system-entry-132.json` 保存了相关环境识别证据。

## TDSQL_CANDIDATE

- TDSQL PostgreSQL 资料也采用 CN/DN/GTM 组件视角描述分布式架构，可作为理解参考。
- TDSQL 资料中“操作通常连接 CN”的开发习惯可作为候选判断，但具体 OpenTenBase 环境仍应以实际连接信息、文档和 `pgxc_node` 为准。

## UNVERIFIED

- 当前 evidence 未验证 GTM 主备完整状态。
- 当前 evidence 未证明所有节点在业务压力下健康。
