# Module Design Prompts

Design-time prompts for the *shape* of a module: how much it hides, where its seam goes, and how that shape decides the test strategy. Language-agnostic — the stack references cover stack-specific shape; this one is about depth and seams.

## Vocabulary

Five terms, used exactly. They're defined here because the obvious alternatives are already taken: "boundary" means a trust, layer, or deploy line elsewhere in these references, and "component" / "service" carry framework baggage.

- **Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, a class, a package, or a slice spanning several tiers.
- **Interface** — everything a caller must know to use the module correctly. Not only the signature: the invariants it upholds, the ordering constraints between its calls, the error modes it can produce, the configuration it requires, and the performance characteristics callers lean on. If a caller has to know it, it's interface — and changing it is a contract change even when no type moves.
- **Depth** — how much behaviour sits behind the interface, per unit of interface the caller has to learn. A **deep** module hides a lot behind a little. A **shallow** one has an interface nearly as complex as its implementation, so the caller pays almost the full cost anyway and the module bought them nothing.
- **Seam** — a place where behaviour can be swapped without editing in that place. *Where* the seam goes is a separate decision from what sits behind it, and worth making deliberately instead of inheriting it from the current file layout.
- **Adapter** — a concrete thing satisfying an interface at a seam. Names the role it fills, not what's inside: a large adapter can wrap a tiny implementation (an in-memory fake), a small one can wrap a big implementation (a real database repo).

## Depth checks

- **The deletion test.** Imagine deleting the module and inlining it at every call site. If complexity vanishes, it was a pass-through and the indirection was all it added. If the same complexity reappears at N callers, it was earning its keep. Run this on every wrapper, façade, or helper the design introduces — *"is this a good abstraction?"* has no answer, this does.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't put a port, an interface, or an injection point somewhere unless something actually varies across it — usually a production adapter plus a test adapter, or two real providers. A single-adapter seam is indirection: one more layer to read through, no substitution bought.
- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small swappable parts — they just aren't part of what callers learn. So a module has **internal seams** (private to the implementation, used by its own tests) as well as the **external seam** at its interface. Don't promote an internal seam into the interface because a test wanted it; that's how a public-for-testing member becomes a contract you're stuck keeping.
- **What else can this hide?** For each method and parameter on the interface, ask what the caller had to learn to use it. Config a caller copies from the previous call site, an ordering rule (*"call `init` first"*), a raw error the caller must classify itself — each is interface the module could have absorbed.
- **Naming is the depth check you can do before writing code.** If the module needs a name listing what it does (`fetch_and_validate_and_cache`), the interface is several concepts, not one.

## Dependency categories

Classify every dependency the module needs. The category decides how the module is tested across its seam, which makes it a design decision rather than a test-writing detail — and classifying it here is what prevents landing on a design whose only testable form is "mock everything".

1. **In-process** — pure computation, in-memory state, no I/O. Always safe to put behind one deep interface and test directly through it. No seam needed.
2. **Local-substitutable** — the dependency has a real local stand-in that runs inside the test suite (an embedded build of the database, a temp or in-memory filesystem, a local emulator). Test against the stand-in. The seam stays internal: no port at the external interface, because nothing varies for callers.
3. **Remote but owned** — your own service across a network hop. Define a port at the seam: the deep module owns the logic, the transport is injected. Production gets the HTTP/gRPC/queue adapter, tests get an in-memory one. The logic stays in one module even though it's deployed across two processes.
4. **True external** — a third-party service you don't control. Same shape as (3): inject a port, tests supply a mock. Here the mock is unavoidable, so pin its shape against a captured real response rather than the shape your code assumes — otherwise the test and the code share one guess.

Categories (3) and (4) each add a port and two adapters to build and maintain. That's real work: it belongs in the sequence, not in the margin.

**Port width is its own decision.** Define the port beside the module that needs it and in *that* module's language, not the provider's — `UsersForPasswordReset.findActiveByEmail(email)`, not a mirror of the database client's surface. Depend on the smallest capability the operation actually uses, and let one cohesive concrete adapter satisfy several such narrow ports. That's what keeps you out of both failure modes at once: the mega-repository every caller drags in whole, and the sprawl of one-method adapters. A port's inputs, outputs, and errors are domain types; raw rows, SDK objects, and framework values stay inside the adapter.

**Ambient time, randomness, and import-time work are dependencies that don't look like one.** `now()`, a generated ID, a mutable module-level singleton, and a module that opens a connection or reads configuration at import all bind the module to something its interface never declares. Each is discovered at test-writing time, when the shape is no longer free to change. Inject a clock and a random source into dependency-bearing modules, or pass `now` explicitly into pure ones. Keep side effects out of import: a module should not start a server, open a connection, read env, or register a handler merely by being imported — that work belongs to the entrypoint that owns the process.

## Test strategy from the shape

- **The interface is the test surface.** Callers and tests cross the same seam, so tests attach at the interface and assert observable outcomes through it. Wanting to test *past* the interface — reaching into internal state, importing a private helper — says the module is the wrong shape; it isn't a reason to widen the interface.
- **Replace, don't layer.** When a refactor deepens a module, the tests that pinned the old shallow pieces one by one become waste as soon as tests exist at the new interface: they pin the implementation you just decided to hide, so they break on the next internal change and get "fixed" by rewriting them. Plan their deletion as part of the refactor. A plan that adds a test layer without naming the layer it retires has doubled the maintenance cost.
- **Tests should survive internal refactors.** They describe behaviour, not implementation. If a test must change whenever the implementation changes, it's testing past the interface — which is the cheapest available check on whether the seam is where you think it is.