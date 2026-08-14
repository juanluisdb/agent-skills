# TypeScript Design Prompts

Design-time TypeScript prompts — questions to ask and shapes to consider before writing code.

## Shape the domain first

Decide the data shape *before* writing the functions that operate on it. Most "type problems" later are shape problems now.

- **What states can this thing be in?** Model with discriminated unions if more than one. `{ status: "loading" } | { status: "success"; data: T } | { status: "error"; error: E }` over `{ status: string; data?: T; error?: E }`. Optional fields create impossible states; discriminated unions make them unrepresentable.
- **What IDs / values are in distinct spaces?** Brand them. `UserId` and `OrgId` both typed as `string` is a substitution bug waiting to happen. Same for currency units (cents vs dollars), sanitized vs raw user input, tokens vs opaque IDs.
- **What constants / lookup tables exist?** Prefer `as const` objects over enums for literal preservation and easier interop. `as const` + `satisfies` validates shape while preserving literal inference.
- **Is a boolean carrying state that isn't binary?** `{ isSent: boolean; isPaid: boolean; sentAt?: Date }` makes the reader correlate four fields to recover one lifecycle, and permits combinations the domain forbids. If the entity has states, that's a tagged union of them, each variant carrying only the data that state actually has.
- **Is a boolean parameter choosing behaviour?** `createUser(input, true)` says nothing at the call site, and the second flag added beside it multiplies the modes silently. Prefer a named option or a domain type: `createUser(input, { emailVerification: "skip" })`. Booleans returned by predicates (`isExpired(token)`) are fine — the smell is booleans as inputs and as stored state.
- **Where do switches over union types live?** Plan for exhaustiveness via `assertNever` so adding a new union member breaks the build at every site that switches on it.

## Boundary model

Where does untrusted data become trusted? Decide once, follow through.

- **What enters from outside?** API responses, env vars, user input, message payloads, file reads, query params, deserialized blobs.
- **What's the validation strategy?** Schema library (Zod, Valibot, Effect Schema), hand-rolled guards, or types-only (accepting the lie)? Pick per boundary; document the choice.
- **What's the validated type?** Plan the type that exists *after* validation — that's what business logic consumes. Raw `unknown` should not propagate beyond the boundary.
- **Schema as single source of truth.** If you pick a schema library, derive the static type from the schema (`z.infer<typeof Schema>`), don't hand-write a parallel `interface` next to it. Decide this at design time — choosing "schema + inferred type" vs "hand-written type + runtime guard" up front prevents two definitions of the same shape drifting apart later.
- **What happens on validation failure?** Reject with what error shape? Logged how? Surfaced where to the consumer?

## Error model

How does this code communicate failure? Pick a discipline and apply consistently.

- **Exceptions vs result types** — JavaScript throws, but a `Result<T, E>` style is sometimes worth the friction (composability, exhaustiveness, no invisible control flow). Don't mix paradigms in the same module.
- **Expected vs unexpected failure** — validation, not-found, permission-denied are expected; model them in the type. Null pointer on internal state is a bug; let it crash with a useful stack.
- **What does an actionable error look like?** "Expected `userId` to be a UUID, got '123abc'" beats "Invalid input." Plan the message shape, not just the error class.

## Observability

Decide what this code emits before writing it — logging bolted on afterward is noise; logging designed in is greppable and alertable.

- **What's logged, at what level?** Lifecycle milestones at `info`, actionable failures at `warn`/`error`, developer detail at `debug`. Don't plan an `error` log for an expected, handled condition, or an `info` log on a hot path.
- **What context rides every line?** Decide the correlation IDs / structured keys (request, user, entity) up front and stamp them at the boundary, so a log line is actionable without spelunking. A failure should be logged once, at the layer with the most context — not at every level it bubbles through.
- **Consistent message + keys** for the same event, so dashboards and alerts can match it. Never log tokens, credentials, or PII.

## Escape-hatch isolation

Some `as` / `!` / `any` will happen at integration boundaries (third-party types, codegen, DOM access). Decide *where* up front.

- **Where will escape hatches live?** A `boundaries/` module, a type-wrapper file, an isolated wrapper around the third-party API — somewhere reviewers can audit.
- **What's the cost-of-being-wrong on each?** A boundary cast that's wrong corrupts everything downstream. Isolate tightly; verify with a runtime check where stakes are high.

## Module shape

What's the public surface?

- **What's exported, what stays internal?** Export the consumer's view, not the implementation. Internal helpers, intermediate types, and abstractions stay unexported unless a consumer genuinely needs them.
- **Barrel or no barrel?** Barrels are convenient but pull bundle weight and risk circular deps. For libraries with curated APIs: yes. For app code: usually no — import from the leaf module.
- **Which package/layer does this belong in?** In a monorepo, decide placement before writing: code shared across apps belongs in the shared library, not an app folder; a platform-agnostic package must not depend on platform-specific libraries (a web+native-shared package can't import DOM/router/web-only deps). Getting placement right up front avoids the "move it to a lib later" churn and the boundary-rule suppressions that follow.
- **Type-only exports?** `export type` separates value and type concerns; required under `verbatimModuleSyntax` / `isolatedModules`.

## Inference policy

How much annotation does this module use?

- **Public API: annotated.** Return types on exports prevent silent signature drift at the source.
- **Internals: inferred.** Trust TS for locals; annotate only where inference would widen or destabilize.
- **`satisfies` for literal data.** Validates shape while preserving narrowest type. Use over `:` annotation for config objects, enum-like maps, route tables, theme tokens.

## Generic policy (when designing reusable code)

- **Generics earn their complexity.** A `<T>` that's only ever called with one type is noise. A `<T>` with no `extends` constraint is suspicious.
- **Constrain meaningfully.** `<T extends object>` is barely a constraint; `<T extends { id: string }>` is one. State what the generic actually needs from T.
- **Inference at call site** — good generics are invisible. If callers must write `f<MyType>(…)`, the design has friction.

## What good looks like

A TS module designed well at planning time produces:

- Domain types named after the *concept*, not the *implementation* (`Subscription`, not `SubRow`)
- Discriminated unions for any "this can be in N states" concept
- Branded types for any ID / amount / unit that shouldn't be substituted
- A single validation boundary per external input, with the validated type used downstream
- Errors modeled in the return type when expected, thrown when unexpected
- Escape hatches confined to named files, not scattered through business logic