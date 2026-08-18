---
name: software-design
description: "Engineering judgement on how software should be shaped: module depth and seams, interfaces and error models, data and state, trust boundaries, test strategy, rollout and idempotency, observability. Language-agnostic. Use when shaping, building, or judging a change."
---

# Software Design

What good looks like when shaping software, independent of language and framework.

This skill holds the judgement, not the stance. Whether you are choosing a shape, building to one, or flagging a deviation in someone else's diff is decided by the context that loaded it. The judgement is the same in all three.

Good design usually looks underwhelming. The work is in the competing values behind the choice, not in the cleverness of the result: this shape costs a layer of indirection and buys a seam two adapters use; that one costs a duplicated definition and buys independent deploys. Taste is knowing which value wins here, and being able to say why. A design nobody can argue with is often one nobody made a decision in.

## The repo wins

Read the repo before applying anything here. Where they disagree, the repo is right.

- Agent-rule files first (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md`). They are the most current explicit statement of convention.
- Then the enforcement layer: type config, lint config, CI. A rule that runs is a decision already made.
- Run the linter rather than checking remembered rules by eye. Mechanical checks are cheaper and more reliable executed than recalled, and anything the build already proves needs no attention here.
- Documented convention is deliberate, so follow it. Undocumented repetition is evidence, not authority: look for a rationale in a comment, doc, or commit message, and treat a pattern with none as emergent rather than chosen.
- Local consistency, edge improvement. New code inside an existing module follows local style; new modules can do better.

## Dimensions that get dropped

Interface shape and the obvious failure paths get covered without prompting. These do not, and each one is invisible to a mock-based unit test.

- **What the tests pin.** A green suite can pin nothing. Delete the guarantee from the implementation; if the suite stays green, it was never pinned.
- **More than one execution.** Retry, resume after interruption, at-least-once redelivery. A side effect needs a dedupe key derived from the work and stable across attempts, not from the attempt. A persisted aggregate that should accumulate must merge across attempts rather than overwrite on completion.
- **More than one state live at once.** A flag's off and on paths, old and new code mid-deploy, old and new schema mid-migration, two API versions in flight, records persisted before the change. Correctness is required in every coexisting state and in the window where they overlap, not just the end state. Any "safe because `<condition>`" rests on an assumption about state you may not control, so name it and check it.
- **Contracts outside the diff.** Deploy config keyed on an env-var *name*, monitors keyed on a log *substring*, a downstream that deserializes your payload strictly, an SDK client depending on current default semantics, an analytics consumer reading an event shape. No grep and no unit test sees these, and renaming or reshaping any of them is a contract change to a system outside the change.
- **Observability of the failure paths.** Enumerate the terminal states the surface can reach: success, retries exhausted, mid-stream failure, cancellation. A metric that only fires on success makes a broken system look healthy.
- **The performance number.** "Fast enough" is not a requirement until it is a number on a stated baseline with somewhere that checks it (`references/operations.md`). Without those three parts nothing fails when it regresses, and the regression arrives as a complaint rather than a build failure.
- **The trust boundary.** Where untrusted data becomes trusted, decided once. Validating a value and then passing the raw value onward throws away what the check proved, so every layer below re-checks or silently trusts.

## Tests that settle an argument

- **Depth.** A lot of behaviour behind a small interface, so callers learn little and change concentrates in one place. If a name has to list what it does, it is several concepts.
- **The deletion test.** Inline the module at every call site. If complexity vanishes it was a pass-through; if it reappears at N callers it earns its keep.
- **One adapter is a hypothetical seam, two is a real one.** Do not build a port, interface, or injection point where nothing actually varies across it. Decide where the seam goes as its own question rather than inheriting it from the current file layout.
- **The simplest thing that could possibly work, then the next thing.** Reach for the version with the fewest moving parts that solves the case in front of you, and let the next real case buy the next piece of machinery. This is not an argument for sloppiness: the simplest thing still has to work, and choosing it is only defensible when you can say what the more elaborate version would have bought.
- **Evidence before complexity.** "Could", "might" and "what if" do not justify code; an observed failure does. When runtime proves the case is real, fix the smallest failure at the boundary that owns it.
- **Make the two unable to disagree.** When a shape lands in two places, such as a model and its wire mirror or a rule and the lint that checks it, prefer one definition over two plus a drift test. The detector is a real option, but it costs a second thing to maintain and guards only what it happens to compare. Take it deliberately, and decide which artifact it compares: the payload the consumer receives, not two self-consistent halves.
- **If the only way to test it is mocking everything, the shape is wrong.** Classify the dependency instead (`references/testing.md`), which names what to substitute.
- **Blast radius sets the effort.** A reversible change earns a decision. An expensive-to-undo one earns an argument, and a record of why the confidence is warranted.

## References

Load the ones that match. A plausible match is a match, and a skipped reference drops a whole dimension.

| Reference | Load when |
|---|---|
| `references/modules.md` | A module's shape is being designed, reshaped, or judged: a new module, an extraction, a refactor that moves responsibilities, a decision about where a seam goes, a dependency to classify, coupling or layering questions. |
| `references/interfaces.md` | A surface someone else calls: a public API, a library or SDK, a CLI, a tool definition, an event or payload contract. Also the error model, defaults, and versioning. |
| `references/state.md` | Data outlives the code that wrote it: a schema or model change, a stored shape, a lifecycle with states, a cache or derived copy, a source-of-truth question. |
| `references/security.md` | Anything user-facing, authenticated, persisting data, calling external services, handling secrets, or touching crypto or PII. Threat model, authn versus authz, the validation boundary, injection surface, outbound request safety, tenant isolation. |
| `references/testing.md` | Deciding what to test, or judging what a suite proves. Dependency classification and the strategy it implies, one test per guarantee, what a green test actually pins, which tests a refactor retires. |
| `references/operations.md` | The change ships, migrates data, runs more than once, has a performance target, or has to be watched in production. Rollout shape, migration ordering, idempotency and replay, failure classification, observability, performance budgets, resource lifecycle. |

A user-visible surface judged on how it looks or feels is out of scope here. That judgement is taste rather than engineering, and no linter checks it.
