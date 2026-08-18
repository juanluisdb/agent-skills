# Shipping and Running It

Everything between "the code is correct" and "the change is safe in production". These dimensions are invisible to a mock-based unit test and to a diff read on its own, which is why they are the ones that get dropped.

## It runs more than once

A unit of work that emits an external side effect or persists an accumulated value can run again: a retry, a resume after interruption, a reconnect, an at-least-once redelivery. Whether re-execution is safe is a different question from whether a single execution is atomic.

- **External side effects need a dedupe key stable across attempts.** Anything emitted outward, a payment, a published event, a notification, a downstream write, must carry a key derived from the *work* and not from the *attempt*, and the consumer must collapse on it. A key regenerated per attempt (a fresh UUID, a per-run timestamp) makes the same effect fire and count twice.
- **Wholesale replacement of a persisted aggregate loses prior attempts.** When completion writes an accumulated value by overwriting it, and the source resets per attempt, the stored value reflects only the last attempt. If the total should be cumulative across attempts, it has to be merged, not replaced.
- **Name the replay scenario and the guard.** The trigger only exists on the retry, resume, or redelivery path, which mock-based tests rarely exercise, so the scenario has to be stated deliberately: *what happens if this exact unit runs twice?*

## More than one state is live at once

A change that does not flip atomically has several states live simultaneously: a flag's off and on paths, old and new code during a rolling deploy, old and new schema mid-migration, two API versions in flight. Correctness is required in every coexisting state *and* in the transitional window where they overlap, not just the end state.

- **Treat "this is safe because `<condition>`" as a claim to verify.** Especially when the condition is global uniformity ("the flag is on for every tenant", "every caller is already on the new version"). That is an assumption about state you may not control, and it is usually decidable by looking at the flag dashboard or the deploy topology.
- **Records already persisted are a coexisting state.** Data written before the change is live state you cannot redeploy: stored rows, archived blobs, frozen message envelopes held in an external scheduler or queue. A newly-required field, or a hard read of a key the change introduces, breaks every record that predates it, either as an error on the read path or as a validation failure at consume time that drops the work.
- **Check the reverse direction.** A rollback leaves new-shaped records being read by the previous version. And check whether the operation that would migrate a legacy record forward is itself the one that breaks on it.
- **Migration pattern: additive first.** Add the new alongside the old, switch the readers, then remove the old. Never delete and replace under live traffic. The backfill is a step in the sequence with its own verification, not a footnote.
- **Rollout shape is a decision.** Feature flag, phased, dark launch, blue-green. Whichever it is, the rollback path is concrete steps, not "we can revert the change". If rollback needs a data fix, that fix is designed now.

## Contracts outside the change

The most expensive misses are correct-looking changes that depend on something *not in them* to land at the same time. The tests pass because they mock the missing piece, and the break shows on merge or in production.

- **Provisioned infrastructure that cannot change in place.** Reading a new field from a denormalized store, a projected index, a cache, or a search document only works if that store was provisioned to carry it. Some cannot be altered in place and must ship *ahead*. Otherwise the field reads as empty in production while every mock-based test passes.
- **A sibling change in flight.** Does this assume another open change's rename, or collide with one? Coordinate the merge order, or assert on something that survives both.
- **Out-of-change callers and tests that pin the old shape.** Renaming a value, index, or constant breaks tests and callers elsewhere. They are updated in the same change, or the mainline goes red the moment it lands.
- **External referencers that bind by convention rather than by import.** Deploy or infrastructure config keyed on a config or env-var *name*. Monitors, alerts, and metric filters keyed on a log *substring*. A downstream service that deserializes your payload, sometimes strictly, so an added field is rejected. A public or SDK client depending on the *current default semantics*. An analytics consumer reading an event or property *shape*. Renaming, rewording, reshaping, or default-flipping any of these is a contract change to a system outside the change. Who reads it that way, and was it confirmed rather than assumed?
- **A routing or allowlist step in another repository.** Emitting an event, exposing a route, or writing to a new index often needs a separate registration to reach its consumer: an event-bus type allowlist, a gateway route, a provisioned index. The emit succeeds, the local test is green, and the data is discarded downstream with no runtime signal. An in-repo "remember to add it" mirror is documentation, not routing.
- **Values that shift, not just names that change.** A metric or counter whose *value* steps up or down (a de-duplicated count, a re-based total) breaks static-threshold alerts and saved queries even though no name changed. Sign-off on a dashboard's interpretation does not cover alerting maths that lives outside the repository.
- **Read the deploy repository rather than accepting "provisioned everywhere".** When the change requires an environment variable, secret, config key, or index to exist, verify it for every target that runs the code, and note which targets inherit it indirectly. A required setting validated at import turns a missing value into a crash loop, and a control that is not wired cannot be used.

The question is: what else must change for this to work end to end, and does it land together?

## Multi-step external operations

When code modifies several external stores in sequence (a database and a cache, two APIs), the ordering decides what a mid-sequence failure leaves behind.

- Delete-then-create loses the old data if the create fails. Create-then-register orphans the resource if registration fails. Prefer create new, update the reference, delete old.
- **A transaction held open across a network call holds its locks for the remote system's latency.** The pooled connection and the locks live for someone else's timeout, and a slow dependency then surfaces as lock contention and pool exhaustion somewhere unrelated, only under load. Move the external call outside the transaction: commit first and emit with a stable dedupe key, or record the intent inside the transaction and publish from an outbox.
- **Durable machinery is earned, not defaulted to.** Plain calls or one database transaction cover a simple single-boundary operation. A saga or durable workflow is earned when progress must survive process loss or redelivery, or when the operation needs long delays, compensation, resumability, timers, human approval, cross-service coordination, or more than one transaction boundary. A short-lived retry on its own does not earn it.
- **Decide retry ownership in the same pass.** An adapter owns a safe short technical retry. The application decides whether the whole operation is attempted again. Only a durable workflow owns retries that must survive a crash or a redelivery.

