---
title: ccc-write-no-ai design
date: 2026-05-27
status: approved-in-chat
---

# ccc-write-no-ai

## Goal

Create a new explicit-use skill that combines the current `ccc-write` and `ccc-no-ai` workflows.

The new skill should:

- act as a clear two-pass entry point for Chinese longform writing tasks
- first produce the requested draft using the `ccc-write` workflow
- then run a second pass using the `ccc-no-ai` workflow when the output is article-shaped prose
- keep the orchestration layer concise instead of duplicating the full rule sets from both existing skills

The new skill should not replace either existing skill as the default entry point.

## User Intent Boundary

This skill is for cases where the user clearly wants a combined workflow such as:

- write this article and then smooth out the AI flavor
- continue this draft and then make it sound more natural
- rewrite this piece and then do one more humanizing pass

This skill should not trigger for generic requests like:

- write an article
- give me an outline
- help me remove AI flavor from this draft

Those generic cases should continue to route to `ccc-write` or `ccc-no-ai` directly.

## Proposed Skill Name

Use `ccc-write-no-ai` as the skill folder name unless implementation uncovers a naming conflict.

Why this name:

- it stays consistent with the existing `ccc-*` naming scheme
- it is explicit about combining writing and de-AI polishing
- it is clear enough to support explicit triggering without sounding like a default entry point

## Workflow Shape

The new skill will be a semi-unified orchestrator.

It will define:

- trigger conditions
- routing behavior
- pass-one versus pass-two rules
- final output behavior
- the boundary between orchestration rules and delegated rules

It will not inline the full content of `ccc-write` or `ccc-no-ai`.

## Route Matrix

Retain the same five task routes already used by `ccc-write`:

- `full_article`
- `outline`
- `rewrite`
- `continue`
- `review`

Execution by route:

- `full_article`: run `ccc-write` pass, then run `ccc-no-ai` pass on the produced article
- `rewrite`: run `ccc-write` rewrite pass, then run `ccc-no-ai` pass on the produced article
- `continue`: run `ccc-write` continuation pass, then run `ccc-no-ai` pass on the produced article
- `outline`: run only the `ccc-write` outline flow and return directly
- `review`: run only the `ccc-write` review flow and return directly

Reasoning:

- the second pass is only useful when the first pass outputs article prose
- `outline` and `review` are not final prose deliverables, so forcing a de-AI rewrite would either distort the format or add no value

## Pass One Rules

Pass one should follow the existing `ccc-write` rules for:

- route selection
- material sufficiency checks
- downgrade behavior when firsthand material is missing
- fact-risk control
- tone control
- output shape for each route

The new skill should explicitly state that it inherits those rules rather than restating them in full.

## Pass Two Rules

Pass two should follow the existing `ccc-no-ai` rules for:

- article-shape cleanup
- voice matching when a user sample exists
- removing templated phrasing, report cadence, and mechanical transitions
- preserving meaning, stance, and required information
- avoiding invented facts, scenes, emotions, or examples

The new skill should explicitly limit pass two to cleanup and naturalization. It must not:

- change the thesis
- add new claims
- move the piece into a new structure unless needed for readability
- strip out required footer behavior inherited from `ccc-write`

## Footer Behavior

For `full_article`, `rewrite`, and `continue`, keep the current `ccc-write` default footer behavior unchanged.

Implementation rule:

- append the fixed footer during the first pass if the route normally requires it
- allow the second pass to smooth the body text without deleting or paraphrasing the fixed footer

## Output Rules

Default output:

- return only the final result
- do not show the intermediate first-pass draft
- do not include a process log
- do not include rewrite notes unless the user explicitly asks for them

If the user asks for comparison or explanation, the skill may provide:

- first-pass versus second-pass comparison
- a short note on what changed
- a brief diagnosis of remaining AI-sounding spots

## Reference Strategy

Keep the new `SKILL.md` lean.

Do not copy large guidance blocks from the existing skills.

Instead:

- point to `ccc-write` for longform writing rules and references
- point to `ccc-no-ai` for anti-AI rewrite rules and references
- only add new reference files if orchestration itself needs reusable examples or edge-case guidance

Expected initial implementation:

- no new `references/` files
- no new `scripts/` files
- include `agents/openai.yaml`

## File Layout

Planned new directory:

```text
ccc-write-no-ai/
├── SKILL.md
└── agents/
    └── openai.yaml
```

No extra docs, readmes, or placeholder resource folders should be created unless implementation reveals a concrete need.

## Frontmatter And Triggering

The `SKILL.md` frontmatter description should make these points explicit:

- it combines article writing with a second humanizing pass
- it is for Chinese longform tasks
- it is best for users who clearly want both stages in one request
- it supports `full_article`, `rewrite`, and `continue` as two-pass outputs
- it supports `outline` and `review` as single-pass outputs

The description should also make clear what the skill is not for:

- not the default generic writing entry point
- not a standalone de-AI rewrite skill for already-written drafts unless the user also wants the writing-stage workflow

## Validation Plan

Validation for the initial version should include:

1. Run skill-folder validation on the finished skill.
2. Manually inspect the trigger description for explicitness.
3. Manually inspect the route matrix to confirm only three routes use the second pass.
4. Check that the output rules do not expose intermediate drafts by default.
5. Check that footer preservation is stated clearly.

## Non-Goals

The first version should not:

- merge the two existing skills into one canonical default skill
- change the behavior of `ccc-write`
- change the behavior of `ccc-no-ai`
- add automation, scripts, or external tools
- create a new house style system

## Open Implementation Notes

Implementation should prefer concise imperative instructions in `SKILL.md`.

If wording becomes repetitive, bias toward:

- one short orchestration rule in the new skill
- one explicit pointer to the existing source skill

Instead of:

- restating full downstream guidance
