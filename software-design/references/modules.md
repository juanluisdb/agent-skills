# Modules, Seams, and Dependencies

The *shape* of a module: how much it hides, where its seam goes, what it depends on, and how that shape decides the test strategy.

## Vocabulary

Five terms, used exactly. They are defined here because the obvious alternatives are already taken: "boundary" means a trust, layer, or deploy line elsewhere in these references, and "component" / "service" carry framework baggage.

- **Module** is anything with an interface and an implementation. Deliberately scale-agnostic: a function, a class, a package, or a slice spanning several tiers.
- **Interface** is everything a caller must know to use the module correctly. Not only the signature: the invariants it upholds, the ordering constraints between its calls, the error modes it can produce, the configuration it requires, and the performance characteristics callers lean on. If a caller has to know it, it is interface, and changing it is a contract change even when no type moves.
- **Depth** is how much behaviour sits behind the interface, per unit of interface the caller has to learn. A **deep** module hides a lot behind a little. A **shallow** one has an interface nearly as complex as its implementation, so the caller pays almost the full cost anyway and the module bought them nothing.
- **Seam** is a place where behaviour can be swapped without editing in that place. *Where* the seam goes is a separate decision from what sits behind it, and worth making deliberately instead of inheriting it from the current file layout.
- **Adapter** is a concrete thing satisfying an interface at a seam. It names the role it fills, not what is inside: a large adapter can wrap a tiny implementation (an in-memory fake), a small one can wrap a big implementation (a real database repo).

## Depth checks

- **The deletion test.** Imagine deleting the module and inlining it at every call site. If complexity vanishes, it was a pass-through and the indirection was all it added. If the same complexity reappears at N callers, it was earning its keep. Run this on every wrapper, façade, manager, or helper: *"is this a good abstraction?"* has no answer, this does.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Do not put a port, an interface, a protocol, or an injection point somewhere unless something actually varies across it, usually a production adapter plus a test adapter, or two real providers. A single-adapter seam is indirection: one more layer to read through, no substitution bought.
- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small swappable parts; they just are not part of what callers learn. So a module has **internal seams** (private to the implementation, used by its own tests) as well as the **external seam** at its interface. Do not promote an internal seam into the interface because a test wanted it. A member made public, a helper exported, or a parameter added only because a test reaches for it turns private structure into a contract you now have to keep. The interface is the test surface: a test that can only work by reaching past it is a signal about the module's shape, not a licence to widen it.
- **What else can this hide?** For each method and parameter on the interface, ask what the caller had to learn to use it. Config a caller copies from the previous call site, an ordering rule (*"call `init` first"*), a raw error the caller must classify itself: each is interface the module could have absorbed.
- **Naming is the depth check you can do before writing code.** If the module needs a name listing what it does (`fetch_and_validate_and_cache`), the interface is several concepts, not one.

## Does it need to exist

Before asking how a module is built, ask whether it needs to exist at all: a speculative abstraction, a config nobody sets, a layer with one caller, an option for a case that may never come. The cheapest code to maintain is the code never written, and an addition warranted by nothing is a design question, not a cleanup.

The same ladder applies to a new dependency or a hand-rolled utility. Does the stdlib, the platform or framework, or an *already-installed* dependency already do this? A new dependency for what a few lines of stdlib cover trades a long-term cost for a short-term convenience; hand-rolled code that reinvents the stdlib is the opposite smell. Name the function or feature that replaces it.

## Where the variance lives

- **Does the top-level function read like the use case?** An orchestrator's job is to name the steps, so it should read close to English: stop the server, install the version, verify it, start again. A top-level function that owns the mechanics instead (argument parsing, process spawning, protocol details, state surgery, long validation branches) has buried the happy path, which is most of what the code does at runtime and should be most of what a reader sees. The fix is to push each mechanic behind a boundary named for what it owns, not to add comments explaining the flow.
- **Count the edit sites the next case needs.** When adding the next variant, a new type, status, provider, or mode, forces parallel edits at several sites (a new branch, *plus* an entry in each of several maps, *plus* a new helper), the variance is scattered instead of owned. The cost compounds: every future variant repeats the shotgun edit, and a missed site is a silent gap. Invert it so each variant owns its own behaviour or data (polymorphic dispatch, a registry, a field on the type), making the next case one localized edit.
- **Duplication is a shared reason to change, not a shared shape.** Code that merely looks alike today will fight a shared helper the first time one caller moves, and the wrong abstraction costs more than the repetition did. Two copies that do not change together are not duplication.

