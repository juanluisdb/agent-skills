# Review Checklist

The dimensions that only a *diff* shows: what the change did to a tree that already worked. The design judgement they rest on is in the `software-design` skill, which every expert loads alongside this file. Load its references by their own conditions, and use them here rather than trading opinions.

From there, the dimensions an expert has to cover and the reference that holds each:

| Dimension | Reference |
|---|---|
| Module depth, the deletion test, seams, dependency classification, layering, duplication with a shared reason | `modules.md` |
| The interface being wider than the signature, defaults and ignored parameters, error models, consumer experience, machine-consumer envelopes | `interfaces.md` |
| Type and model shape, illegal states, parse-once at the boundary, divergent sources of truth, changing a shape that already has data | `state.md` |
| Trust boundaries, injection, authn versus authz, secrets, PII, tenancy, crypto | `security.md` |
| What a test actually pins, mocked contracts, mutation, retired tests, whether the guardrail runs | `testing.md` |
| Idempotency and replay, coexisting states, out-of-diff dependencies, migration ordering, failure classification, observability, mirrored guards | `operations.md` |

Work through the dimensions below systematically as well. Not every one applies to every diff. Skip those that clearly do not, but do not skip one because it requires deeper investigation.

## Overly Defensive Code

Look for: broad `except Exception`, `.get()`/`getattr()` where `KeyError`/`AttributeError` is not a real possibility, fallback defaults that paper over unexpected states. These patterns hide bugs rather than surface them. Flag the specific call and explain what real scenario it could be masking.

## Correctness

Logic errors, off-by-one, wrong conditionals, mismatches between documented and actual behavior, missing edge cases (None/null, empty collections, boundary conditions), race conditions, incorrect state management.

**Merge hygiene.** Verify the diff doesn't silently drop code from a botched merge. Run `git diff <base>..HEAD | grep "^-.*\(def \|class \)"` and check every removed definition: is it intentional (mentioned in the MR description) or does it still have callers? Symbols deleted by a bad merge resolution pass type-checking and unit tests when callers mock the service, surfacing only at runtime as `AttributeError`. This is a bug class code-reading alone misses — the grep is the check.

## Exception Handling

Missing try-catch for real failure modes, incorrect error propagation, swallowed exceptions. Distinguish from overly defensive code: flag *missing* handling here, flag *unnecessary* handling under "overly defensive code". Trace every `except` path — does each branch either handle or re-raise? Can the handler's return value be confused with a normal result?

**The caught type must match what the body actually raises.** A `try` whose body can raise `KeyError`/`TypeError` under an `except ValueError` doesn't handle that case — the error escapes the handler unchanged. This is most dangerous when the handler exists to *guarantee* something (a structured error response, a skip-and-continue, a rollback): the guarantee silently holds only for the narrow type caught, and the other failure modes bypass it. Trace what each line in the body can throw and confirm the `except` covers it — widen the clause, or raise the type the handler expects.

Whether each failure exit is classified as terminal or transient, and whether a misconfiguration can present as a healthy no-op, is in `operations.md` § Failure classification. It is one of the highest-yield checks on any diff that consumes or dispatches work.

## Stale Base & Divergent Target

Triggered when Phase 1's base-freshness triage flags overlap. A diff is reviewed against its base, but it *merges* into the target's **current** head. The danger isn't the conflict itself (git announces that) — it's that a careless "take ours / take theirs" silently drops one side's semantics, usually regressing a change already shipped on the target. Invisible to a diff-only read and to unit tests passing on the stale base.

- **Reconstruct intent on the target side.** For each overlapping commit (`git log <target> ^<merge-base> -- <file>`), read its message and diff: what did it introduce — a new gate, a renamed constant, a tightened invariant?
- **Name what a wrong resolution erases.** State the specific target-side behavior a "take ours" would drop. *That* is the finding: not "this will conflict" but "resolving it wrong regresses X."
- **Point at the guard.** Identify the test that pins the at-risk behavior, so the rebase can be verified rather than eyeballed.

Flag as blocking: rebase onto the target, resolve *semantically* (keep both intents), re-run that test. Detect and name — don't resolve here.

## Architecture & Design

