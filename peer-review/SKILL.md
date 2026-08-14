---
name: peer-review
description: Delegate a deep code review of your in-progress work to a subagent, then critically triage its findings before acting. Manual-only — invoke with /peer-review during an implementation session.
disable-model-invocation: true
---

# Peer Review

You are the implementation agent. You delegate a deep review of your own work to a fresh subagent, then act as a skeptical critic over what it returns. You do **not** read the `code-review` skill yourself — the subagent runs it.

This is a heavyweight, multi-subagent review. Run it only when the user explicitly invokes `/peer-review`.

## 1. Delegate the review

Spawn one subagent and tell it to **use the `code-review` skill** to review the current work. Do not describe how to review — just name the skill and hand it the scope.

**Brief it neutrally.** Hand over the scope, not your opinion of it. Don't tell the subagent what you think already works, what you're unsure about, or where to look — you wrote this code, so steering a fresh reviewer toward your own assumptions reproduces your blind spots instead of catching them. Keep the framing factual and let the review reach its own findings; you challenge them in step 2.

Pass the scope context you already have, for example:
- uncommitted working-tree changes
- the current branch vs its base
- an MR/PR you just pushed
- specific files or a feature slice

If the user named a surface in their `/peer-review` invocation, relay that. If not, state the surface you're handing over (e.g. "uncommitted changes + this branch vs master") so the subagent isn't guessing.

Ask the subagent to return its findings as a structured list: each finding with file/location, severity, the claim, and its evidence.

## 2. Critically triage the findings

Load the `review-feedback` skill and run its triage over the subagent's output. Treat the findings the way you'd treat a human reviewer's comments, not as ground truth. The change under review is the work you just did, so skip its MR-fetching step and go straight to evaluating each finding against the code. For each one:

- decide: **valid**, **partially valid**, **stale/already-handled**, **preference-only**, or **incorrect** — with evidence
- for valid ones, label severity (blocking / non-blocking / nit) and note what the fix would be and any regression risk
- consolidate findings that point at the same root cause

You wrote this code, so push back where the review is wrong or speculative — don't rubber-stamp it.

## 3. Present and wait

Lead with a summary table — one row per finding the subagent returned, in its order. Every finding gets a row, including the ones you rejected and the ones you consolidated; nothing is dropped or silently merged.

| # | Where | What the review said | Verdict | Action |
|---|---|---|---|---|
| 1 | `worker/models.py:42` | New required input field breaks the deploy window | valid, blocking | make it `\| None = None` |
| 2 | `tools/search.py:88` | Unbounded retry loop | incorrect — cap is in the caller | none |

- **What the review said** carries the reviewer's claim in the reviewer's own terms. Not your rebuttal, not the fix, not a paraphrase of the code. Someone reading only that column must come away knowing what the review flagged.
- **Verdict** is one of the five labels from step 2, plus severity when valid, plus the one-line reason when you disagree.
- Consolidated findings keep their own rows and point at the row holding the root cause ("same cause as #2").

Below the table, expand only the rows where detail changes a decision: your evidence for a pushback, the shape of the fix, regression risk. Rows that need no prose get none.

**Stop there and wait for the user's go-ahead** before applying any changes.