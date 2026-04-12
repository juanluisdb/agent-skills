---
name: code-review
description: Review pull requests, merge requests, diffs, or local branches and surface actionable findings. Use when the user asks for code review, review this PR/MR/diff, or wants approval-oriented feedback. Not for triaging existing reviewer comments; use `review-feedback` for that.
---

# Code Review

Use this skill for the review itself: understand the change, assess risk, and surface actionable findings.

## Boundaries

- Review the code change, not the discussion around it.
- If the user primarily wants help understanding or responding to existing review comments, use `review-feedback`.
- Keep the review conversational by default. Draft or post platform comments only if the user asks.

## Review Surface

Start by identifying what is being reviewed:

- a GitHub PR
- a GitLab MR
- a local branch against a base branch
- an explicit diff or patch
- a set of changed files

Figure out the base and head when needed. If the review surface is ambiguous, inspect the repo or provided link and state the assumption you are using.

## Gather Context

- Read the diff, but do not stop there.
- Read affected files in full when they matter to behavior, contracts, or surrounding logic.
- Pull in title, description, linked issue, or commit context when available and helpful.
- Distinguish mechanical changes from behavioral ones and spend most of the review on behavioral risk.

## Existing Review Context

If the platform or local context exposes existing comments, discussions, or review threads:

- check whether a concern has already been raised
- avoid repeating the same point unless you have materially new evidence or a clearer framing
- do not treat existing comments as truth; verify them against the current code and latest diff
- call out when a concern appears stale, already addressed, or only partially addressed

## Review Mindset

- Review like the deciding engineer, not a passive observer.
- Prioritize correctness, contracts, failure modes, security, and test coverage over style.
- Prefer concrete, actionable findings over vague discomfort.
- Use judgment about depth: a tiny rename does not need an architecture essay, but a risky refactor may need broader reasoning.

## Review Lenses

Use the lenses that match the change:

- correctness and edge cases
- interfaces, schemas, and data contracts
- error handling and operational failure modes
- tests and regression coverage
- security and trust boundaries
- maintainability, coupling, and design clarity
- performance or scaling risks when the change touches hot paths or fan-out

Load deeper references only when they materially help:

- `references/typescript-review.md` for TypeScript reviews
- `references/python-review.md` for Python reviews
- `references/security-review.md` for auth, input handling, secrets, permissions, external calls, or other risky boundaries
- `references/conventional-comments.md` when drafting review comments for posting

## Complex Reviews

For large or high-risk reviews, consider parallel passes across different code areas or perspectives.

- Split by subsystem when the diff spans distinct parts of the codebase.
- Split by lens when the risky questions are different: correctness, contracts, security, performance, tests, or design.
- Give each pass a clear scope so the same issue is not rediscovered three times.
- Synthesize before reporting back: merge duplicates, resolve disagreements, and present one coherent set of findings.
- If the review is small or tightly coupled, keep it in one pass instead of parallelizing for its own sake.

## Findings

Present findings in chat first.

Each finding should include:

- priority
- location
- issue
- why it matters
- concrete suggestion

When relevant, also note whether the concern is already raised elsewhere in the review context.

Use this priority scale:

- `CRITICAL`: likely production breakage, data loss, security vulnerability, or severe contract error
- `HIGH`: bug or breaking behavior likely to matter soon
- `MEDIUM`: meaningful correctness or maintainability risk under realistic conditions
- `LOW`: minor issue with limited blast radius
- `SMELL`: something looks fragile or inconsistent but impact is not yet fully clear
- `SUGGESTION`: non-blocking design or polish idea

## Guardrails

- Do not rely on diff snippets alone when full-file context is needed.
- Do not post comments automatically.
- Do not inflate low-signal nits when higher-risk issues exist.
- Do not assume an existing reviewer is right just because they commented first.
