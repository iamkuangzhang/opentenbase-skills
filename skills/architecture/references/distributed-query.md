# 分布式查询

## DOCUMENTED

OpenTenBase 不能完全按单机 PostgreSQL 理解。单机 PostgreSQL 中 SQL 通常只在一个数据库实例内规划和执行；OpenTenBase 中，用户连接 CN 后，CN 需要结合表分布和节点拓扑，把一条 SQL 拆解、下发到 DN，并汇总结果。

## SQL 基本流向

1. 用户连接 CN。
2. CN 解析 SQL。
3. CN 根据元数据、表分布和查询条件生成分布式执行计划。
4. CN 将可下推的任务发送到相关 DN。
5. DN 执行本地数据访问。
6. CN 汇总结果并返回给用户。

## VERIFIED

- 当前环境只读验证了可连接 CN 和 `pgxc_node` 拓扑。

## UNVERIFIED

- 当前 evidence 未验证复杂 join、聚合、下推计划或跨 DN 数据重分布行为。

## 使用提醒

当分析 SQL 性能或插件兼容性时，不要只问“SQL 在 PostgreSQL 能不能跑”，还要问：

- SQL 是否依赖单机可见性。
- 函数是否能被安全下推。
- 数据是否需要跨 DN 重分布。
- 结果是否需要 CN 汇总。
