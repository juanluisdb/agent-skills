---
name: review-feedback
description: Triage feedback on a code change and recommend what to fix, defend, clarify, or ignore. Use for MR/PR review comments, unresolved threads, a reviewer's notes, or findings a review agent handed back. Not for producing the first-pass review itself; that's code-review.
---

# Review Feedback

Use this skill when the main task is to understand and act on feedback that already exists about a code change, whatever carried it: MR/PR threads, notes from a colleague, or findings returned by a review agent.

## Boundaries

- This skill is for triaging review feedback, not doing the initial code review from scratch.
- If the user wants a fresh review of the change itself, use `code-review`.
- **This skill assesses; it does not edit.** The deliverable is a verdict per thread and a recommended next move. Applying a fix, drafting a reply, and resolving a thread are separate actions the user asks for after reading the assessment. Triaging and patching in one motion skips the step that was the point: the whole exercise exists because some of these threads should not be actioned at all, and that call is the user's. Read the code as much as you need, run whatever experiment settles a question, change nothing.

## Gather Context

When the feedback lives in an MR/PR:

1. Fetch MR/PR title and description first to understand the change intent.
2. Fetch discussions (for GitLab, see `glab` skill for API patterns — paginated discussion fetching, filtering unresolved).
3. Default to unresolved, resolvable discussions only unless user asks for all.

