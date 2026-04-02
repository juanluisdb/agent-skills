# Writing RFCs

Load this reference when the user needs help writing, structuring, or refining an RFC.

## Start From The Problem

- An RFC should start from a concrete problem, not a preferred solution.
- Name what triggered the RFC: recurring bugs, scaling limits, product pressure, migration pain, operational incidents, or design drift.
- Separate symptoms from root causes. A good RFC explains why the current pain exists, not only what change sounds attractive.

Do not start drafting files until the current state and problem are clear enough to explain plainly.

## Understand The Current State

Before writing:

- inspect the relevant code, data flow, and operational constraints
- verify factual claims about how the system works today
- identify the boundaries of the problem and what is explicitly out of scope

If you cannot explain the current state clearly, investigate more before expanding the RFC.

## README Is An Index Card

Treat `README.md` as the entry point, not the full proposal.

It should let a reader understand in seconds:

- what this RFC is about
- why it exists now
- where the substantive discussion lives

Keep the detail in supporting docs when the problem analysis, design, rollout plan, or testing plan would otherwise get mixed together.

## Split Docs By Purpose

Do not split purely because a document is long. Split when different sections serve different jobs.

Common patterns:

- `current_state.md` for how things work today and why that is a problem
- `technical_design.md` for the proposed approach, trade-offs, and rejected alternatives
- `implementation_plan.md` for rollout sequencing, dependencies, and migration steps
- `qa_plan.md` for testing and validation on non-trivial changes

Small RFCs can stay compact. Large RFCs should separate concerns so readers can jump to the part they need.

## Design Discussion Quality

- Present meaningful alternatives, not just the preferred answer.
- Explain trade-offs honestly. Every reasonable option has downsides.
- Record rejected alternatives briefly so future readers do not reopen the same branch of the decision tree without context.
- Evolve the RFC into a coherent proposal as feedback arrives; do not turn it into a changelog of every idea ever mentioned.

## Scope And Delivery

- Keep scope aligned with the stated problem.
- Prefer incremental delivery over big-bang transitions when the change is risky.
- Call out migrations, compatibility constraints, rollback concerns, and operational unknowns when they matter.
- Be explicit about what this RFC does not attempt to solve.

## Writing Style

- Be concrete.
- Prefer verified facts over hand-wavy claims.
- Use structure that helps readers scan quickly.
- Keep the PR description short and let the RFC docs be the source of truth.
