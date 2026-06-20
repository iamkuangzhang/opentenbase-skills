# 风险等级

- `read-only`：检查命令和只读 SQL。
- `low-risk`：本地格式整理、总结、证据归档。
- `medium-risk`：可能给系统带来压力或读取大日志的命令，需要明确边界。
- `high-risk`：服务生命周期、配置修改、文件系统写入、数据库写入、节点操作。
- `forbidden-in-system-entry`：首次进入识别阶段禁止执行的高风险操作。
