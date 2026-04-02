# Python Review

Load this reference when reviewing Python code and the base `code-review` skill needs language-specific help.

## What To Watch

- Broad `except Exception` or fallback-heavy code that hides bugs instead of surfacing them
- Untyped or weakly typed interfaces such as `Any`, `dict[str, Any]`, and lossy typed-object to dict round-trips
- Optional values and defaults that silently widen behavior instead of making caller intent explicit
- Public functions whose names, parameters, and return types no longer match their real behavior
- Serialization and validation logic happening too late, after invalid state has already spread
- Hidden coupling through shared constants, duplicated mappings, or drift between Pydantic models, ORM models, and API payloads
- Resource handling that depends on callers remembering the right cleanup sequence

## Heuristics

- Prefer specific exceptions over generic ones.
- Prefer explicit models, enums, and typed structures over stringly or dict-heavy plumbing.
- Check whether accepted parameters are actually used.
- Look for backwards-compatibility issues in field renames, type changes, and shape changes.
- Verify tests cover the changed behavior, not only the happy path.
