---
name: swe-design
description: Thinking guide for software design and implementation planning. Use when comparing approaches, shaping APIs, planning refactors, or designing systems. Not for visual, brand, or UX design critique.
---

# SWE Design

Use this skill when the task is to reason about software structure, trade-offs, and implementation shape before or during coding.

## Mindset

- Match design effort to task size. A one-line fix does not need an architecture document.
- Explore more than one viable approach before converging on a recommendation.
- Keep the design grounded in the actual codebase, constraints, and likely maintenance burden.

## Design Prompts

- What problem are we solving, and what is explicitly out of scope?
- Where should the authority for this behavior live?
- What interface do we want other code to depend on?
- What are the meaningful alternatives, and what do we gain or give up with each?
- How will this be tested?
- What happens when dependencies fail, inputs are partial, or the operation runs twice?
- What future changes would this design make easier or harder?
- Does this reduce coupling, or just move it somewhere less visible?
- Are we adding abstraction because the domain needs it, or because duplicate-looking code feels uncomfortable?

## Principles

- Deep modules over thin wrappers.
- Domain-first naming over implementation-first naming.
- Explicit contracts over hidden defaults.
- Incremental, reversible steps over big-bang changes.
- YAGNI: do not optimize for speculative requirements.
- DRY with judgment: remove duplication when the abstraction is real.
- Design for testability, failure, and operability from the start.
- Prefer the least surprising surface area that still gives you room to evolve the internals.

## When Helpful

Present two or more approaches with trade-offs and a recommendation.

Do not force that structure when the user wants lightweight design guidance woven into an implementation discussion.
