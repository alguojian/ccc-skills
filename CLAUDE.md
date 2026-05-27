# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This repository contains Claude Code skills for Chinese writing and rewriting.

- `ccc-write` helps with full articles, outlines, rewrites, continuations, and reviews of Chinese longform content, especially公众号、个人博客、观点稿、体验稿、方法论长文.
- `ccc-no-ai` rewrites existing Chinese text to reduce AI-sounding phrasing, template language, and mechanical rhythm while preserving the original meaning.

The repository is content/configuration-oriented rather than an application codebase. There is currently no package manifest, build system, lint configuration, or automated test runner in the tracked files.

## Common commands

- Inspect tracked files: `git ls-files`
- Check working tree state: `git status --short`
- Review local changes: `git diff`

No verified build, lint, or test commands exist in this repository at the moment. Do not invent npm, Python, or other toolchain commands unless a future change adds the corresponding config files.

## Architecture

- `ccc-write/SKILL.md` is the main longform-writing skill definition. It contains skill metadata, routing rules, writing constraints, output modes, style principles, reference-file usage rules, and final self-check criteria.
- `ccc-write/references/content_methodology.md` is supporting methodology material for topic selection, HKR evaluation, content archetypes, pacing, and creative case framing.
- `ccc-write/references/style_examples.md` is a style reference library for openings, transitions, knowledge insertion, self-deprecation, investigative writing, character sketches, cultural elevation, humor, endings, and AI-vs-human rewrite examples.
- `ccc-no-ai/SKILL.md` is the rewrite-focused skill definition for removing AI-sounding phrasing from existing Chinese article text. It should stay centered on rewrite boundaries, output minimalism, article-shape cleanup, voice-sample matching, Chinese-pattern diagnosis, scene adaptation, and preserving meaning.
- `ccc-no-ai/agents/openai.yaml` stores UI metadata for the `ccc-no-ai` skill.
- `ccc-no-ai/references/chinese_ai_patterns.md` is a focused Chinese pattern library for diagnosing template language, report-style structure, empty uplift, and other common AI tells in Chinese prose.
- `ccc-no-ai/references/voice_matching.md` documents how to extract a user's writing fingerprint from samples and prioritize that fingerprint during rewrites.
- `ccc-no-ai/references/house_voice_fingerprint.md` stores the repo owner's default Chinese article voice fingerprint so the skill has a stable fallback voice when no fresh sample is provided in the current conversation.
- `ccc-no-ai/references/article_quality_rubric.md` defines the internal quality checks for deciding whether a rewritten Chinese article feels like a real article instead of merely a polished answer.

The longform skill intentionally keeps large examples in `references/` rather than `SKILL.md`. Preserve that split when expanding `ccc-write`. `ccc-no-ai` should likewise keep its main workflow in `SKILL.md` and push detailed Chinese-pattern and voice-matching guidance into `references/`.

## Skill behavior to preserve

Key constraints from `ccc-write/SKILL.md` that should remain central when editing the skill:

- The skill helps the user write; it must not impersonate a specific real creator or inherit identity markers from reference material.
- Route each request before writing: `full_article`, `outline`, `rewrite`, `continue`, or `review`.
- `full_article`, `rewrite`, and `continue` should append the repository's fixed footer verbatim by default unless the user explicitly asks to remove it.
- If the user has not provided enough real material for first-hand experience, testing, dialogue, emotions, or concrete scenes, downgrade to an outline, missing-material list, interview questions, test plan, or article skeleton instead of fabricating details.
- Separate confirmed facts, judgments, and associations. High-risk facts such as dates, prices, model capabilities, quotes, statistics, product details, and historical claims should be verified when possible or phrased cautiously when not verified.
- Default tone is `standard`; use `mild` or `raw` only when the task or source draft calls for it.
- References are for learning structure, rhythm, transitions, and observation methods, not for copying sentences, identities, fixed signatures, personal experiences, or recognizable creator-specific mannerisms.

Key constraints from `ccc-no-ai/SKILL.md` that should remain central when editing the skill:

- The skill is for rewriting existing Chinese text, not for writing from scratch.
- Preserve meaning, stance, and required information while reducing template language and AI-like rhythm.
- If the user provides their own writing sample, prefer matching that sample's sentence rhythm, paragraph density, transitions, and tone over applying a generic polished style.
- If the current conversation does not include a new sample but the request clearly continues the repository owner's Chinese article voice, use the stored house voice fingerprint as the fallback style reference.
- For article-shaped content, repair listified or fragmented AI formatting before doing finer-grained style work.
- Default to outputting only the final rewritten text unless the user explicitly asks for explanations or comparisons.
- Never invent facts, data, examples, experiences, or quotes to make text feel more human.
- Adapt tone to the source context without turning "human" into slang, affectation, or deliberate mistakes.
- Run an internal second-pass audit so the output does not merely swap old AI cliches for a newer "smooth rewrite" template.

## Editing guidance

When changing a skill, update its `SKILL.md` for behavior that should always apply. Put expanded examples, long style samples, or reusable methodology into files under `references/` only when the skill clearly benefits from them, and keep each `SKILL.md` as the concise orchestration layer.
