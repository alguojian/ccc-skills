# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This repository contains a Claude Code skill for Chinese longform writing. The skill is designed to help with full articles, outlines, rewrites, continuations, and reviews of Chinese longform content, especially公众号、个人博客、观点稿、体验稿、方法论长文.

The repository is content/configuration-oriented rather than an application codebase. There is currently no package manifest, build system, lint configuration, or automated test runner in the tracked files.

## Common commands

- Inspect tracked files: `git ls-files`
- Check working tree state: `git status --short`
- Review local changes: `git diff`

No verified build, lint, or test commands exist in this repository at the moment. Do not invent npm, Python, or other toolchain commands unless a future change adds the corresponding config files.

## Architecture

- `ccc-write/SKILL.md` is the main skill definition. It contains the skill metadata, routing rules, writing constraints, output modes, style principles, reference-file usage rules, and final self-check criteria.
- `ccc-write/references/content_methodology.md` is supporting methodology material for topic selection, HKR evaluation, content archetypes, pacing, and creative case framing.
- `ccc-write/references/style_examples.md` is a style reference library for openings, transitions, knowledge insertion, self-deprecation, investigative writing, character sketches, cultural elevation, humor, endings, and AI-vs-human rewrite examples.

The main skill intentionally instructs agents not to load all references by default. Future edits should preserve that architecture: keep operational rules and routing in `SKILL.md`, and keep large examples or methodology material in `references/` for on-demand reading.

## Skill behavior to preserve

Key constraints from `ccc-write/SKILL.md` that should remain central when editing the skill:

- The skill helps the user write; it must not impersonate a specific real creator or inherit identity markers from reference material.
- Route each request before writing: `full_article`, `outline`, `rewrite`, `continue`, or `review`.
- If the user has not provided enough real material for first-hand experience, testing, dialogue, emotions, or concrete scenes, downgrade to an outline, missing-material list, interview questions, test plan, or article skeleton instead of fabricating details.
- Separate confirmed facts, judgments, and associations. High-risk facts such as dates, prices, model capabilities, quotes, statistics, product details, and historical claims should be verified when possible or phrased cautiously when not verified.
- Default tone is `standard`; use `mild` or `raw` only when the task or source draft calls for it.
- References are for learning structure, rhythm, transitions, and observation methods, not for copying sentences, identities, fixed signatures, personal experiences, or recognizable creator-specific mannerisms.

## Editing guidance

When changing the skill, update `ccc-write/SKILL.md` for behavior that should always apply. Put expanded examples, long style samples, or reusable methodology into files under `ccc-write/references/` and keep `SKILL.md` as the concise orchestration layer.