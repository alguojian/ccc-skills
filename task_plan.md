# 任务计划

## 目标

在当前仓库中创建一个新的 `ccc-write-no-ai` skill，把 `ccc-write` 和 `ccc-no-ai` 组合成一个明确触发的两阶段写作入口。

## 阶段

| 阶段 | 状态 | 说明 |
|---|---|---|
| 1 | complete | 梳理现有 skill、确认边界、完成设计讨论 |
| 2 | complete | 编写并确认中文设计文档 |
| 3 | complete | 初始化新 skill 骨架并编写 `SKILL.md` |
| 4 | complete | 生成并检查 `agents/openai.yaml` |
| 5 | complete | 运行校验并做人工检查 |
| 6 | in_progress | 汇总结果并向用户说明 |

## 关键约束

- 新 skill 只在用户明确要“两段式处理”时触发
- `full_article`、`rewrite`、`continue` 走第二阶段
- `outline`、`review` 不走第二阶段
- 不复制两边已有的长规则，保持编排层轻量
- 保留 `ccc-write` 的固定尾注规则

## 已知风险

- 触发描述如果写得太宽，可能会抢走 `ccc-write` 或 `ccc-no-ai` 的默认入口
- 第二阶段边界如果写得不够死，容易被理解成可改立场或补事实
