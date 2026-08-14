# Review Checklist

Work through each dimension systematically. Not every dimension applies to every diff — skip those that clearly don't apply, but don't skip a dimension just because it requires deeper investigation.

## Overly Defensive Code

Look for: broad `except Exception`, `.get()`/`getattr()` where `KeyError`/`AttributeError` is not a real possibility, fallback defaults that paper over unexpected states. These patterns hide bugs rather than surface them. Flag the specific call and explain what real scenario it could be masking.

## Type Design

Are types expressive and complete? Flag `dict[str, Any]`, untyped intermediates, `Any` return types, and `Literal` string unions that should be enums. If a well-typed object gets serialized to an untyped dict and re-wrapped into a typed model, flag the lossy round-trip.

**Boolean blindness.** A bag of correlated booleans and optional fields standing in for a lifecycle (`is_sent` / `is_paid` / `sent_at` / `paid_at`) permits combinations the domain forbids and forces every reader to re-derive the state machine from field names. A tagged union or an explicit status makes the illegal combinations unconstructable. Flag behaviour-controlling boolean *parameters* too — `create_user(input, True)` carries no meaning at the call site, and the second flag added beside it multiplies the modes silently; a named option or domain type reads at the call site and stays readable when a third mode arrives. Booleans returned by predicates are fine.

## Models & Data Contracts

Changes to domain models, DTOs, DB schemas/ORM models, enums, type definitions, constants. For each: Is the shape correct? Are fields at the right level of nesting? Does the structure imply relationships that don't exist? Are there breaking changes or backward compatibility concerns?

## Interface Contracts

Do function names match their actual parameters and return types? Does the public API surface make intent clear? Any breaking changes to call sites not visible in the diff?

**The interface is wider than the signature.** Everything a caller must know to use the code correctly is part of the contract: the invariants it upholds, the ordering constraints between its calls, the error modes it can raise, the configuration it requires, and the performance characteristics callers lean on. Each of those can change while the types stay byte-identical — a function that now raises where it used to return an empty list, one that must be called after an `init` it didn't need before, a setting that becomes required, a call that quietly turns into N calls. Those are breaking changes with no type diff to catch them, so read the body for them and check whether the callers and the docstring were updated too.

## Module Depth & Seams

Whether the change's new structure earns its place. A **deep** module hides a lot of behaviour behind a small interface; a **shallow** one has an interface nearly as complex as its implementation, so callers pay almost the full cost anyway. Two checks settle this instead of trading opinions about it:

- **The deletion test.** Imagine deleting the new module and inlining it at every call site. If complexity vanishes, it was a pass-through and the indirection was all it added. If the same complexity reappears at N callers, it was earning its keep. Run it on each wrapper, façade, manager, or helper the diff introduces — *"is this a good abstraction?"* has no answer, this does.
- **One adapter means a hypothetical seam. Two adapters means a real one.** A port, interface, protocol, or injection point with a single implementation is indirection, not decoupling: one more layer to read through, no substitution bought. Two implementations (production plus test, or two real providers) make the seam real. Flag the speculative one, and flag the diff that adds a seam where nothing varies.
- **An internal seam promoted into the interface.** A member made public, a helper exported, or a parameter added *only* because a test reaches for it turns the module's private structure into a contract it now has to keep. The interface is the test surface: if a test can only work by reaching past it, that's a signal about the module's shape, not a licence to widen it.

## Out-of-Diff & Coordinated-Change Dependencies

The most expensive misses are correct-looking diffs that depend on something *not in the diff* to land with them. Unit tests pass (they mock the missing piece) and the break only shows on merge or in production. Ask, for any change to a shape, name, or stored field:

