# Python Review Practices

Language-specific review guidance for Python codebases. Load this alongside the review checklist when reviewing Python code.

## Type Expressiveness

- **Prefer `StrEnum` over `Literal` string unions** — more extensible, centrally maintained, easier to grep, and plays well with serialization
- **Treat `dict[str, Any]` as a code smell** — use typed Pydantic models or TypedDict. Flag lossy typed-object → dict → typed-object round-trips
- **No untyped intermediates** — every variable in a data pipeline should have a known type. `Any` return types force callers to guess
- **`Optional[X]` must be intentional** — if None is never expected, don't accept it. If it is, handle it explicitly

## Pydantic Patterns

- **Field placement** — are fields at the right level of nesting? Does the structure imply relationships that don't exist?
- **Cross-field invariants** — enforce with `@model_validator`, not downstream code. Fail at construction, not deep in execution
- **Default values** — avoid defaults on fields that callers should always decide explicitly. Defaults silently mask intent
- **Breaking changes** — field renames, type changes, removed fields. Check serialization/deserialization compatibility

## Defaults & Parameters

- If a parameter is accepted, it must be stored and used. An ignored parameter with a default is a silent bug
- Avoid default values on function parameters that callers should always decide explicitly
- Trace every defaulted parameter: is the default safe for *all* callers, or does it paper over a decision?
- A field made `Optional` or a parameter given a default *only so existing tests keep passing* is a smell — fix the test to supply the value, don't loosen the contract. Test convenience is not a real caller need

## Exception Handling

- **Specific over generic** — `except ValueError` beats `except Exception`. Broad catches hide bugs
- **Missing vs overly defensive** — flag both. Missing handling for real failure modes is as bad as catching exceptions that can't happen
- **Handler return values** — can the handler's return be confused with a normal result? (e.g., returning `None` for both "not found" and "error")
- **`.get()` / `getattr()` with defaults** — only use when the missing-key case is real and intentional

## Memory & Resource Leaks (Long-Running Services)

Critical for any service that runs continuously (web servers, workers, daemons):

- **Instance accumulation** — objects appended to instance attributes, class-level collections, or module-level caches that are never pruned
- **Context-local storage** — `ContextVar`, `threading.local`, or similar that are set but never cleared after request completion
- **Missing cleanup in error paths** — `finally` blocks that don't cover all resources, especially in generators/async iterators
- **Reference cycles** — objects holding mutual references that prevent timely GC
- **Unclosed handles** — connections, sessions, file handles, temp files not cleaned up. Use context managers
- **Cleanup method completeness** — if `cleanup()` expects the caller to `flush()` first, the method is incomplete

## Composition & Design

- **Prefer composition over inheritance** — especially for complex hierarchies
- **Dependency injection** — pass dependencies as parameters, avoid global state
- **YAGNI** — don't add abstractions until a second use case exists
- **Imports** — check for circular imports introduced by new code. Verify all imports are used