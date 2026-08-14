# TypeScript Review Practices

Language-specific review guidance for TypeScript codebases. Load this alongside the review checklist when reviewing TypeScript code.

Opinionated — strong defaults with noted exceptions. When the review checklist and this file overlap, this file provides the TS-specific interpretation.

## Strict Mode

- **`strict: true` is the baseline** — if the project doesn't have it, that's a finding. Without it, the type system is lying to you
- **`noUncheckedIndexedAccess: true`** should be on — array/object index access returning `T` instead of `T | undefined` is a lie. Once enabled, every `arr[i]` and `record[key]` is `T | undefined`; flag every `!` papering over this rather than narrowing
- Flag any tsconfig loosening (`skipLibCheck`, `any`-permissive options) and ask why it exists

## Inference Discipline

- **Don't annotate what TS can infer** — `const name: string = "x"` widens the literal. Trust the inferer for locals; annotate only at function/module boundaries and public APIs where the inferred type would be unstable or expose too much detail
- **`const` vs `let` widening** — `const x = "foo"` is `"foo"`; `let x = "foo"` is `string`. Same value, different inferred precision
- **Return type annotations on exported functions** — let TS infer internally; annotate exports so signature drift is caught at the source rather than at every call site
- **`satisfies` over `:` annotation** when you want type-checking *without* widening the inferred literal type. Annotation widens; `satisfies` validates and preserves

## Type Precision & Narrowing

- **Narrow over wide** — `"success" | "error"` over `string`, `42` over `number`, specific tuple over `any[]`. If the set of values is known, the type should reflect it
- **`as const` for literal preservation** — prefer `as const` objects over enums. Enums have quirks (reverse mapping, numeric enums, not erasable). `as const` + `satisfies` gives you the best of both: literal types with shape validation
  - Exception: string enums are fine when the codebase already uses them consistently, or when interop requires it (ORMs, codegen). Don't rewrite working enums for ideology
- **`satisfies` over `as`** — `satisfies` validates without widening. `as` asserts without checking. Prefer `satisfies` when you want to ensure a value matches a type while preserving literal inference
- **Discriminated unions for state modeling** — `{ status: "loading" } | { status: "success"; data: T } | { status: "error"; error: E }` over `{ status: string; data?: T; error?: E }`. Optional fields create impossible states; discriminated unions make them unrepresentable
- **Const type parameters** (`<const T>`) — use when you need to infer literal types from generic arguments without requiring `as const` at the call site

## Exhaustiveness

- **`switch` over a string union is NOT exhaustive by default** — a missing case silently returns `undefined`. Add a `default: assertNever(value)` helper (`function assertNever(x: never): never { throw new Error("Unhandled: " + String(x)) }`) so a new union member breaks the build at every switch site
- **`satisfies never`** as an inline alternative for ad-hoc exhaustiveness on a discriminant
- **Prefer discriminated unions over `typeof` chains** for narrowing complex unions — a literal `kind` field handles exhaustiveness more reliably and produces clearer error messages

## Branded & Nominal Types

- **TS is structural** — `UserId` and `OrgId` both declared as `string` are interchangeable. The compiler will not catch passing one where the other is expected
- **Brand IDs that shouldn't be swapped**: `type UserId = string & { readonly __brand: "UserId" }` (or via a unique symbol). Construction goes through a single factory; downstream code accepts only the branded type
- **Worth it when**: distinct ID spaces, currency amounts that differ by unit (cents vs dollars), tokens/secrets that should never substitute for opaque IDs, sanitized vs raw user input
- **Cost**: one factory + one type alias per branded value. Effectively free; pays back the first time an ID gets swapped in a refactor

## Type Assertions & Escape Hatches

- **Every `as` is a claim the compiler can't verify** — flag each one. Ask: what's the real type? Can you narrow instead of assert?
- **`any` is a hole in the type system** — it infects everything it touches. `unknown` is almost always what you want. Flag `any` in function signatures, return types, and generic constraints
- **Non-null assertion (`!`)** — same as `as`: an unverified claim. Prefer narrowing with a guard or early return
- **`@ts-ignore` / `@ts-expect-error`** — `@ts-expect-error` is strictly better (fails when the error is fixed). But both deserve scrutiny: why can't the types express the reality?
  - Acceptable: working around a third-party library's broken types with a comment explaining the upstream issue
  - Not acceptable: silencing a real type error because modeling it correctly is hard
