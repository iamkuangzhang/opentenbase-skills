# CN、DN、GTM

## DOCUMENTED

- CN，即 Coordinator，是用户通常连接的 SQL 入口。
- DN，即 DataNode，负责存储和执行被分发到数据节点上的实际数据访问任务。
- GTM 负责全局事务相关协调，是分布式一致性语义中的关键组件。
- 用户通常连接 CN，而不是直接连接 DN，因为 CN 承担 SQL 解析、计划、路由、结果汇总等入口职责。

## VERIFIED

- 在当前测试环境中，`pgxc_node` 已只读验证返回 2 个 CN 和 2 个 DN。
- 证据位于 `dev/evidence/command-output/2026-06-21-074548-system-entry-130.json` 和 `dev/evidence/command-output/2026-06-21-074549-system-entry-132.json`。

## UNVERIFIED

- 当前 evidence 未验证 GTM 的完整主备状态。
- 当前 evidence 未证明所有节点都在业务压力下健康，只证明可读取拓扑和至少一个 CN 可连接。

## 解释要点

一个 CN 可连接不等于整个集群完全正常。原因包括：

- 其他 CN 可能不可连接。
- 某些 DN 可能不可达或状态异常。
- 配置文件、进程、监听端口和 `pgxc_node` 可能不一致。
- 事务协调组件异常可能影响写入或跨节点事务。