- **Provisioned infrastructure that can't change in place.** Reading a new field from a denormalized store, a projected index, a cache, or a search doc only works if that store was provisioned to carry it. Some can't be altered in place (e.g. a secondary-index projection) and must ship *ahead*. A diff that reads the field but never updated the provisioning returns null/empty in production while every mock-based test passes.
- **A sibling in-flight MR.** Does this change assume another open MR's rename/refactor, or will it collide with one? Coordinate merge order or assert on something that survives both — otherwise whichever lands second leaves master red.
- **Out-of-diff tests/callers that pin the old shape.** Renaming a value, index, or constant breaks tests and callers elsewhere that assert the old name. Grep for who pins it and update them *in the same MR*, or CI on master goes red the moment this lands.
- **External referencers that bind by convention, not by import.** Some consumers depend on your surface through a contract no repo grep or unit test can see: deploy/infra config keyed on a config/env-var *name*, monitors/alerts/metric-filters keyed on a log *substring*, a downstream service that deserializes your payload (strictly — an added field can be rejected), a public/SDK client depending on the *current default semantics*, an analytics dashboard reading an event/property *shape*. Renaming, rewording, reshaping, or default-flipping any of these is a contract change to a system outside the diff. Ask who reads it that way and whether it was confirmed, not assumed.
- **A routing/allowlist step in another repo.** Emitting an event, exposing a route, or writing to a new index often needs a *separate* registration to reach its consumer (an event-bus type allowlist, a gateway route, a provisioned index). The emit succeeds, the local mirror-set test is green, and the data is discarded downstream with no runtime signal. Confirm the companion change exists and is deployed per environment, and treat an in-repo "remember to add it" mirror as documentation, not routing.
- **Values that shift, not just names that change.** A metric or counter whose *value* steps up or down (a de-duplicated count, a re-based total) breaks static-threshold alerts and saved queries even though no name changed. Owner sign-off on a dashboard's interpretation doesn't cover alerting math that lives outside the repo — ask explicitly.
- **Read the deploy repo, don't accept "provisioned everywhere."** When a change requires an env var, secret, config key, or index to exist, verify it in the deploy/GitOps repo for every target that runs the code, and note which targets inherit it indirectly. A required setting validated at import turns a missing value into a crash loop; a control that isn't wired can't be used.

The check is "what else must change for this to actually work end-to-end?" — and verify those land together.

## Stale Base & Divergent Target

Triggered when Phase 1's base-freshness triage flags overlap. A diff is reviewed against its base, but it *merges* into the target's **current** head. The danger isn't the conflict itself (git announces that) — it's that a careless "take ours / take theirs" silently drops one side's semantics, usually regressing a change already shipped on the target. Invisible to a diff-only read and to unit tests passing on the stale base.

- **Reconstruct intent on the target side.** For each overlapping commit (`git log <target> ^<merge-base> -- <file>`), read its message and diff: what did it introduce — a new gate, a renamed constant, a tightened invariant?
- **Name what a wrong resolution erases.** State the specific target-side behavior a "take ours" would drop. *That* is the finding: not "this will conflict" but "resolving it wrong regresses X."
- **Point at the guard.** Identify the test that pins the at-risk behavior, so the rebase can be verified rather than eyeballed.

Flag as blocking: rebase onto the target, resolve *semantically* (keep both intents), re-run that test. Detect and name — don't resolve here.

## Coexisting States & Staged Rollout

A change that doesn't flip atomically has **more than one state live at once** — a feature flag's off and on paths, old and new code during a rolling deploy, old and new schema mid-migration, two API versions in flight. Verify the change is correct in *every* coexisting state and in the transitional window where they overlap, not only the end state.

Treat any "this is safe / a no-op because `<condition>`" as a claim to verify, not context to accept — especially when the condition is global uniformity ("the flag is on for every tenant," "every caller is already on the new version"). That's an assumption about state the author may not control, and it's usually empirically decidable (check the flag dashboard, the deploy topology) — so verify it rather than forwarding the question.

**Records already persisted are a coexisting state too.** Data written before this change is live state you cannot redeploy: stored rows, archived blobs, frozen message envelopes held in an external scheduler or queue. A newly-required field, or a hard read of a key this change introduces (`row["new_key"]`), breaks every record that predates it — as a 500 on the read path, or as a validation failure at consume time that drops the work. Check the old-code-reads-new-data direction as well (a rollback leaves new-shaped records being read by the previous version), and check whether the operation that would migrate a legacy record forward is itself the one that breaks on it.

## Silent Defaults & Ignored Parameters

Check every function parameter with a default value: is the default truly safe for all callers, or does it silently mask a decision the caller should make? Trace the parameter — is it actually stored and used, or accepted and discarded? An ignored parameter with a default produces no error at the call site, making it one of the hardest bugs to catch in review. For models with conditionally-required fields, check that cross-field invariants are enforced at construction, not downstream.