- **Type assertions in tests** — `as any` in tests is still a smell. Tests that bypass the type system aren't testing the real interface. Flag and suggest typed alternatives (proper mocks, builders, fixtures)

## Type Predicates & Assertion Functions

Two ways to teach the type system about a runtime check. Both are user-supplied guarantees — the compiler trusts the implementation.

- **`x is T` type predicate** — narrows in the branch where the predicate returns true. Use for guards in conditional logic: `if (isUser(x)) { /* x is User here */ }`
- **`asserts x is T` assertion function** — narrows for the *rest of the scope* after the call. Use for invariant checks at the top of a function: `assertIsUser(x); /* x is User from here on */`
- **The implementation is unverified** — `function isUser(x: unknown): x is User { return true }` compiles. Predicates and assertions are claims the reviewer must check against the actual logic, same as `as`
- **Prefer compiler-verified narrowing** when a structural check works: `if ("id" in x && typeof x.id === "string")` is verified; `isUser(x)` is not

## Generics

- **Generics must earn their complexity** — a generic that's only ever instantiated with one type is noise. A generic that doesn't constrain anything (`<T>` with no `extends`) is suspicious
- **Prefer inference over annotation** — if TS can infer the generic, don't force callers to specify it. Good generics are invisible at the call site
- **Constrain meaningfully** — `<T extends object>` is almost as useless as `<T>`. What does the function actually need from `T`? Use `extends` with the minimal required shape
- **Avoid generic soup** — `<T extends Record<K, V>, K extends keyof T, V extends T[K]>` often means the abstraction is wrong. If you need a PhD to read the signature, the function is doing too much

## Variance Footguns

- **Method syntax is bivariant; function-property syntax is contravariant** — `interface X { foo(x: T): void }` accepts `(x: SubT) => void` *and* `(x: SuperT) => void`. `interface X { foo: (x: T) => void }` honors `strictFunctionTypes`. Method shorthand silently widens what the type system enforces
- **`strictFunctionTypes` does not cover methods** — the historical reason is constructor and event-handler compatibility. Flag any callback type declared with method syntax where strict variance actually matters
- **Array and `ReadonlyArray` variance** — `Array<T>` is invariant in T's mutability story; `ReadonlyArray<T>` is covariant. Functions that only read should accept `ReadonlyArray`

## Runtime Validation at Boundaries

- **Types evaporate at runtime** — external API responses, user input, environment variables, file reads, query params, message queues. Any data entering the system from outside needs runtime validation, not just a type annotation
- **Validate then trust** — validate once at the boundary, use the validated type internally. Don't scatter validation checks through business logic
- **Schema is the single source of truth** — when a runtime schema (Zod, Valibot, etc.) already describes a shape, derive the static type from it (`z.infer<typeof Schema>`) rather than hand-writing a parallel `interface`. Two independently-maintained definitions of the same shape drift silently; the schema and the type must never be allowed to disagree. Flag a hand-written type sitting next to a schema for the same data
- **Environment variables are `string | undefined`** — `process.env.FOO` is not a `string`. Validate and parse at startup, export typed config. Never access `process.env` deep in business logic
- **JSON.parse returns `unknown`** — if your code does `JSON.parse(x) as MyType`, that's an unvalidated assertion. Validate after parsing
- **Don't let `unknown` propagate deep** — `unknown` is the right type at boundaries, but should be narrowed or parsed within a few lines. `unknown` arguments deep in business logic mean validation was deferred or skipped; the function is operating on values it can't reason about

## Error Handling

- **`catch` gives you `unknown`** — never assume the shape of a caught error. Narrow with `instanceof` or a type guard before accessing properties
- **Model expected errors in types** — if a function can fail in known ways, the return type or thrown error type should communicate that. A function that returns `T` but sometimes throws `NotFoundError` has an invisible contract
- **Distinguish expected from unexpected errors** — validation failures, not-found, permission denied are expected and should be handled. Null pointer on an internal object is a bug — let it crash with a useful stack
- **Error messages should be actionable** — "Invalid input" vs "Expected `userId` to be a UUID, received: '123abc'" — the second one is debuggable
- **Avoid `try/catch` around code that can't throw** — same as Python's "overly defensive code" dimension. Don't catch what can't fail

