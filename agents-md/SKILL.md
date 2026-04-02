---
name: agents-md
description: Write or improve `AGENTS.md` files for coding agents. Use when creating, reviewing, or tightening repo instruction files so they stay short, specific, actionable, and repo-specific. Not for general README or end-user docs.
---

# Write Effective AGENTS.md Files

Use this skill when asked to create, review, or refine an `AGENTS.md`.

## Goal

Produce an `AGENTS.md` that helps an agent work correctly in this repo without burying important rules in boilerplate.

## Example Requests

- "Draft an `AGENTS.md` for this repository."
- "Review our `AGENTS.md` and make it shorter and more useful."
- "Tighten this `AGENTS.md` so the agent stops missing our workflow rules."

## Mindset

- There is no canonical template.
- Treat sections as optional building blocks, not required headings.
- Use medium/high freedom: adapt the structure to the repo, team habits, and risk level.
- Keep only instructions the agent cannot reliably infer from code, tooling, or standard conventions.
- Prefer one concrete command, rule, or example over several abstract sentences.

## What Good AGENTS.md Files Usually Do

- Put recurring commands early.
- Make verification explicit.
- Capture repo-specific conventions and workflow rules.
- Define boundaries, approval points, and things the agent must not touch.
- Point to deeper docs instead of duplicating them.
- Stay short enough that important rules remain visible.

## Common Sections

Common sections often include Commands, Verification, Project Structure, Conventions, Workflow, Boundaries, References, etc...

Use only the sections that materially help. Merge, rename, reorder, or skip sections freely.

## Writing Process

1. Inspect the repo before drafting. Look for the actual commands, tools, layouts, and repeated pain points.
2. Identify what the agent truly needs help with. Focus on rules that are easy to miss or hard to infer.
3. Draft compact instructions in bullets or short sections.
4. Trim aggressively. If a line would not change agent behavior, cut it.
5. Check whether the file tells the agent how to verify success, when to ask first, and what to avoid.

## Include

- Exact commands for install, lint, test, build, dev, deployment checks, etc...
- Verification steps the agent can run on its own
- Repo-specific conventions that differ from defaults
- Important directory guidance when it changes how the agent should work
- Workflow rules around branches, commits, pull requests, reviews, approvals, etc...
- Boundaries around secrets, generated files, migrations, infra, vendor code, or risky areas
- Links or references to deeper docs when the detail does not belong inline

## Avoid

- Generic advice like "write clean code" or "follow best practices"
- Long tutorials or architecture essays
- File-by-file inventories of the whole repo
- Restating conventions the agent can infer by reading nearby code
- Frequently changing facts that are better discovered dynamically
- Rigid section lists that force filler content

## Review Checklist

When reviewing an existing `AGENTS.md`, check for:

- Missing commands the agent needs repeatedly
- Missing validation or test expectations
- Missing boundaries or approval points
- Guidance that is too vague to follow or verify
- Guidance that is obvious, redundant, or too long
- Root-level instructions that should live closer to a subdirectory instead

## Heuristics

- If the file is getting long, move detail into referenced docs instead of expanding inline.
- If a rule only matters for one area of the repo, prefer a nested `AGENTS.md` near that code.
- If a workflow is specialized but not always relevant, consider a skill instead of loading it every session.
- If the agent keeps missing a rule, make the wording sharper or shorten the surrounding file so the rule stands out.

## Output Standard

The final `AGENTS.md` should feel specific to the repository, easy to scan, and immediately usable by an agent. It should read like working instructions, not like policy prose or documentation filler.
