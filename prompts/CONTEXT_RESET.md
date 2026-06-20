# 上下文重置提示

如果发生上下文丢失或交接：

1. 先停止编辑，停止继续运行命令。
2. 重新阅读 `PROJECT_BRIEF.md`、`CURRENT_STATE.md`、`SAFETY.md`、`TEST_ENV.md` 和当前技能。
3. 查看 `git status` 和 `git diff`。
4. 总结：
   - `VERIFIED` 事实
   - `DOCUMENTED` 事实
   - `UNVERIFIED` 事实
   - 当前修改
   - 最新证据
5. 在状态恢复前，不要执行写操作。
6. 除非证据缺失或过期，不要重复执行昂贵或有风险的测试。
7. 未验证前，不要把普通 PostgreSQL 经验直接套用到 OpenTenBase。