**Don't loosen a contract for tests.** A parameter made optional or given a default (`= None`, `| None = None`) only so existing tests or callers keep compiling is a smell — the default encodes "the tests don't pass this," not a real caller need. Fix the test to supply the value and keep the parameter required. Test convenience is not a contract requirement.

## Multi-Step External Operations

When code modifies multiple external stores in sequence (DB + cache, two APIs, etc.), check the ordering for atomicity and recoverability. If step N fails, is data left consistent? Common anti-patterns: delete-then-create (old data lost if create fails), create-then-register (orphaned resources if registration fails). Prefer: create new, update reference, delete old.

**A transaction held open across a network call.** When a database transaction wraps an HTTP request, a queue publish, or a call into another service, the locks and the pooled connection it holds live for the *remote* system's latency and timeouts. A slow dependency then surfaces as lock contention and pool exhaustion somewhere that looks unrelated, and only under load. Flag the pattern and check whether the external call can move outside the transaction boundary: commit first and emit with a stable dedupe key, or record the intent inside the transaction and publish from an outbox.

## Idempotency Under Retry & Resume

A unit of work that emits an external side effect or persists an aggregate can run **more than once** — a retry, a resume after interruption, a reconnect, an at-least-once redelivery. Whether re-execution is safe is a separate question from whether a single execution is atomic (above).

- **External side effects must be idempotent under replay.** Anything emitted outward — a payment or payout, a published event, an email/notification, a downstream write — must carry a dedupe key that is *stable across re-executions* of the same logical unit, and the consumer must collapse on it. A key regenerated per attempt (a fresh UUID, a per-run timestamp) makes the same effect fire and count twice. Trace the key back to something derived from the work, not from the attempt.
- **Wholesale-replace of a persisted aggregate loses prior attempts.** When completion writes an accumulated value by overwriting (`state = this_attempt`) and the source resets per attempt, the persisted value reflects only the *last* attempt — diverging from any cumulative ledger fed incrementally. Check whether the stored total should be cumulative across attempts and, if so, that it's merged, not replaced.
- **The trigger is invisible to a diff-only read** — it surfaces only on the retry/resume/redelivery path, which mock-based tests rarely exercise. Name the replay scenario and the test that would catch a double-emit.

The check: *"what happens if this exact unit runs twice?"*

## Trust Boundaries & External Data Parsing

When data crosses a system boundary (external API response, storage deserialization, user input), check that parsing failures produce distinguishable, useful errors rather than crashing the operation or being silently absorbed. Partial results are usually better than total failure when processing a collection from an external source.

**Parse once, then pass the trusted value.** A check that validates a raw value and then hands that same raw value onward throws away what it just proved, so everything downstream either re-checks it or trusts it silently. Flag the shape `validate(x)` followed by a call still taking the untyped `x`: the boundary should return a parsed domain value — a model, a value object, a branded type — that cannot exist in the invalid state. Internal code then receives something already trusted instead of re-deriving the same guarantee at every layer, and the re-checks you delete are the ones that would have drifted.

## Correctness

Logic errors, off-by-one, wrong conditionals, mismatches between documented and actual behavior, missing edge cases (None/null, empty collections, boundary conditions), race conditions, incorrect state management.

**Merge hygiene.** Verify the diff doesn't silently drop code from a botched merge. Run `git diff <base>..HEAD | grep "^-.*\(def \|class \)"` and check every removed definition: is it intentional (mentioned in the MR description) or does it still have callers? Symbols deleted by a bad merge resolution pass type-checking and unit tests when callers mock the service, surfacing only at runtime as `AttributeError`. This is a bug class code-reading alone misses — the grep is the check.

## Exception Handling

Missing try-catch for real failure modes, incorrect error propagation, swallowed exceptions. Distinguish from overly defensive code: flag *missing* handling here, flag *unnecessary* handling under "overly defensive code". Trace every `except` path — does each branch either handle or re-raise? Can the handler's return value be confused with a normal result?

**The caught type must match what the body actually raises.** A `try` whose body can raise `KeyError`/`TypeError` under an `except ValueError` doesn't handle that case — the error escapes the handler unchanged. This is most dangerous when the handler exists to *guarantee* something (a structured error response, a skip-and-continue, a rollback): the guarantee silently holds only for the narrow type caught, and the other failure modes bypass it. Trace what each line in the body can throw and confirm the `except` covers it — widen the clause, or raise the type the handler expects.

