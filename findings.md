# 关键发现

## 现有 skill 分工

- `ccc-write` 负责长文写作、续写、扩写、改写、提纲与审稿
- `ccc-no-ai` 负责对已有中文文章做去 AI 味、自然化和笔气贴合

## 新 skill 已确认的边界

- 名称使用 `ccc-write-no-ai`
- 这是一个明确触发的专项 skill，不是默认入口
- `full_article`、`rewrite`、`continue` 为双阶段
- `outline`、`review` 为单阶段

## 元数据约束

- `agents/openai.yaml` 的字符串值需要加引号
- `interface.default_prompt` 需要显式提到 `$ccc-write-no-ai`
- `short_description` 应简短、面向 UI 展示

## 实现约束

- 新 skill 使用 `skill-creator` 的 `init_skill.py` 初始化
- 当前第一版不新增 `references/`、`scripts/`、`assets/`

## 实现过程中的额外发现

- `init_skill.py` 对 `short_description` 有 25 到 64 个字符的长度限制
- Windows 下运行 `generate_openai_yaml.py` 读取中文 `SKILL.md` 时，需要设置 `PYTHONUTF8=1`，否则会按 `gbk` 解码并报错
- `quick_validate.py` 在 UTF-8 环境下通过，说明新 skill 的 frontmatter 和目录结构有效
