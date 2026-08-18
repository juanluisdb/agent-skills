# Interfaces and Contracts

A surface someone else calls: a public API, a library or SDK, a CLI, a tool definition, an event or payload contract. The distinguishing property is that you do not own all the callers, so the cost of getting it wrong is paid later and by someone else.

## The interface is wider than the signature

Everything a caller must know to use the code correctly is part of the contract: the invariants it upholds, the ordering constraints between its calls, the error modes it can raise, the configuration it requires, and the performance characteristics callers lean on.

Each of those can change while the types stay byte-identical: a function that now raises where it used to return an empty list, one that must be called after an `init` it did not need before, a setting that becomes required, a call that quietly turns into N calls. Those are breaking changes with no type diff to catch them. When one moves, the callers and the documentation move with it.

## Shape it around the caller's work

- **Model the consumer's use case, not the storage layout.** A surface that mirrors the tables makes every consumer reassemble the concept the domain already has, and each one does it slightly differently. The unit the caller thinks in is the unit the interface should return.
- **The common case is one call.** If reaching the ordinary outcome takes a fetch, a filter, and a second fetch, the interface has pushed its own composition onto the caller. A common multi-step pattern is a candidate for a single call that owns it.
- **Every additional signature is cognitive load.** Methods returning near-identical shapes usually want to be one method plus a parameter. A caller who cannot tell which of two to call without reading the source is looking at a surface that has not decided.
- **Names and defaults carry the documentation.** Parameter names should read at the call site rather than leaking internal naming, defaults should match the most common use, and the valid values of a constrained parameter should be discoverable without reading the implementation.
- **Remove friction the system could absorb.** Any step the implementation could do transparently, and instead asks the caller to do, is a step some caller will skip.

## The error model

Pick one discipline per module and hold it.

- **Expected versus unexpected.** Validation failure, not-found, and permission-denied are expected outcomes and belong in the return type or a declared error set. A broken internal invariant is a bug and should fail loudly with a useful stack rather than being folded into a normal-looking result.
- **Failures must be distinguishable.** A consumer needs to tell "not found" from "no data" from "the call failed". Silent empty results are the worst failure mode, because the caller cannot tell success from breakage. Two distinct causes must not share one message: collapsing "no credential" and "credential provider unreachable" into "set your token" leaves a caller who already set it with no path to recovery.
- **An actionable message says what to do next.** "Expected `userId` to be a UUID, got '123abc'" beats "Invalid input". The message shape is part of the design, not just the error class.
- **Do not mix paradigms in one module.** Exceptions in half the functions and result values in the other half means every caller has to know which is which.

## Defaults and ignored parameters

- **A default is a decision made on the caller's behalf.** For each parameter with one, ask whether it is safe for every caller, or whether it quietly masks a choice the caller should be making.
- **Trace the parameter.** Is it stored and used, or accepted and discarded? An ignored parameter with a default produces no error at the call site, which makes it one of the hardest bugs to notice.
- **Do not loosen a contract for tests.** A parameter made optional only so existing tests or callers keep compiling encodes "the tests do not pass this", not a real caller need. Fix the test and keep the parameter required.
- **Cross-field invariants belong at construction.** A conditionally-required field enforced downstream will be reached by a path that skipped the check.

## When the consumer is a program

An API, CLI, or tool called by a script, a service, or an agent has no reader to interpret an inconsistency, so the envelope *is* the contract and partial adherence is a bug.

- A universal status field must be false on *every* failure path. A rejected result emitted under `success: true` is read as a success.
- Exit codes must distinguish categories consistently across commands, and across read and write paths.
- A requested output format (`--json`) must be honoured on error paths too, not only the happy one.
- For a tool an agent calls, the description and the field docs are the interface. What the caller has to already know to use it correctly is exactly what belongs there.

## Changing a published surface

- **Additive is cheap, everything else is coordinated.** Adding an optional field or a new call is usually safe unless a consumer deserializes strictly. Renaming, removing, retyping, tightening validation, or flipping a default is a coordinated change with a rollout, and it needs to know who the consumers are.
- **A default's *semantics* are part of the contract.** A client that never passed the parameter is depending on the current behaviour just as firmly as one that did.
- **Version when you cannot coordinate.** Two versions live at once is the normal state of a published API, so the design question is how long you carry the old one and what tells you it is safe to drop, not whether the transition is instant.
- **Documentation teaches the workflow, not the method list.** What to call first, what next, what the entry point is, and which assumptions are implicit (ID formats, enum values, required preprocessing).
