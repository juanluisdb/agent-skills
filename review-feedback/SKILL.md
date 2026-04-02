---
name: review-feedback
description: Analyze existing PR or MR review comments and recommend what to fix, defend, clarify, or ignore. Use when the user asks about reviewer feedback, unresolved comments, or how to respond to review threads. Not for first-pass review of the code change itself.
---

# Review Feedback

Use this skill when the main task is to understand and act on existing review comments.

## Boundaries

- This skill is for triaging review feedback, not doing the initial code review from scratch.
- If the user wants a fresh review of the change itself, use `code-review`.
- Keep replies and thread resolution manual unless the user explicitly asks you to draft or post them.

## Gather Context

- Identify the review surface: PR, MR, local review export, or pasted comments.
- Read the change intent first so comments are evaluated in context.
- Collect existing comments or discussions, prioritizing unresolved or actionable threads unless the user asks for everything.
- For GitHub PRs, load `references/github-feedback.md`. If `gh` is available, use the helper script there to fetch threads efficiently.
- If `gh` fails because of sandbox, auth, or environment restrictions, do not assume no feedback exists. Consider rerunning outside the sandbox with approval if that access is important to the task.

## Evaluate Each Thread

For each meaningful thread:

- identify the impacted file, symbol, or behavior
- read the relevant code in full, not only the quoted snippet
- check whether later commits already addressed the concern
- decide whether the feedback is valid, partially valid, stale, preference-only, or incorrect
- explain the reasoning with evidence from the current code

## Recommendations

For each actionable thread, recommend the next move:

- fix directly
- take a different fix than the reviewer suggested
- defend the current approach
- ask for clarification
- no action because the concern is stale or no longer applies

If several comments point at the same root issue, consolidate them instead of treating them as unrelated work.

## Output

Present an action-ready summary in chat.

Useful fields are:

- thread or location
- assessment
- why
- recommended next step
- tests or follow-up needed

## Complex Feedback Sets

If there are many threads, consider parallel passes by file, subsystem, or comment cluster, then merge overlapping conclusions before reporting back.

## Guardrails

- Do not assume a reviewer is right just because they left a comment.
- Do not ignore a comment just because it sounds minor; verify the actual code impact.
- Do not post replies, resolve threads, or mark discussions done unless the user asks.