## Failure classification

Every failure exit lands in one of two buckets: retry it, or give up on it. The two mistakes fail in opposite directions.

Retrying a deterministic failure burns attempts and ends as a terminal error anyway. Classifying a *transient* or *misconfiguration* failure as terminal produces a **silent drop**: the unit of work is acked, skipped, or logged and continued, with no retry, no dead letter, and no alert.

Watch for infrastructure statuses treated as a legitimate "nothing to do": a 404 from a misrouted endpoint, a 401 or 403 from a mispointed URL, throttling. And for a batch reporting zero failures while every item was skipped. The bar is that a systemic misconfiguration must not be able to present as a healthy no-op, so the drop is loud and the counters distinguish "nothing to do" from "could not do it".

## Observability

How the change behaves in production is visible only through what it emits, so the log and metric lines are designed, not bolted on afterwards.

- **Cover every terminal path, not just success.** Enumerate what the surface can reach: success, retries exhausted, mid-stream failure, cancellation. A counter emitted only on success, or a blanket cleanup block that always records success, undercounts exactly the failures the instrumentation exists to surface, and the dashboard looks healthy because the bad cases never logged. Check that the metric *name* matches what it counts.
- **Right level.** Developer detail at debug, normal lifecycle milestones at info, conditions an operator must act on at warning or error. An error on an expected handled condition cries wolf; a debug on a real failure hides it. Health-check pings and per-item hot-path lines at info are noise.
- **Log once, at the layer with the most context.** A failure logged where it is caught *and* re-logged by an outer handler produces several entries for one event. Do not both log and re-raise.
- **Actionable content.** A line that omits the identifiers needed to act on it is nearly useless. Which entity, which user, which request.
- **Consistent wording and keys** for the same event everywhere, so it stays greppable and alerts can match it. Decide the correlation identifiers up front and stamp them at the boundary.
- **Nothing sensitive.** No tokens, credentials, PII, or full request bodies. Note that a log call inside an exception handler can emit more than the fields passed to it: the logging layer may back-fill the live exception and its frames, and a validation library's message can embed the offending input verbatim. Capture the type and location in the handler, then log after the block exits.

## Guards that model a rule enforced elsewhere

A gate, validator, pre-flight check, lint rule, or drift test can be wrong in a way ordinary code cannot: it passes, everything looks healthy, and the thing it exists to catch sails through. Read the rule it mirrors at the source, then ask what failing case this check must reject.

- **Does the predicate match the real semantics?** Recurring shapes: keying on a value that is not what actually decides, reading one field of a multi-field switch, or ignoring the branch that is live precisely when the other is not. Each produces both a false positive on a valid config and a false negative on the broken one.
- **Does the pre-flight probe the surface it is checking?** A readiness, credential, or permission check that hits an endpoint which does not enforce the thing being verified returns "ok" for exactly the misconfiguration it was added to catch. Probe a surface that enforces the gate, and distinguish "verified bad" from "could not verify".
- **Does the drift guard compare the real artifact?** Comparing field names, or asserting each side against its own hardcoded copy, checks two self-consistent halves and not the contract between them. Validate the serialized payload the producer emits against the consumer's real definition. Permissive deserialization means the consumer silently discards whatever the producer added, so nothing fails until runtime.
- **Does the fix close the class or one instance of it?** After a mirror is repaired, ask whether the same "add it upstream and stop" mistake survives one layer down: a second lookup table, a per-variant map, an expected-type dictionary keyed on the same enum.

## Performance budgets

A performance requirement is three things: a number, the baseline it holds on, and the place that fails when it is exceeded. Drop any one and it stops being a requirement. "Should be fast" cannot regress, because nothing was claimed.

- **Commit to the number before writing the code,** while the shape is still open. A budget decided afterwards gets set to whatever the implementation happens to do.
- **The baseline is half the number.** A latency target means nothing without the load it holds at, and a client-side target means nothing without the device and network. State them: p99 at expected peak, or a mid-range phone on a throttled connection.
- **Name the enforcement point.** A budget checked by a person is a budget that drifts. It belongs in the pipeline, next to the tests, and the guardrail rules above apply to it: a check that runs nowhere protects nothing.
- **Browser surfaces have standard numbers** worth using rather than inventing: LCP under 2.5s, INP under 200ms, CLS under 0.1, plus a byte cap per route or entry point. The techniques that hit them (dimensions on media, dynamic imports for heavy viewers and editors, leaf imports over barrels, font-display, priority hints) are well known; the decision is the budget, and which surfaces are exempt.
- **Measure the thing the user waits for,** not the thing that is easy to instrument. A fast query behind a slow render, or a fast handler behind a slow queue, is a green metric on a bad experience.

## Resource lifecycle

In a long-running service a small per-request leak compounds into an out-of-memory under sustained load.

- Objects accumulated in instance attributes, class-level collections, or context-local storage that nothing clears. Missing cleanup in a finally block. Unclosed connections, sessions, or file handles.
- **Teardown is self-contained.** If a caller has to call one method before another to clean up correctly, the interface is leaking internal ordering.
