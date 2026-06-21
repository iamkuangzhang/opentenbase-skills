# 发现清单

分小组运行命令，并保存原始输出。

## 1. OS 身份

```bash
whoami
id
hostname
hostname -I
pwd
date
uname -a
```

## 2. 工具发现

```bash
command -v opentenbase_ctl || true
command -v pgxc_ctl || true
command -v psql || true
command -v postgres || true
command -v pg_config || true
type -a opentenbase_ctl 2>/dev/null || true
type -a pgxc_ctl 2>/dev/null || true
type -a psql 2>/dev/null || true
type -a pg_config 2>/dev/null || true
```

## 3. 版本

使用已发现的二进制路径。不要假设 `PATH` 一定指向当前活跃集群。

```bash
psql --version
pg_config --version
postgres --version
```

## 4. 进程

优先使用进程过滤：

```bash
ps -ef | grep -E '[p]ostgres|[g]tm|[p]gxc|[o]pentenbase'
pgrep -a postgres || true
pgrep -a gtm || true
```

## 5. 端口

```bash
ss -lntp
```

如果权限导致进程名不可见，需要记录这个限制。

## 6. 有边界的配置搜索

只搜索已知目录：

```bash
find "$HOME" -maxdepth 4 \( -name 'opentenbase_config.ini' -o -name 'config.ini' -o -name 'pgxc_ctl.conf' \) -type f 2>/dev/null
find /data/opentenbase -maxdepth 5 \( -name 'opentenbase_config.ini' -o -name 'config.ini' -o -name 'pgxc_ctl.conf' \) -type f 2>/dev/null
find /opt -maxdepth 5 \( -name 'opentenbase_config.ini' -o -name 'config.ini' -o -name 'pgxc_ctl.conf' \) -type f 2>/dev/null
```

不要执行无边界的 `find /`。

## 7. 数据库只读检查

只能使用显式参数或配置文件中发现的 CN host/port 候选。

不要根据端口号是否以 `3` 开头猜测 CN。监听端口只能作为一致性证据，不能单独作为 CN 候选。

```bash
PGCONNECT_TIMEOUT=5 psql -h <host> -p <port> -d postgres -U <user> -Atc 'SELECT 1;'
PGCONNECT_TIMEOUT=5 psql -h <host> -p <port> -d postgres -U <user> -Atc 'SELECT version();'
PGCONNECT_TIMEOUT=5 psql -h <host> -p <port> -d postgres -U <user> -Atc "SELECT node_name,node_type,node_host,node_port FROM pgxc_node ORDER BY node_name;"
```

脚本支持以下数据库连接参数：

```bash
--db-user <user>
--database <database>
--cn-host <host>
--cn-port <port>
--connect-timeout <seconds>
--no-database
```

`--cn-host` 和 `--cn-port` 必须同时提供。
