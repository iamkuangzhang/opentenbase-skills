# 输出格式

最终回复建议使用以下结构：

```text
摘要
- 状态：
- 主机：
- 用户：
- OpenTenBase：
- 检测置信度：
- server_version：
- psql_version：
- postgres_binary_version：
- pg_config_version：
- 管理工具：
- 可连接 CN：
- 拓扑：
- 一致性：
- 是否允许写操作：false

VERIFIED
- ...

DOCUMENTED
- ...

UNVERIFIED
- ...

警告
- ...

已保存证据
- ...

下一步
- ...
```

无法确认时写 `unknown`，不要猜。

必须提到具体证据文件。不要把聊天记录当成证据。
