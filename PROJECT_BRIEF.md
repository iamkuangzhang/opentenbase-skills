# 项目说明

目标：帮助 AI Agent 第一次进入 OpenTenBase 服务器时，在执行任何运维动作之前，先识别环境、拓扑、管理工具、风险边界和安全下一步。

## 语言约定

本项目以中文作为文档、技能说明、提示词和评测内容的主要语言；目录名、技能名、程序代码、命令参数、状态常量和结构化数据字段使用英文。OpenTenBase 专有名词和工具名称保留原文，必要时在首次出现时提供中文解释。

## 事实状态标签

- `VERIFIED`：已在当前真实环境测试，并保存证据。
- `DOCUMENTED`：来自官方文档、源码或可信资料，但尚未在当前环境验证。
- `UNVERIFIED`：推断、不可用、不明确，或仍需验证。

不要把 `DOCUMENTED` 或 `UNVERIFIED` 写成 `VERIFIED`。

## 路线图

1. `system-entry`
2. `architecture`
3. `cluster-operations`
4. `basic-usage`
5. `diagnostics`
6. `extension-management`
7. `plugin-ctl`

当前阶段只完成 `opentenbase-system-entry`。
