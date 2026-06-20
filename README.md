# OpenTenBase Agent Skills

这是一个面向 AI Agent 的 OpenTenBase 技能包项目。

当前第一阶段只完成一个技能：

- `opentenbase-system-entry`：当 AI Agent 第一次进入一台可能已经安装 OpenTenBase 的服务器时，执行只读环境识别。

本项目以中文作为文档、技能说明、提示词和评测内容的主要语言；目录名、技能名、程序代码、命令参数、状态常量和结构化数据字段使用英文。OpenTenBase 专有名词和工具名称保留原文，必要时在首次出现时提供中文解释。

## 当前边界

`opentenbase-system-entry` 只负责识别环境，不负责运维操作。

允许：

- 识别 OpenTenBase 版本和安装目录。
- 识别 `opentenbase_ctl`、`pgxc_ctl`、`psql`、`postgres`、`pg_config`。
- 查看 GTM / CN / DN 相关进程和监听端口。
- 尝试连接可达 CN，并只读查询 `pgxc_node`。
- 输出风险、未知项和证据文件。

禁止：

- 启动、停止、初始化、清理、切换、扩缩容 OpenTenBase 集群。
- 修改配置文件。
- 执行数据库写操作。
- 部署、注册、回滚插件。
- 读取私钥、密码、token 等无关敏感信息。

## 目录

```text
opentenbase-agent-skills/
├── skills/system-entry/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/discover_environment.py
├── shared/
├── prompts/
├── evals/
└── evidence/
```

## 快速验证

```bash
python skills/system-entry/scripts/discover_environment.py --json
```

脚本的人类可读输出使用中文；JSON 字段名保持英文，方便后续评测、脚本和 Agent 工具消费。