**Terminal or transient — and does the code agree?** Every failure exit lands in one of two buckets: retry it, or give up on it. Classify each one and check the code's handling matches, because the two mistakes fail in opposite directions. Retrying a deterministic failure burns attempts and ends as a terminal error anyway; classifying a *transient* or *misconfiguration* failure as terminal produces a **silent drop** — the unit of work is acked, skipped, or logged-and-continued with no retry, no dead-letter, and no alert. Watch for infrastructure statuses (404 on a misrouted endpoint, 401/403 from a mispointed URL, throttling) treated as a legitimate "nothing to do", and for a batch that reports `failed=0` while every item was skipped. The bar: a systemic misconfiguration must not be able to present as a healthy no-op, so make the drop loud and keep counters that distinguish "nothing to do" from "could not do it".

## Cross-File Duplication & Divergent Sources of Truth

Before noting a new helper, grep for similar logic in adjacent modules. Traversal patterns, isinstance chains, and data extraction logic are common duplication sources. Watch for the same concept (enum, mapping, constant) defined independently in multiple places — these drift silently and produce inconsistent behavior.

**Two copies that don't change together aren't duplication.** Before flagging it, check the copies answer to the same reason for changing. Code that merely looks alike today will fight a shared helper the first time one caller moves, and the wrong abstraction costs more than the repetition did — so a duplication finding needs the shared *reason*, not the shared shape. Where the reason is genuinely one thing, the rest of this section applies.

**Prefer collapsing the duplication over detecting its drift.** A parity/drift test is the second-best answer: it converts a silent divergence into a CI failure, but it leaves two definitions to maintain and it only guards what it happens to compare. Ask first whether the two can be made unable to disagree (one shared definition, one derived from the other, construction with named arguments the type-checker verifies instead of an untyped splat). When a detector is genuinely the right call, it must compare the artifact that actually crosses the boundary — see *Mirrored Rules & Gates*.

## Mirrored Rules & Gates

A gate, guard, validator, lint rule, pre-flight check, or drift test is code that *models a rule enforced somewhere else*. It can be wrong in a way ordinary code can't: it passes, everything looks healthy, and the thing it exists to catch sails through. Read the rule it mirrors at the source, then ask what failing case this check must reject.

