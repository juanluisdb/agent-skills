# Sessions And Context

Use this reference when the task touches session persistence, branching, compaction, prompts, or context management.

## Session Model

- Pi sessions are tree-structured JSONL files, not flat transcripts.
- Each entry points to a `parentId`, which enables branching, rewinding, alternate explorations, and summaries of abandoned paths.
- Important entry categories include:
  message entries,
  model/thinking-level changes,
  compaction entries,
  branch summaries,
  custom entries,
  custom messages,
  labels and session metadata.

## Why This Matters

- Review branches, side quests, and reversible exploration are native Pi workflows.
- Product integrations should avoid collapsing everything into one linear chat unless that tradeoff is deliberate.
- Extension and host behavior may depend on branch-aware session semantics.

## Context Assembly

- `AGENTS.md`
  Repo or directory instructions loaded hierarchically from global and project paths.
- `SYSTEM.md`
  Replaces the default system prompt.
- `APPEND_SYSTEM.md`
  Appends to the default system prompt without replacing it.
- Skills
  Loaded on demand through their descriptions and then read as markdown when relevant.
- Prompt templates
  Reusable prompt expansions rather than durable system behavior.
- Extension hooks
  Can inject context, filter history, or implement memory-like behavior.
- Compaction
  Summarizes older context as history grows; this is part of the runtime design, not a bolt-on convenience.

## Guidance

- Prefer reusable knowledge in files and resources over giant repeated bootstrap prompts.
- If you need durable repo conventions, put them in `AGENTS.md` or a skill.
- If you need dynamic or runtime-derived context, use extension hooks.
- If you need a different product abstraction, be explicit about how it maps back to Pi sessions and context.
