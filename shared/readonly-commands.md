# 只读命令

允许的命令示例：

```bash
whoami
id
hostname
hostname -I
pwd
date
uname -a
command -v <name>
type -a <name>
readlink -f <path>
ls -l <path>
stat <path>
find <known-root> -maxdepth 4 -name <pattern>
ps -ef
pgrep -a <pattern>
ss -lntp
netstat -lntp
cat <known-config>
head -n 100 <known-log>
tail -n 100 <known-log>
```

只读 SQL 示例：

```sql
SELECT 1;
SELECT version();
SELECT current_database();
SELECT current_user;
SELECT node_name, node_type, node_host, node_port FROM pgxc_node ORDER BY node_name;
```
