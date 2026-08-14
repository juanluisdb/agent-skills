---
name: skill-craft
description: Author or revise an AI-agent skill. Use to create, scaffold, or build a new skill, or to diagnose, improve, audit, or prune an existing one (e.g. "the skill isn't triggering", "this skill is too long").
---

# Craft a Skill

A skill exists to make an agent's *process* predictable — the same way every run, not the same output. Every choice below serves that.

This skill has two branches. Pick one, then both converge on the shared **Principles** and a **Pruning pass** before you finish.

- **Author** — creating a new skill from scratch → start at *Author a skill*.
- **Revise** — improving, auditing, debugging, or pruning an existing skill → start at *Revise a skill*.

## Author a skill

### 1. Gather requirements

Extract what you can from the conversation and context first; only ask for what's genuinely missing:

1. **Name** — lowercase, hyphens only (e.g. `review-pr`). Use `$ARGUMENTS` if provided.
2. **What it does** — one sentence.
3. **Trigger phrasing** — 2-3 realistic ways the need shows up in user language. This is authoring input for the description; do not dump it into the body.
4. **Output** — what the agent should produce or accomplish.
5. **Edge cases / constraints** — unusual inputs, failure cases, hard rules.
6. **Invocation** — must the agent fire it on its own (or must another skill reach it)? If it only ever fires when you type its name, make it user-invoked. See *Invocation*.
7. **Scope** — global (`~/.agents/skills/<name>/`), project (`.agents/skills/<name>/`), or a path the user gives.

### 2. Write SKILL.md

Decide the kind, then apply the *Principles* below:

- **Reference skill** — conventions, patterns, or domain knowledge the agent applies while doing other work.
- **Task/workflow skill** — a step-by-step procedure for a repeatable action.

Write the frontmatter and body, then run the *Pruning pass*.

## Revise a skill

### 1. Read the whole skill

Read `SKILL.md` and any linked files. Note its kind, its branches, and what each line is doing.

### 2. Diagnose against the failure modes

Walk the skill against the failure modes in the *Pruning pass* and the *Principles*. The failure-mode list is your diagnostic checklist — most edit requests map to one:

- not triggering → *Description* / *Leading words*
- too long → **sprawl** (disclose reference; split branches)
- rushes or skips a step → **premature completion** (sharpen the completion criterion)
- overdoes it — loads everything, verifies everything, grinds past usefulness → **over-steer**
- says nothing new → **no-op**
- repeats itself → **duplication**
- stale, no-longer-true lines → **sediment**

### 3. Apply targeted edits

Change only what the diagnosis calls for: smallest edit that fixes the cause, single source of truth. Then run the *Pruning pass* over the result.

## Principles (both branches)

### Invocation

Two choices, each with a cost:

- **Model-invoked** — keeps a `description`; the agent can fire it autonomously and other skills can reach it. Costs **context load** — the description sits in the context window every turn. This is the default.
- **User-invoked** — set `disable-model-invocation: true`; only the user typing its name reaches it. Zero context load, but costs **cognitive load** — the user must remember it exists. The `description` becomes a human-facing one-liner.

Pick model-invocation only when the agent must reach the skill on its own. When user-invoked skills pile up past what you can remember, a **router skill** (one user-invoked skill that names the others and when to reach for each) cures it.

### Description

Drives discovery — the agent reads it to decide when to load the skill. Third person, under ~250 characters (longer gets truncated).

- **Front-load the leading word** — the description is where it does its invocation work.
- **One trigger per branch** — synonyms that rename a single branch are duplication; keep only genuinely distinct triggers.
- State what it does *and* when to use it, in realistic user phrasing. Name boundaries (when **not** to use it) if it would otherwise misfire on adjacent tasks.

If the user asks to prevent automatic invocation, add `disable-model-invocation: true`.

### Leading words

A **leading word** is a compact concept already living in the model's pretraining (e.g. *lesson*, *tracer bullets*, *red*) that the agent thinks with while running the skill. Repeated as a token, it anchors a whole region of behaviour in the fewest tokens by recruiting priors the model already holds.

It serves predictability twice. In the body it anchors *execution*: the agent reaches for the same behaviour every time the word appears. In the description it anchors *invocation*: when the same word lives in your prompts, docs, and code, the agent links that shared language to the skill and fires it more reliably.

Reach for an existing word before coining one — a made-up word recruits no priors, so you pay its definition in tokens. Hunt restated phrases and collapse them ("fast, deterministic, low-overhead" → *tight*).

