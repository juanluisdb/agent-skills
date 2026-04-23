---
name: explain-code
description: Explain code clearly and accurately for humans. Use when the user asks to explain a file, function, diff, stack trace, or code path, or says "what does this do", "walk me through this", or "how does this work".
disable-model-invocation: true
---

# Explain Code

## Goal

- Match the user's scope exactly.
- Optimize for comprehension, not exhaustiveness.
- Explain behavior and structure before offering interpretation.

## Gather Context

- Read the relevant code before explaining it.
- Expand outward only as needed: callers, callees, types, tests, config, or data flow.
- If the request is ambiguous, state the scope assumption you are using.
- If key context is missing, say what is missing and how that limits the explanation.

## Output Shape

- Match the user's requested depth and format.
- For non-trivial explanations, usually start with a short `TLDR`.
- Use short sections with clear headings when the explanation has multiple parts.
- Anchor claims with file or line references when that improves clarity.

## Flows And Diagrams

- Use a small `mermaid` diagram when the main story is control flow, data flow, handoff between components, or state transitions.
- Keep diagrams minimal and faithful to the code.
- Prefer diagrams when they clarify sequencing or relationships faster than prose.
- Do not present inferred edges or behavior as confirmed facts.

## Code Snippets

- Show only the code needed for the current point.
- Prefer short excerpts over large verbatim blocks.
- You may simplify a snippet when that makes the explanation clearer, but keep it behavior-faithful.
- If a snippet is simplified, say so.
- Add brief comments only when they materially help explain the point.

## Facts vs Inference

- Separate what is directly supported by the code from what you are inferring.
- Mark uncertainty explicitly with phrasing such as `Fact`, `Inference`, `Likely`, or `Unclear from the code shown`.
- If the code does not establish something, say so plainly.
- Do not invent intent, requirements, bugs, or future behavior.

## Guardrails

- Do not turn the answer into a line-by-line transcript unless the user asked for that.
- Do not hide uncertainty behind confident wording.
- Do not overload the explanation with irrelevant surrounding code.
- Prefer the simplest explanation that remains accurate.