The criteria are in `modules.md`: depth, the deletion test, adapter count, where the variance lives, whether the thing needs to exist at all. What this dimension adds is the reviewer's licence to use them on the change as a whole.

Challenge fundamental decisions — even late in review, identifying a design problem is better than not. Architecture findings are often exploratory; mark them DESIGN or SUGGESTION unless small and immediately actionable.

Before reviewing *how* a change is built, ask whether it needs to exist at all: a speculative abstraction, a config nobody sets, a layer with one caller, an option for a case that may never come. The cheapest code to maintain is the code never written, so a warranted-by-nothing addition is a DESIGN question, not cleanup of code assumed necessary.

## Performance & Resource Management

Inefficient algorithms, unnecessary loops, N+1 queries, blocking calls. For systems with fan-out patterns, consider how data scales through parallel workers and consolidation phases.

Look for **memory and resource leaks**: objects accumulated in instance attributes, class-level collections, or context-local storage that are never cleared; missing cleanup in `finally` blocks; reference cycles preventing GC; unclosed connections, sessions, or file handles. In long-running services, a small per-request leak compounds into OOM under sustained load.

Check that **cleanup/teardown methods are self-contained**: if a caller needs to call `flush()` before `cleanup()`, the method is leaking internal teardown ordering.

## Dependencies

Outdated or unnecessary dependencies. New dependencies that pull in heavy transitive imports or conflict with existing ones. Before accepting a new dependency or a hand-rolled utility, walk the ladder in `modules.md` § Does it need to exist, and name the function or feature that replaces it. Supply-chain checks (advisories, provenance, install scripts, lockfile) are in `security.md`.

## Naming & Readability

Clear intent, consistent conventions, unused code, unclear variable names. Complex nested logic that should be broken up.

**Guard clauses over a nested valid path.** Invalid conditions should leave immediately — early return, raise, assert — so the valid path stays flat and linear. Flag the inverse: the real work buried three conditionals deep, with the failure cases implied by what happens after the closing braces. The rewrite is mechanical and usually removes lines.

**Magic literals.** A string or number literal that carries meaning (a status value, a limit, a key, a provider name) and is referenced in more than one place — or is non-obvious even once — should be a named constant. Flag repeated raw literals and unexplained magic numbers.

## Dead Code Shipped

Code added by the diff that nothing consumes. Distinct from "unused code that predates the change" — this is *newly shipped* dead weight a reviewer should catch before it lands. Check for: exports nothing imports, types/interfaces no longer referenced (often left behind when a field replaces them), values computed and returned but never read by the caller, parameters accepted and discarded, and helpers added "for later." Each is either removed now or, if intentionally ahead of a consumer, annotated with a TODO referencing the follow-up.

## Docstring & Comment Drift

When a diff changes a function's behavior, the docstring/comment/field-description that documents it is part of the change. A doc that still describes the old behavior is a finding, not a nitpick — a stale docstring is worse than none, because it actively misleads the next reader.

- Verify docstrings, inline comments, and public schema/field descriptions match what the body now does. If the diff drops a branch or flips a status code, the prose above it must follow.
- When the same shape or rule is described in two places — two code paths, a model and its projection, a schema field and its comment — confirm they actually agree. Divergent descriptions of one contract drift silently and send the next debugger chasing a phantom.
- **An unqualified guarantee the code only conditionally holds is a finding, not a nitpick.** "The row is terminal here", "this is always present", "converges on re-run" — each is load-bearing for the next reader's reasoning, and each is often true for only one path (the in-stream failure, the post-migration record, the update case). A comment asserting an invariant the code doesn't hold will misdirect the next debugger, so scope it to the case that holds, or state the precondition it depends on.
- **One rationale restated in several places is a drift risk.** The same "why" copied across four docstrings, a banner comment, a field description, and a doc page will not be updated in all six. Keep the full rationale in one canonical spot and leave a one-line contract at the others — the repetition also buries the genuinely non-obvious note next to it.
- **A comment that explains the code by naming a mechanism the same diff deletes is worse than none.** After removing a call site, helper, or repair path, grep the prose for it: a docstring pointing at a symbol that no longer exists sends the next reader looking for it instead of reasoning about what's there. Describe the invariant, and leave the history to the doc or ticket that keeps it.