### Prescriptiveness

The most important authoring decision: match the level of freedom to the task's fragility.

- **High freedom** — multiple valid approaches, context-dependent (code review, research, analysis). Give direction, not steps.
- **Medium freedom** — a preferred pattern with acceptable variation (reports, structured output). Provide adaptable templates.
- **Low freedom** — fragile, side-effecting, order-critical (deploys, migrations). Give exact steps to run in sequence.

The analogy: a narrow bridge over cliffs needs exact guardrails (low freedom); an open field needs only a direction (high freedom).

**Prescribe the process, not the pressure.** Low freedom encodes an order the task genuinely requires. Emphasis whose only job is to force compliance — caps-lock imperatives, a rule restated at every step, "if in doubt, do X" blanket nudges — is not prescriptiveness, it's distrust, and it backfires as *over-steer* (see the Pruning pass). If a step matters, say so once, calmly, with the reason.

### Effective content

- **The agent is already smart.** Only include what it doesn't know — your patterns, conventions, constraints, non-obvious rules. Don't explain general programming concepts.
- **Give the reason with the rule.** A rule carrying its motivation generalizes to cases you didn't enumerate; a bare imperative doesn't.
- **Say what to do, not what to avoid.** "Write flowing prose" lands better than "don't use bullets"; reach for a negative only when the boundary itself is the point.
- **Never ask the agent to echo its internal reasoning as output.** "Show your thinking" instructions produce refusals or filler; ask for the conclusion and the evidence instead.
- **Be concrete enough to verify.** "Use 2-space indentation" beats "format code properly." If you couldn't check whether the agent followed it, it's too vague.
- **Completion criteria.** End each step on a checkable, exhaustive "done" condition ("every modified model accounted for", not "produce a change list"). A vague bound invites premature completion.
- **Structure for scanning.** Headers and bullets over dense paragraphs.

### Information hierarchy & supporting files

Rank content by how immediately the agent needs it: in-skill steps, then in-skill reference, then **disclosed** reference — a linked file reached by a context pointer, loaded only when needed. **Progressive disclosure** (pushing reference into a linked file) keeps `SKILL.md` legible. The test is branching: inline what every branch needs; disclose what only some branches reach. A context pointer's *wording*, not its target, decides how reliably it loads.

Add folders only to solve repeated pain:

- **`scripts/`** — deterministic command sequences that would otherwise be rewritten.
- **`references/`** — detailed docs or schemas loaded on demand.
- **`assets/`** — templates or files the agent uses in its output.
- **`examples/`** — when the quality bar is easier shown than told.

Keep references one level deep from `SKILL.md`.

## Pruning pass (run before finishing — both branches)

Hunt each failure mode sentence by sentence; delete aggressively rather than reword:

- **No-op** — a line the model already obeys by default, so you pay tokens to say nothing. Cut it; if it's a weak leading word (*be thorough*), strengthen it (*relentless*) rather than swap technique.
- **Over-steer** — the no-op's harmful sibling: emphasis deployed to force a behavior a plain instruction already gets (caps-lock imperatives, an exhortation restated at every turn, "if in doubt, do X" nudges, mandated re-checks of work the agent verifies anyway). These overshoot — the agent over-loads, over-verifies, over-delegates, or grinds past the point of usefulness. Distinguish deliberate process (a step the workflow requires — keep it, stated once) from pressure (words there only to make the agent comply — cut them).
- **Duplication** — the same meaning in more than one place. Keep one single source of truth. Exception: a slim end-of-file anchor list of one-line pointers back to rules defined in full elsewhere is legitimate — models attend to the end of context — as long as anchors point, never restate.
- **Sediment** — stale lines that no longer bear on the task. Remove.
- **Sprawl** — too long even when every line is live. Disclose reference; split by branch or sequence.
- **Premature completion** — a step that ends on a vague bound. Sharpen its completion criterion first; only split the sequence if the rush persists.

## Confirm & test

1. Show the user the final `SKILL.md`.
2. Explain invocation: `/<skill-name>` if the platform supports it, or describe when it auto-triggers.
3. Suggest a quick test invocation.

## Reference: directory structure

```text
skill-name/
├── SKILL.md           # Required — main instructions
├── references/        # Optional — detailed docs, loaded on demand
├── examples/          # Optional — example outputs
├── scripts/           # Optional — helper scripts the agent can execute
└── assets/            # Optional — templates and output resources
```