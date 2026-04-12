# TypeScript Review Practices

Language-specific review guidance for TypeScript codebases. Load this alongside the review checklist when reviewing TypeScript code.

Opinionated — strong defaults with noted exceptions. When the review checklist and this file overlap, this file provides the TS-specific interpretation.

## Strict Mode

- **`strict: true` is the baseline** — if the project doesn't have it, that's a finding. Without it, the type system is lying to you
- **`noUncheckedIndexedAccess: true`** should be on — array/object index access returning `T` instead of `T | undefined` is a lie
- Flag any tsconfig loosening (`skipLibCheck`, `any`-permissive options) and ask why it exists

## Type Precision & Narrowing

- **Narrow over wide** — `"success" | "error"` over `string`, `42` over `number`, specific tuple over `any[]`. If the set of values is known, the type should reflect it
- **`as const` for literal preservation** — prefer `as const` objects over enums. Enums have quirks (reverse mapping, numeric enums, not erasable). `as const` + `satisfies` gives you the best of both: literal types with shape validation
  - Exception: string enums are fine when the codebase already uses them consistently, or when interop requires it (ORMs, codegen). Don't rewrite working enums for ideology
- **`satisfies` over `as`** — `satisfies` validates without widening. `as` asserts without checking. Prefer `satisfies` when you want to ensure a value matches a type while preserving literal inference
- **Discriminated unions for state modeling** — `{ status: "loading" } | { status: "success"; data: T } | { status: "error"; error: E }` over `{ status: string; data?: T; error?: E }`. Optional fields create impossible states; discriminated unions make them unrepresentable
- **Const type parameters** (`<const T>`) — use when you need to infer literal types from generic arguments without requiring `as const` at the call site

## Type Assertions & Escape Hatches

- **Every `as` is a claim the compiler can't verify** — flag each one. Ask: what's the real type? Can you narrow instead of assert?
- **`any` is a hole in the type system** — it infects everything it touches. `unknown` is almost always what you want. Flag `any` in function signatures, return types, and generic constraints
- **Non-null assertion (`!`)** — same as `as`: an unverified claim. Prefer narrowing with a guard or early return
- **`@ts-ignore` / `@ts-expect-error`** — `@ts-expect-error` is strictly better (fails when the error is fixed). But both deserve scrutiny: why can't the types express the reality?
  - Acceptable: working around a third-party library's broken types with a comment explaining the upstream issue
  - Not acceptable: silencing a real type error because modeling it correctly is hard
- **Type assertions in tests** — `as any` in tests is still a smell. Tests that bypass the type system aren't testing the real interface. Flag and suggest typed alternatives (proper mocks, builders, fixtures)

## Generics

- **Generics must earn their complexity** — a generic that's only ever instantiated with one type is noise. A generic that doesn't constrain anything (`<T>` with no `extends`) is suspicious
- **Prefer inference over annotation** — if TS can infer the generic, don't force callers to specify it. Good generics are invisible at the call site
- **Constrain meaningfully** — `<T extends object>` is almost as useless as `<T>`. What does the function actually need from `T`? Use `extends` with the minimal required shape
- **Avoid generic soup** — `<T extends Record<K, V>, K extends keyof T, V extends T[K]>` often means the abstraction is wrong. If you need a PhD to read the signature, the function is doing too much

## Runtime Validation at Boundaries

- **Types evaporate at runtime** — external API responses, user input, environment variables, file reads, query params, message queues. Any data entering the system from outside needs runtime validation, not just a type annotation
- **Validate then trust** — validate once at the boundary, use the validated type internally. Don't scatter validation checks through business logic
- **Environment variables are `string | undefined`** — `process.env.FOO` is not a `string`. Validate and parse at startup, export typed config. Never access `process.env` deep in business logic
- **JSON.parse returns `unknown`** — if your code does `JSON.parse(x) as MyType`, that's an unvalidated assertion. Validate after parsing

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

## Module Design & Exports

- **Barrel files (`index.ts`) can hide costs** — re-exporting everything increases bundle size and creates circular dependency risks. In a barrel, every consumer pays for every export
- **Export what's needed, not what exists** — internal helpers, implementation types, and intermediate abstractions should stay unexported unless a consumer genuinely needs them
- **Circular dependencies** — TS handles circular imports better than Python, but they still cause initialization-order bugs and make the dependency graph unpredictable. Flag and suggest restructuring
- **Type-only imports** — use `import type { X }` for types that don't need a runtime presence. Reduces bundle weight and makes the import's purpose explicit

## Node-Specific

- **Streams need error handling** — a readable stream without an `error` listener will crash the process. Pipe chains need error handling on every stream, not just the last one
- **`process.exit()` skips cleanup** — pending I/O, open connections, incomplete writes. Prefer graceful shutdown patterns
- **Buffer handling** — `Buffer.from(untrustedString)` uses UTF-8 by default. When encoding matters, be explicit. When comparing buffers for security purposes (tokens, hashes), use `timingSafeEqual`
- **Event emitter memory leaks** — listeners added in request handlers but never removed accumulate. Flag `.on()` calls that should be `.once()` or that need cleanup in a teardown path
- **File descriptors** — same as Python's resource management: open handles in long-running services leak. Use `using` (explicit resource management) or try/finally patterns
