---
name: write-mr-description
description: Write or edit any MR/PR description as a snapshot of the final change — what it does, why, what changed — not a development journey. Read this before writing or editing any MR/PR description, whether the user asks or you generate one from a diff.
---

# Writing good MR descriptions

An MR description is a **snapshot of the final change**, not a journal of how you got there. The reviewer doesn't care about the path you walked — they care about what the code looks like now and why it should be merged.

## The anti-pattern to avoid

AI-generated descriptions often read like a changelog of the development session:

> First, we refactored the X module. Then we noticed the Y bug, so we fixed it. After that, we added tests. Finally, we updated the docs.

This is wrong. The MR is not the story of your branch. Squashed commits, reverted experiments, and detours are invisible to the reviewer and irrelevant to the merged state. Describe what **is**, not what happened.

## Structure

Keep it brief. Four parts, in this order:

1. **What** — one or two sentences naming the change in the present tense. ("Adds X.", "Replaces Y with Z.", "Fixes the bug where …")
2. **Why** — the motivation: the bug, the requirement, the constraint, the ticket. Skip if it is genuinely self-evident from the what.
3. **Changes** — a short list of the notable modifications a reviewer should know about before opening the diff. Bullet points, present tense. Group by area if it helps; don't enumerate every file.
4. **Decisions** — the choices you made while implementing, and why. The goal: a reviewer reads these and has no questions left to ask, except to disagree. Capture anything a reviewer would otherwise stop and question — an approach taken over an obvious alternative, a tradeoff, a scope boundary, a library or pattern choice. Frame each as the reason for the final state ("uses X rather than Y because Z"), never as the order of events. Omit only decisions that are self-evident from the diff.

That's the whole template. Adapt freely — a one-line trivial fix needs only "What"; a large refactor might add a "Notes for reviewers" or "Rollout" callout.

## Voice

- Present tense, declarative. "Adds retry logic to the client." Not "I added" or "we will add".
- No timeline words: *first*, *then*, *after that*, *finally*, *initially*, *originally*.
- No narration of *how you worked*: "explored several approaches", "ended up". Recording *what you decided and why* is not this — that belongs in **Decisions**, framed as the reason for the final state.
- Cut filler. If a sentence describes the merged state in fewer words, prefer that.

## Numbers

A number belongs in the description only when it **is the argument** — a measured speedup, a chosen limit, a reduced payload. Then say how it was measured. Incidental metrics (coverage percentages, test counts, line counts, timings quoted as colour) are decoration the reviewer can't act on: they drift out of date and invite nitpicks. Leave them out.

Never do work just to decorate the description. Running the test suite to harvest a pass count or a coverage figure adds noise, not evidence — CI already reports that. Run things to verify the change, not to caption it.

## Where the change comes from

If you already hold the change in context — you just implemented it, or worked it out in this session — write from what you know. Don't re-read the diff to confirm; you already carry the decisions and the *why*, which the diff can't tell you anyway.

If you don't have that context, read the final diff and describe **that**. Don't infer a development sequence from commit messages — squash-merge often makes them noise. Pull the *why* and the *decisions* from the ticket or conversation; if they aren't there, ask the user rather than guess.
