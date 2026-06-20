# 危险命令

`opentenbase-system-entry` 阶段禁止执行：

```text
init all
clean all
kill all
failover
start all
stop all
remove node
add node
CREATE
ALTER
DROP
TRUNCATE
INSERT
UPDATE
DELETE
COPY FROM
CREATE EXTENSION
```

同样禁止：

- 修改配置文件。
- 修改 GUC。
- 删除数据目录。
- 使用 `sudo` 绕过权限。
- 读取私钥、密码、token 或无关敏感文件。