When the feedback was handed to you directly (a review agent's findings, notes in chat), you already have the comments. Establish the change they are about instead — the diff, branch, or working tree — and read it before judging any finding.

## Triage by Relevance and Severity

Label each thread quickly:

| Label | Meaning |
|---|---|
| **blocking** | Must resolve before merge — correctness, security, contract issue |
| **non-blocking** | Valid concern but shouldn't hold up merge |
| **nit** | Style, formatting, naming preference |
| **question** | Reviewer seeking clarification, not necessarily requesting a change |
| **praise** | Positive feedback, no action needed |

Prioritize technically actionable threads (blocking + unresolved).

**A severity that arrives with the feedback is a claim, not a label to adopt.** Findings handed over by a review agent usually come pre-graded on a scale of their own (CRITICAL / HIGH / MEDIUM / DESIGN / LOW / SMELL, or similar). Re-derive the label above from the code and the blast radius instead of translating the grade you were given: a CRITICAL that nothing reachable produces is not blocking, and a LOW on a published contract other deploys read may be. Say where you moved a severity and why — the move is often the most useful line in the summary.

## Evaluate Each Thread

For each meaningful thread:

- identify the impacted file, symbol, or behavior
- read the relevant code in full, not only the quoted snippet
- check whether later commits already addressed the concern
- when the concern is empirically decidable (a race that may not be reachable, a test that allegedly fails, a claimed perf cost), run the cheap experiment — a repro, the test, a mutation — instead of reasoning about it; a defense backed by evidence beats a rationale, and so does a fix
- decide whether the feedback is valid, partially valid, stale, preference-only, or incorrect
- explain the reasoning with evidence from the current code

## Look for the Root Decision

Before recommending fixes, step back and read the threads *together*, not one by one. A cluster of comments is often symptoms of a single bad decision — a design, scope, or approach choice — rather than independent defects.

Signals the comments share a root cause:

- multiple reviewers poking at the same area or abstraction
- repeated "why is this here?", "this feels awkward", or "couldn't this be simpler?"
- several nits piled on code that maybe shouldn't exist at all

When you see this, **do not fix each comment in isolation.** A workaround per thread entrenches the bad decision and produces a patchwork that's worse than the original. The right move is usually a single one: name the underlying decision and put it back on the table — surface it to the user (and likely the reviewer) instead of silently patching around it. This is the escalation case for the "ask before architectural changes" guardrail below.

Hold the bar in both directions: don't manufacture a grand architectural problem out of three unrelated nits. Only call out a root decision when the signal is real.

## Weigh the Remedy Against the Risk

Some comments are valid in the abstract and still not worth acting on. The reviewer names an edge case, and honoring it means a retry layer, an abstraction, a config knob, and three new states to test. The concern is real, the remedy is a cathedral.

Price both sides before recommending a fix:

- **Reachable?** Trace the real callers and upstream contracts. A guard against a state nothing can produce isn't defensive, it's misleading: future readers preserve it and design around it.
- **Cost if it happens.** Blast radius and recoverability, not just "is it a bug". A retried worker task that fails loudly is not data corruption.
- **Cost of the remedy.** Count concepts added, not lines: new abstraction, new config knob, new failure mode, permanent reading cost.

Real risk plus cheap fix means fix it. Real risk that only a heavy remedy fixes is a design problem, not a thread: see "Look for the Root Decision".

For a speculative risk with a heavy remedy, one of these rungs usually settles it:

- raise or assert on the unexpected state, because fail fast beats handle-everything
- narrow the type or contract so the state can't be constructed
- one line naming the invariant and why it holds
- a test pinning the assumption, so CI reports the day it stops holding
- a tracked follow-up when the risk is real but not now

Hold the bar in both directions. Harden without arguing where the tail is expensive: security boundaries, data loss, money, PII, published contracts other deploys depend on. Low probability doesn't shrink those. And "this is overengineering" is a claim needing the same backing a fix would: the reachability trace, not a preference.

When you recommend defending, make the defense falsifiable. Grant that the state would be bad, show why it can't occur, name the cheaper rung you took, and invite the path you may have missed. The reviewer may know a caller you can't see.

## Recommendations

For each actionable thread, recommend the next move. These name what should happen next, not what you do now:

- **fix as proposed** — the reviewer's point stands and the fix is straightforward and low-risk
- **alternative fix** — if tradeoffs exist or a different approach is better
- **defend current approach** — when concern is not applicable, with rationale
- **concede** — the remedy is useless but trivial and adds no new concept, so closing the thread costs less than the argument. Label it a concession, not agreement, and let the user pick
- **ask for clarification** — when reviewer intent is unclear
- **no action** — because the concern is stale or no longer applies

If several comments point at the same root issue, consolidate them instead of treating them as unrelated work — and if that root issue is a flawed decision, recommend revisiting it rather than working around each symptom (see "Look for the Root Decision").

Include potential regressions and required tests for each option.

## Present Action-Ready Summary

Present in chat. Useful fields:

- thread or location
- assessment (valid / partially valid / disproportionate / stale / not applicable)
- why
- recommended next step
- tests or follow-up needed

Ordered by severity and impact. End with the open questions that need the user's answer, then **stop and wait**. The summary is the finished deliverable; editing code or posting replies starts only when the user says which recommendations to take.

## Complex Feedback Sets

If there are many threads, consider parallel passes by file, subsystem, or comment cluster, then merge overlapping conclusions before reporting back.

## Draft & Post Replies (MR/PR, on demand)

Only when the user explicitly says to respond, post, or draft replies:

1. Draft each reply per *How to write a reply* below
2. Show the full batch to the user for final confirmation
3. Post using the platform's API (for GitLab, see `glab` skill for posting workflow)

**Do NOT post anything until the user explicitly says to.**

### How to write a reply

A reply is read in a narrow comment column by a colleague with a dozen other threads open. They should get the answer from the first line and be able to check it without asking you anything.

- **Open with the disposition.** Fixed, not fixing, partly, or a question back — in the first few words, before the reasoning. Someone scanning ten threads needs to know which ones still want them.
- **Point at evidence, not at reasoning.** The commit SHA, the file and line, the test that now covers it, the callers you traced. A colleague can check a link. They can't check a rationale.
- **Two or three sentences is a finished reply.** Everyday words, one idea per sentence. No hedging, no "great catch" preamble, no restating their comment back at them. Keep every fact, path and number.
- **Show it when the answer has a shape.** A before-and-after diff, the call path, the real values through the case they're worried about. A reviewer reading a paragraph about an ordering problem has to rebuild the ordering; four lines of sequence hand it over.
- **A defence grants the concern first**, then shows why the state can't occur, names the cheaper rung you took instead, and invites the caller you may have missed. See *Weigh the Remedy Against the Risk*.
- **Answer that thread and nothing else.** A summary across threads belongs in the MR description or one top-level comment, not appended to a reply about something narrower.

## Guardrails

- A reviewer comment is a claim, not a verdict — verify against the code in both directions: don't assume the reviewer is right, don't dismiss a minor-sounding one unchecked.
- Measure what's measurable before classifying fix vs defend.
- A comment cluster can hide one bad decision — surface it, don't patch symptoms one by one.
- Valid in the abstract isn't the same as worth building: price the remedy before recommending it (see "Weigh the Remedy Against the Risk").
- Assess, don't edit: the deliverable is the verdict and the recommended move, and the user decides which ones get taken.
- A severity that came with the feedback is a claim to re-derive, not a label to adopt.
- Never post replies unless the user asks. Never resolve or mark done a thread someone else started unless the user explicitly asks — check the thread's original author first; resolving another person's thread on your own initiative reads as dismissing their feedback for them.
- Call out hidden coupling (shared utilities, schema contracts, persistence formats).
- Be explicit about uncertainty when context is missing.