- **Does the predicate match the real semantics?** Recurring shapes: the gate keys on a value that isn't what actually decides (a specific priority number when the engine sorts by whatever is lowest; a pool's first entry when what matters is its size), or it reads one field of a multi-field switch (a flag's default variation without consulting whether the flag is *on*, so a legitimately-disabled config is reported as an error), or it ignores the branch that is live precisely when the other is not (the off-value a flag serves *while off*). Each produces both a false positive on a valid config and a false negative on the broken one.
- **Does the pre-flight probe the surface it's checking?** A readiness/credential/permission check that hits an endpoint which doesn't enforce the thing it's verifying returns "ok" for exactly the misconfiguration it was added to catch. Make it probe a surface that actually enforces the gate, and distinguish "verified bad" from "could not verify" instead of collapsing every non-success into one verdict.
- **Does the drift guard compare the real artifact?** Comparing field *names*, or asserting each side against its own hardcoded copy, checks two self-consistent halves and not the contract between them. Validate the serialized payload the producer actually emits against the consumer's real definition. Remember that permissive deserialization (ignore-extras) means the consumer silently discards whatever the producer added, so nothing fails until runtime.
- **Does the fix close the class, or one instance of it?** After a mirror is repaired, ask whether the same "add it upstream and stop" mistake survives one layer down — a second lookup table, a per-variant map, an expected-type dict keyed on the same enum. If it does, the class isn't closed.

## Architecture & Design

Coupling, separation of concerns, SOLID principles. Challenge fundamental decisions — even late in review, identifying a design problem is better than not. Architecture findings are often exploratory; mark them SUGGESTION unless small and immediately actionable.

Before reviewing *how* a change is built, ask whether it needs to exist at all — a speculative abstraction, a config nobody sets, a layer with one caller, an option for a case that may never come. The cheapest code to maintain is the code never written; flag a warranted-by-nothing addition as a DESIGN question, not just cleanup of code assumed necessary.

**Does the top-level function read like the use case?** An orchestrator's job is to name the steps, so it should read close to English: stop the server, install the version, verify it, start again. Flag one that owns the mechanics instead — argument parsing, process spawning, protocol details, state surgery, long validation branches. The happy path is most of what the code does at runtime and should be most of what a reader sees; when it is buried under machinery the fix is to push each mechanic behind a boundary named for what it owns, not to add comments explaining the flow.

**Count the edit sites the next case needs.** When adding the next variant — a new type, status, provider, mode — forces parallel edits at several sites (a new `if`/`isinstance`/`switch` branch, *plus* a new entry in each of several maps, *plus* a new helper), the variance is scattered instead of owned. The cost compounds: every future variant repeats the shotgun edit, and a missed site is a silent gap. Flag it as DESIGN — invert so each variant owns its own behavior or data (polymorphic dispatch, a registry, a field on the type), making the next case a single localized edit. This is the forward-looking counterpart to the duplication smell above: duplication is the same logic copied *now*; this is the same edit forced *every time* the set grows.

## Ambient Dependencies & Import-Time Work

A dependency the interface never declares binds the code to something a caller can't see and a test can't replace. Each one surfaces later as a test that can only be written by patching the world.

- **Ambient time and randomness.** `datetime.now()`, `time.time()`, `uuid4()`, or a random choice called deep inside logic. Flag it when the value is load-bearing — an expiry, a dedupe key, a scheduling decision, a retry window — and ask for an injected clock or random source, or an explicit `now` passed in. The symptom is a test that must freeze global time to assert a business rule.
- **Import-time side effects.** A module that starts a server, opens a connection, builds a client, reads env, or registers a handler at module level runs that work for everyone who imports it, including the test collector and unrelated tooling. Flag module-level statements that perform I/O or construct something with dependencies; that work belongs to the entrypoint that owns the process.
- **Mutable module-level state.** A runtime-mutated singleton leaks between tests and between requests, and nothing owns its lifecycle. Constants and pure lookup tables are fine; a cache, a registry filled at import or first use, or a client swapped per environment is shared mutable state with no owner.

## Security

Weight this lens heavier when the change crosses trust boundaries, touches auth/authz, handles secrets, processes external input, or widens permissions.

**Key questions:**
- What input is attacker-controlled, indirectly controlled, or easier to influence than the code assumes?
- Where does untrusted data cross into templates, shell commands, file paths, queries, URLs, deserializers, or privileged operations?
- Are *both* authentication and authorization enforced, or is the code only checking identity?
- Does the change widen permissions, expose new data, or make sensitive actions easier to trigger?
- Are secrets, tokens, cookies, credentials, or user-linked data logged, cached, or returned too broadly?
- Do external requests allow SSRF-like behavior, unsafe redirects, or overly flexible destinations?
- Are defaults secure, or does omitted configuration quietly weaken protection?

**Common findings:** injection (SQL, XSS, command, template), hardcoded secrets, unsafe deserialization or dynamic evaluation, auth bypass, missing/misplaced authz, trusting client-provided identifiers or ownership claims, overbroad CORS / cookie / session / token scopes, sensitive data leaking through logs, errors, analytics, or debug output, permission changes without matching tests.

Focus on realistic abuse paths, not theoretical perfection. Internet-facing, multi-tenant, and admin-path changes are higher risk. When a concern is plausible but incomplete, surface the uncertainty instead of overstating it.

## Performance & Resource Management

Inefficient algorithms, unnecessary loops, N+1 queries, blocking calls. For systems with fan-out patterns, consider how data scales through parallel workers and consolidation phases.

Look for **memory and resource leaks**: objects accumulated in instance attributes, class-level collections, or context-local storage that are never cleared; missing cleanup in `finally` blocks; reference cycles preventing GC; unclosed connections, sessions, or file handles. In long-running services, a small per-request leak compounds into OOM under sustained load.

Check that **cleanup/teardown methods are self-contained**: if a caller needs to call `flush()` before `cleanup()`, the method is leaking internal teardown ordering.

## Logging & Observability

How the change behaves in production is visible only through what it logs. Review log statements as real code, not afterthoughts.

- **Right level.** `debug` for developer detail, `info` for normal lifecycle milestones, `warning`/`error` for conditions an operator must act on. An `error` on an expected, handled condition cries wolf; a `debug` on a real failure hides it. Health-check pings and per-item hot-path lines at `info` are noise.
- **Log once.** A failure logged where it's caught *and* re-logged by an outer handler — or logged and then re-raised into a handler that logs it again — produces several entries for one event. Log it at the single layer with the most context; don't both log and re-raise.
- **Actionable content.** A line that omits the identifiers needed to act on it ("Deletion failed") is nearly useless — include which entity, user, table, request. Conversely, drop lines that carry no diagnostic value.
- **Consistent wording & keys.** The same event should log with the same message and the same structured keys everywhere, so it stays greppable and dashboards/alerts can match it. Several near-identical messages that mean one thing ("API request validated" / "App request validated" / …) should converge to one.
- **No sensitive data** — tokens, credentials, PII, or full request bodies in logs (overlaps Security).
- **A log call inside an `except` block emits more than the fields you passed.** Two mechanisms, both invisible at the call site: the logging layer can back-fill the *live* exception and its frames (a formatter reading the current exception state, or an `exc_info` default), and a validation library's message can embed the offending input value verbatim. So a handler that deliberately logs only `error_type` still ships the failing connection string, the source lines, or the user's email at `warning`. The fix is the shape the code already uses elsewhere: capture the type/location in the handler, then log *after* the block exits, or catch the validation error separately and log only its type and field locations.
- **Cover every terminal path, not just success.** When a diff adds a metric/log/event meant to *measure* something, check that it fires on all outcomes — success, retries-exhausted, mid-stream raise, cancellation — not only the happy path. A counter emitted only on success, or a blanket `finally` that always records `outcome="success"`, silently undercounts exactly the failures the instrumentation exists to surface; the resulting dashboard looks healthy because the bad cases never logged. Also check the metric *name* matches what it counts (a "retry count" that increments on the terminal non-retried error overstates retries).

## Dependencies

Outdated or unnecessary dependencies. New dependencies that pull in heavy transitive imports or conflict with existing ones.

Before accepting a **new dependency or a hand-rolled utility**, walk the ladder: does the stdlib, the platform/framework, or an *already-installed* dependency already do this? A new dep for what a few lines of stdlib cover trades a long-term cost for a short-term convenience; hand-rolled code that reinvents the stdlib is the opposite smell. Name the function/feature that replaces it.

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

## Module & Layer Boundaries

Does an import cross a boundary the wrong way? A shared/platform-agnostic package pulling in a platform-specific dependency, a lower layer importing from a higher one, or an app reaching into another app's internals. Reusable code drifting into an app folder instead of the shared library is the same smell. A boundary-rule suppression (`eslint-disable`) is a flag, not a resolution.

## Testing

Coverage gaps for critical paths, test quality, determinism. Check whether new behavior is tested at all. When the same change is applied to multiple code sites, verify tests cover all sites — not just the first one encountered.

**Would the test fail if the behavior regressed?** A test that passes is worthless if it would *keep* passing after the guarantee it claims to protect is broken. Two recurring ways this happens:
- **It mocks the thing under contract.** If the load-bearing behavior is "the validator rejects stale keys before projection runs," a test that patches out the validator (or the whole conversion step) exercises the mock, not the guarantee — a refactor that removes the real check sails through CI. Mock the boundaries *around* the unit, not the unit's own contract; for an end-to-end guarantee, leave the collaborator real.
- **It asserts an incidental proxy instead of the invariant.** Comparing a `set` when *order* is the property that matters, asserting a label that's coincidental to the behavior, or pinning a count without pinning what was counted — all pass while the real mapping silently breaks. Assert the thing that would actually be wrong if the code were wrong.
- **It fakes an external contract with the code's own assumption of it.** When a test stubs an outside dependency (an API response, a queue message, a stored record) using the shape the code *assumes*, the test and the code share one guess — they agree by construction. A wrong assumption about the real contract (a field name, casing, an envelope key) then passes every test while production silently gets nothing. Pin boundary shape against a captured real sample or a contract test, not a mock authored from the same assumption the code makes.

**Prove it by mutation when reading leaves it open.** Reading a test tells you what it asserts, not what it would catch — but most of the time reading settles it, and a guarantee you cleared by reading gets one line saying so, not a run. Mutate the ones reading can't settle: the checks above are the cue (mocked collaborator, incidental proxy, faked contract, load-bearing value arriving as a parameter, no test feeding the input the fix targets). Delete or invert the one line the guarantee rests on, run the narrowest selection that covers it — not the whole suite, never with coverage — and require a failing test. A green run there *is* the finding; report the mutation and the result the way you'd report a benchmark. Grep for other tests touching the symbol before calling it unpinned, since a narrow selection can miss the test that pins it. Restore the file before your next read — other reviewers are reading the same tree.

**Pin the wiring, not just the function.** A test that passes the load-bearing value in as a parameter pins the *function*; the expression at the call site that computes that value is unpinned, and mutating it often leaves the whole suite green. This is common when mocks make the call-site value invisible (a bare `Mock()` whose every attribute is truthy). Find the single expression the fix rests on and require a test that drives the call site.

**Check the assertion's direction.** A containment or subset assertion (`derived <= source`, "every mirrored key exists upstream") stays true as the source of truth *grows*, so it cannot catch the drift that actually happens: someone adds a member upstream and stops. Invert it — enumerate the source, keep an explicit allowlist of deliberate exclusions, and require every other member to be accounted for downstream. Then a new member fails the test until someone classifies it.

**Verify the guardrail runs.** A test that exists but executes in no pipeline protects a laptop, not master. When the change leans on a drift test, contract test, or lint rule as its safety story, confirm that package is in the CI project set and reachable from the configured test paths, and that the suite is green *reproducibly* (not dependent on terminal width, colour, locale, wall-clock time, or ambient env vars).

When a fix is added specifically to handle a tricky input (multi-line content, an empty list, a boundary value), there must be a test feeding *that* input — otherwise the next person who simplifies the fix away passes CI.

**Did a refactor leave its superseded tests behind?** When a change merges pieces behind a new interface, the old tests that pinned those pieces individually now pin the implementation the change just decided to hide. They break on the next internal edit and get "fixed" by rewriting them, so the diff has doubled the maintenance cost instead of moving it. Replace, don't layer: tests at the new interface should have retired the old per-piece ones. Flag the tests that survived a structure they no longer describe, and the reverse case too — a new interface with no tests of its own, resting entirely on the old ones.

## Consumer Experience

Apply when the change adds or modifies a consumer-facing interface (public API, SDK, library, CLI, tool description, LLM-facing surface). Review from the consumer's perspective: "will they succeed on the first try?" Skip for purely internal changes.

**API surface & redundancy:** Are there methods returning near-identical schemas that could collapse to one + a parameter? Would the consumer know which method to call without reading source? Every additional signature is cognitive load — justify it.

**Failure modes:** Can the consumer distinguish "not found" from "no data" from "error"? Silent empty results are the worst failure mode. Are error messages actionable — do they tell the consumer what to do next, or just what went wrong? Is validation consistent across parameters?

**Machine consumers: the contract includes every exit path.** When the consumer is a program, a script, or an agent rather than a person, the envelope is the API and partial adherence is a bug. Check that a universal status field is false on *every* failure path (a rejected plan emitted under `success: true` is read as a success), that exit codes distinguish categories consistently across commands and across read *and* write paths, that a requested output format (`--json`) is honoured on error paths too rather than only the happy one, and that two distinct causes don't share one message — collapsing "no credential" with "credential provider unreachable" into "set your token" leaves a consumer that already set it with no path to recovery.

**Discoverability & workflow:** Does the documentation teach the workflow (what first, what next) or just list methods? Is the entry point obvious? Are there implicit assumptions (ID formats, enum values, required preprocessing)?

**Defaults & conventions:** Do defaults match the most common use case? Are parameter names self-explanatory, or do they leak internal naming? Are valid values for constrained parameters discoverable without reading source?

**Unnecessary friction:** Any steps the system could handle transparently that it's pushing onto the consumer? Any common multi-step patterns (A→B→C) worth a single-call shortcut?

Frame findings from the consumer's perspective ("a consumer calling this will..."). Usually SUGGESTION priority unless the issue will cause frequent consumer failures.