## Async & Promises

- **Unhandled promises are silent failures** — every `async` call must be `await`ed, returned, or explicitly fire-and-forget with a comment explaining why
- **Sequential vs concurrent** — `await a(); await b()` when `a` and `b` are independent is a serial bottleneck. Use `Promise.all`/`Promise.allSettled` for independent operations
- **`Promise.all` fails fast** — if one rejection shouldn't abort everything, use `Promise.allSettled` and handle mixed results
- **Async generators and cleanup** — same concern as Python: if an async generator is abandoned mid-iteration, `finally` blocks may not run. Ensure resources are cleaned up
- **Floating promises in callbacks** — `array.forEach(async (item) => ...)` doesn't await anything. Use `Promise.all(array.map(...))` or a sequential loop

## Immutability & Mutation

- **`Readonly<T>` for data that shouldn't change** — function parameters, config objects, shared state. Mutation bugs are hard to trace; `Readonly` makes them compile errors
- **`ReadonlyArray<T>` / `readonly T[]`** — when the array's contents and length shouldn't change. `.push()` on a shared array is a mutation bug
- **Avoid mutating function arguments** — if a function needs to transform data, return a new value. Mutation of inputs creates action-at-a-distance bugs
- **Spread vs mutation** — `{ ...obj, updated: value }` over `obj.updated = value` for objects that are passed around. But don't spread deep objects when a targeted `structuredClone` + mutation is clearer
- **`Readonly<T>` vs `as const`** — different operations, often confused. `Readonly<T>` is a *shallow* type-level transform (nested fields still mutable). `as const` is an *inference-time* directive that produces deep readonly literal types on inline expressions. Use `Readonly<T>` for function params; `as const` for literal data

## Module Design & Exports

- **Barrel files (`index.ts`) can hide costs** — re-exporting everything increases bundle size and creates circular dependency risks. In a barrel, every consumer pays for every export
- **Export what's needed, not what exists** — internal helpers, implementation types, and intermediate abstractions should stay unexported unless a consumer genuinely needs them
- **Circular dependencies** — TS handles circular imports better than Python, but they still cause initialization-order bugs and make the dependency graph unpredictable. Flag and suggest restructuring
- **Respect package/layer boundaries (monorepos)** — a platform-agnostic or shared package must not import platform-specific deps (a package shared across web and native can't pull in `react-router-dom`, `window`, DOM types, etc.); a lower layer must not import from a higher one. Flag the import that crosses the boundary the wrong way — an `eslint-disable` on a boundary rule is a smell, not a fix
- **Reusable code belongs in the shared lib, not an app** — when a util/component/hook in an app folder is (or will be) used by more than one app, it belongs in the shared library layer. A leaf app reaching into another app's internals is a layering violation
- **Type-only imports** — use `import type { X }` for types that don't need a runtime presence. Reduces bundle weight, makes the import's purpose explicit, and is *mandatory* under `verbatimModuleSyntax` / `isolatedModules` (used by Vite, esbuild, swc-based pipelines). Mixed value+type imports erase imperfectly and can break the bundle in some toolchains

## Node-Specific

- **Streams need error handling** — a readable stream without an `error` listener will crash the process. Pipe chains need error handling on every stream, not just the last one
- **`process.exit()` skips cleanup** — pending I/O, open connections, incomplete writes. Prefer graceful shutdown patterns
- **Buffer handling** — `Buffer.from(untrustedString)` uses UTF-8 by default. When encoding matters, be explicit. When comparing buffers for security purposes (tokens, hashes), use `timingSafeEqual`
- **Event emitter memory leaks** — listeners added in request handlers but never removed accumulate. Flag `.on()` calls that should be `.once()` or that need cleanup in a teardown path
- **File descriptors** — same as Python's resource management: open handles in long-running services leak. Use `using` (explicit resource management) or try/finally patterns