## Dependency categories

Classify every dependency the module needs. The category decides how the module is tested across its seam, which makes it a design decision rather than a test-writing detail, and classifying it early is what prevents landing on a design whose only testable form is "mock everything".

1. **In-process** is pure computation, in-memory state, no I/O. Always safe to put behind one deep interface and test directly through it. No seam needed.
2. **Local-substitutable** means the dependency has a real local stand-in that runs inside the test suite (an embedded build of the database, a temp or in-memory filesystem, a local emulator). Test against the stand-in. The seam stays internal: no port at the external interface, because nothing varies for callers.
3. **Remote but owned** is your own service across a network hop. Define a port at the seam: the deep module owns the logic, the transport is injected. Production gets the HTTP, gRPC, or queue adapter; tests get an in-memory one. The logic stays in one module even though it is deployed across two processes.
4. **True external** is a third-party service you do not control. Same shape as (3): inject a port, tests supply a mock. Here the mock is unavoidable, so pin its shape against a captured real response rather than the shape your code assumes, otherwise the test and the code share one guess.

Categories (3) and (4) each add a port and two adapters to build and maintain. That is real work: it belongs in the sequence, not in the margin.

**Port width is its own decision.** Define the port beside the module that needs it and in *that* module's language, not the provider's: `UsersForPasswordReset.findActiveByEmail(email)`, not a mirror of the database client's surface. Depend on the smallest capability the operation actually uses, and let one cohesive concrete adapter satisfy several such narrow ports. That is what keeps you out of both failure modes at once: the mega-repository every caller drags in whole, and the sprawl of one-method adapters. A port's inputs, outputs, and errors are domain types; raw rows, SDK objects, and framework values stay inside the adapter.

**Ambient time, randomness, and import-time work are dependencies that do not look like one.** Each binds the module to something its interface never declares, and each is discovered at test-writing time, when the shape is no longer free to change.

- **Ambient time and randomness.** `now()`, `time()`, a generated ID, a random choice called deep inside logic. It matters when the value is load-bearing: an expiry, a dedupe key, a scheduling decision, a retry window. Inject a clock and a random source into dependency-bearing modules, or pass `now` explicitly into pure ones. The symptom is a test that must freeze global time to assert a business rule.
- **Import-time side effects.** A module that starts a server, opens a connection, builds a client, reads env, or registers a handler at module level runs that work for everyone who imports it, including the test collector and unrelated tooling. That work belongs to the entrypoint that owns the process.
- **Mutable module-level state.** A runtime-mutated singleton leaks between tests and between requests, and nothing owns its lifecycle. Constants and pure lookup tables are fine; a cache, a registry filled at import or first use, or a client swapped per environment is shared mutable state with no owner.

## Layers and placement

- **Which package or layer does this belong in?** Decide before writing. Code shared across applications belongs in the shared library, not an application folder. A platform-agnostic package must not depend on platform-specific libraries. Getting placement right up front avoids the "move it to a lib later" churn and the boundary-rule suppressions that follow.
- **Imports cross boundaries one way.** A shared or platform-agnostic package pulling in a platform-specific dependency, a lower layer importing from a higher one, or one application reaching into another's internals are all the same error. A boundary-rule suppression is a flag, not a resolution.
- **The public surface is the consumer's view, not the implementation's.** Internal helpers, intermediate types, and abstractions stay unexported unless a consumer genuinely needs them.

## Test strategy from the shape

- **The interface is the test surface.** Callers and tests cross the same seam, so tests attach at the interface and assert observable outcomes through it. Wanting to test *past* the interface, reaching into internal state or importing a private helper, says the module is the wrong shape; it is not a reason to widen the interface.
- **Replace, do not layer.** When a refactor deepens a module, the tests that pinned the old shallow pieces one by one become waste as soon as tests exist at the new interface: they pin the implementation you just decided to hide, so they break on the next internal change and get "fixed" by rewriting them. Their deletion is part of the refactor. Work that adds a test layer without naming the layer it retires has doubled the maintenance cost.
- **Tests should survive internal refactors.** They describe behaviour, not implementation. If a test must change whenever the implementation changes, it is testing past the interface, which is the cheapest available check on whether the seam is where you think it is.
