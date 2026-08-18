# Data and State

Data outlives the code that wrote it. A function can be rewritten this afternoon; a stored shape has to be lived with, migrated, and read by code that no longer exists in the repo. That asymmetry is why the data shape is decided first and defended hardest.

## Shape the data before the functions

Most "type problems" later are shape problems now.

- **What states can this thing be in?** If more than one, that is a tagged union of them, each variant carrying only the data that state actually has. Optional fields create impossible states; a discriminated union or an explicit status makes them unconstructable.
- **Boolean blindness.** A bag of correlated booleans and optional fields standing in for a lifecycle (`is_sent` / `is_paid` / `sent_at` / `paid_at`) permits combinations the domain forbids, and forces every reader to re-derive the state machine from field names. Booleans returned by predicates are fine; the smell is booleans as stored state.
- **A boolean parameter choosing behaviour.** `create_user(input, True)` carries no meaning at the call site, and the second flag added beside it multiplies the modes silently. A named option or a domain type reads at the call site and stays readable when a third mode arrives.
- **Which values are in distinct spaces?** A `UserId` and an `OrgId` both typed as a bare string is a substitution bug waiting to happen. The same goes for currency units, sanitized versus raw input, and tokens versus opaque IDs. Give them distinct types where the language allows it.
- **Name the concept, not the storage.** `Subscription`, not `SubRow`. A type named after where it happens to live will be wrong as soon as it lives somewhere else.
- **Is the nesting right?** Fields at the wrong level of nesting imply relationships that do not exist, and a structure that implies a relationship will eventually be read as asserting one.
- **Untyped intermediates lose what was proved.** A well-typed object serialized to an untyped map and re-wrapped into a typed model is a lossy round trip with no error at either end.
- **Exhaustiveness is a design feature.** Where the language can make adding a variant break every site that switches on it, take it. That is the mechanism that stops a new state from being silently unhandled.

## Parse once at the boundary

Decide once where untrusted data becomes trusted, and follow through.

- **Enumerate what enters from outside:** API responses, environment variables, user input, message payloads, file reads, query parameters, deserialized blobs.
- **Pick the validation strategy per boundary** (a schema library, hand-written guards, or types-only, which is accepting the lie) and record the choice.
- **Plan the type that exists *after* validation.** That is what the logic consumes. An untyped or unknown value must not propagate past the boundary.
- **Validating and then passing the raw value onward throws away what the check proved.** The shape to avoid is `validate(x)` followed by a call still taking the unvalidated `x`. The boundary returns a parsed domain value that cannot exist in the invalid state, so nothing downstream re-derives the same guarantee, and the re-checks you did not write are the ones that would have drifted.
- **One schema, one definition.** If validation comes from a schema, derive the static type from the schema rather than hand-writing a parallel type beside it.
- **Decide what a validation failure produces.** Which error shape, logged where, surfaced how. When processing a collection from an external source, a partial result with distinguishable per-item errors usually beats total failure.

## One source of truth

- **The same concept defined independently in two places drifts silently.** An enum, a mapping, a constant, or a limit that exists in a model and again in its wire mirror, a config file, or a downstream copy will diverge, and the divergence surfaces as behaviour nobody can reproduce.
- **Prefer making the two unable to disagree** over detecting that they did: one shared definition, or one derived from the other. A parity or drift test is the second-best answer. It converts a silent divergence into a CI failure, but it leaves two definitions to maintain and guards only what it happens to compare.
- **Derived data needs a stated relationship to its source.** A cache, a denormalized column, a projected index, a search document, a materialized total. Say what invalidates it, what rebuilds it, and what the system does while it is stale, because "eventually consistent" without those three is just "sometimes wrong".
- **Two writers to one piece of state is a design decision, not an accident.** If there are two, name which one wins and what happens when they disagree.

## Where state lives

- **Push state to as few places as possible.** A component that holds no state can be restarted, scaled, retried, and tested without ceremony. Most of the difficulty in a system concentrates wherever state does, so concentrating it deliberately is what keeps the rest simple.
- **Someone owns each piece of state's lifecycle.** Who creates it, who mutates it, when it is cleaned up. State with no owner is the shape that leaks: accumulated in an instance attribute, a class-level collection, or a context-local that nothing clears.
- **Local state that is really shared is the expensive mistake.** In-process state that two replicas each hold their own copy of behaves correctly on one machine and wrongly on two, and the failure only appears under a topology change.

## Changing a shape that already has data

A schema, model, DTO, or stored payload change is a change to records you cannot redeploy.

- A newly-required field, or a hard read of a key this change introduces, breaks every record written before it.
- Check the other direction too: after a rollback, the previous version reads records written in the new shape.
- Check whether the operation that would migrate a legacy record forward is itself the one that breaks on it.

The ordering, the backfill, and the rollout that make such a change safe are in `operations.md`.
