---
name: implement
description: Build the code for a plan that already exists — decide the tests before writing, keep the happy path readable, and surface where the plan meets reality. Use when a plan, spec, ticket, or agreed approach exists and the work is to implement it.
---

# Implement

A plan exists and the job is to build it. Two things separate code that lands from code that comes back: the tests were decided before the code, and the happy path stayed readable.

## 1. Ground yourself

**The plan is whatever you were given.** A markdown doc, a ticket, a colleague's notes, an RFC, the conversation above. Plans arrive in every shape and none of them are wrong — read what exists and treat it as the spec rather than looking for a format it doesn't have.

**Read the code before writing any.** The call sites, the data flow, the conventions of the module you're about to change. A plan is written from outside the tree, so some of it is wrong in ways only the code shows, and finding that on the first file is cheap.

**Name what the plan doesn't say** — the tests, the failure paths, the rollout, the thing it assumed existed. Those gaps are yours to decide or to raise, and either is fine. Leaving them implicit is not: an unstated decision gets made anyway, silently, by whichever line you happen to write first.

## 2. Decide the tests before the code

This is the part of test-first work that pays, and the part usually skipped.

- **Take the cases from the plan when it names them.** When it doesn't, decide them now and say what they are before writing implementation. A case is a name, the input that drives it, and the observable outcome asserted — not "cover the parser". Check the list against the slice rather than against itself: every behaviour the plan or the ticket names has a case, or is explicitly out. When the list is what drives the build, a behaviour missing from it is missing from the product, and the suite is green either way.
- **Test at the boundary a caller uses.** If a test can only pass by reaching into internals, that's a signal about the shape of the code, not a licence to widen the interface.
- **One cycle per behaviour, not per function.** The unit is the thing the plan named, not each helper you happen to write on the way there.
- **Some behaviour is a property, not a list of cases.** A parser, a smart constructor, a state machine, a roundtrip, a normalization that must be idempotent — state the property and let generated input find the case you wouldn't have thought of: parse-then-render returns the input, normalizing twice equals normalizing once. One property often replaces the six examples you were about to enumerate.
- **On a large slice, write one failing test at the slice boundary and build inward.** It stays red through several internal steps, and that is correct rather than a problem to fix. Cycling test-code-test around individual functions inside a slice buys nothing and costs a full run each time.
- **See it fail for the right reason before the code exists.** One run, and read the failure: the assertion fired, and the expected-vs-actual is the one you predicted. An import error, a missing name, or a collection error is not red — it's a test that never ran, and you are the only observer of this step. This is what separates a test that describes intended behaviour from one retrofitted to whatever got built. A test that passes the moment you write it is either asserting nothing or the behaviour already exists — find out which before moving on.
- **The bar for whether a test earns its place:** delete the guarantee from the implementation. If the suite stays green, the test isn't pinning anything, and a test that pins nothing is pure maintenance cost.
- **Assert the invariant, not a proxy for it.** A count without what was counted, a set where order is the property that matters, a mock of the very thing under contract — each passes while the behaviour breaks.

In code that already exists:

- No seam to test at yet? Write a characterization test around current behaviour first, then change it. That test is the safety net for the change, and it can be deleted afterwards.
- In a flaky suite, a random red is not signal. Isolate a stable repro or say plainly that the suite needs attention.

## 3. Write the happy path first

The normal flow is most of what the code does at runtime, so it should be most of what a reader sees.

- **Top-level functions name the steps.** An orchestrator reads close to English: stop the server, install the version, verify it, start again. It does not own argument parsing, process spawning, protocol details, state surgery, or long validation branches — each of those goes behind a boundary named for what it owns.
- **Guard first, then run flat.** Invalid conditions leave immediately by return, raise, or assert. The valid path stays linear instead of nesting three conditionals deep.
- **Parse once at the boundary, then pass the trusted value.** Validating a raw value and passing that same raw value onward throws away what the check proved, so every layer below re-checks or silently trusts. Return a parsed domain value that cannot hold the invalid state, and let internal code receive something already true.
- **Make illegal states unrepresentable** where the language allows it. Mutually exclusive conditions belong in one tagged union, not three optional fields a reader has to correlate.
- **Deep boundaries, not helper shrapnel.** One operation whose interface hides real complexity beats three shallow helpers that force the reader to reassemble a single idea. If a name has to list what it does, it's several concepts.
- **Tell the owner of the state what to do.** Reading someone's state, deciding, and mutating it from outside spreads one invariant across two files.
- **Evidence before complexity.** No speculative safeguards, no theoretical race handling, no fallback chains, no options nothing sets. "Could", "might", and "what if" don't justify code — an observed failure does. When runtime later proves the case is real, fix the smallest failure at the boundary that owns it rather than building a general defence around one incident.
- **Follow the code you're in.** Local conventions win over your preferences; improve at the edges, not in the middle of someone else's module.

## 4. Comments

Default to none. A comment earns its place only by carrying a non-obvious *why*: a constraint, an invariant, surprising API behaviour, the reason a workaround exists.

Never write a caption restating the line below it, change history ("now uses X instead of Y"), or reviewer talk ("as requested", "NEW", "fixed"). Where a caption feels necessary above tricky code, rename the variable or function instead — the urge to explain is usually a naming problem.

Keep: suppressions with their reason (`noqa`, `type: ignore`, `eslint-disable`), TODOs that link a ticket, licence and generated-file headers, and public API documentation.

## 5. When the plan meets reality

The plan was written without the code in front of it, so some of it won't survive contact. When the tree contradicts the plan, stop and say so instead of improvising a way through. Name what you found, what it breaks, and the choice you'd make.

Improvising is the expensive failure here: the plan and the code silently diverge, nobody knows which one is true, and the gap surfaces at review time as a pile of findings that are really one unmade decision. Small mechanical differences you can absorb without a decision — a helper that already exists, a different file to put it in — just carry on.

## 6. Done means

- Every part of the plan's slice is built, not the easy parts with the rest noted as follow-ups.
- The tests you named run and pass, and you saw each of them fail first.
- A sweep over the whole diff for comments that don't earn their place, in one pass at the end rather than after each edit.
- Temporary artifacts gone: scratch files, debug prints, commented-out attempts.
- What you'd flag to a reviewer, said plainly: what the plan didn't cover, what you decided alone, what you're unsure about.
