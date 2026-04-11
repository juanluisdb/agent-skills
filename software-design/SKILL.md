---
name: software-design
description: Thinking guide for designing good software while building. Use when comparing approaches, shaping APIs, workflows, contracts, defaults, data models, or refactors. Combines engineering rigor with product-aware reasoning. Not for visual design, branding, or broad PM strategy.
---

# Software Design

Use this skill when the task is to reason about software structure, behavior, and trade-offs before or during coding.

## Mindset

- Start from the actual software decision in front of you.
- Stay grounded in the codebase, constraints, and maintenance burden.
- Keep engineering rigor primary, but do not treat product thinking as optional.
- Design good software by considering both how the system works and how it is experienced.
- Explore materially different approaches before converging, especially for long-lived surfaces.

## Operating Sequence

1. Frame the decision.
2. Identify who experiences this decision and what they are trying to do.
3. Explore distinct design directions, including more radical alternatives when the decision matters.
4. Evaluate each direction through both product and engineering lenses.
5. Converge on the simplest robust design that creates a clear surface and can be supported cleanly underneath.

Scale the depth to the task. A one-line fix does not need an architecture exercise. A new API, workflow, contract, or refactor usually does.

## Design Prompts

### Framing

- What problem are we solving?
- What is explicitly out of scope?
- What are we optimizing for in this decision: clarity, flexibility, speed, safety, adoption, operability, backward compatibility, or something else?
- Is this a short-lived implementation choice or a long-lived software surface?

### Consumer And Job

- Who is the immediate consumer of this decision?
- Is that consumer an end user, developer, operator, maintainer, or another system?
- What are they actually trying to do?
- What would feel obvious, trustworthy, and unsurprising to them?
- What mistakes are they likely to make?

### Surface And Mental Model

- What surface do we want others to depend on?
- Does the design match the consumer's job, or mainly reflect current internals?
- Are we exposing a stable mental model or leaking implementation details?
- Are naming, defaults, workflow, and behavior aligned with the domain?
- Should this surface be task-centric, object-centric, workflow-centric, or something else?
- Is the contract explicit enough to be understandable without knowing the implementation?

### Exploring Approaches

- What are the materially different ways to model this?
- Are we comparing different mental models, or only minor implementation variants?
- What would a more opinionated version look like?
- What would a more flexible or lower-level version look like?
- What would the simplest possible version look like?
- Which approach gives the clearest surface with the lowest long-term regret?

### Technical Design

- Where should the authority for this behavior live?
- What module or boundary should own the complexity?
- Does this reduce coupling, or just move it somewhere less visible?
- Are we adding abstraction because the domain needs it, or because duplicate-looking code feels uncomfortable?
- How will this be tested?
- What happens when dependencies fail, inputs are partial, or the operation runs twice?

### Product Quality In Software

- What defaults create trust, and which create confusion?
- How should failure behavior appear at the surface?
- What should be easy, and what should require explicit intent?
- What concepts, permissions, states, or errors will users need to understand?
- Does this design make common tasks simple without making edge cases impossible?

### Evolution

- If internals change later, would this surface still make sense?
- What future changes would this design make easier or harder?
- Is this design incremental and reversible?
- Are we locking in a contract too early, or hiding too much behind a vague interface?

## Principles

- Engineering rigor first, but never isolated from product reality.
- Consumer-first surfaces, implementation-second reasoning.
- Design around the job to be done, not the current internals.
- Stable mental models over accidental implementation leaks.
- Explicit contracts over hidden defaults.
- Trustworthy defaults over configuration sprawl.
- Deep modules over thin wrappers.
- Domain-first naming over implementation-first naming.
- Incremental, reversible steps over big-bang changes.
- Design for failure, testability, and operability from the start.
- YAGNI: do not optimize for speculative requirements.
- DRY with judgment: remove duplication when the abstraction is real.

## When Helpful

Present distinct approaches with trade-offs before recommending a direction, especially when the decision affects a long-lived surface such as an API, workflow, contract, or data model.

Do not force a fixed output structure when lightweight guidance is enough. The goal is better software decisions, not ceremony.
