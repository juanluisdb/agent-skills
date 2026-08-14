# React Review Practices

Framework-specific review guidance for React codebases. Load alongside `typescript-review.md` when the diff touches `.tsx`/`.jsx`, hooks, or component code.

Opinionated. When generic TS rules and these overlap, this file provides the React-specific interpretation. Cross-cutting browser concerns (a11y, bundle, Web Vitals, browser security) live in `frontend-review.md`.

## Rules of Hooks

- **Hooks at the top level only** — never inside conditionals, loops, or after an early `return`. Conditional hooks shift hook indices between renders and silently scramble state
- **Custom hooks must `use*` prefix** — that's how the lint rule and React's runtime identify them as hooks
- **Exhaustive deps** — every reactive value referenced inside an effect / memo / callback must be in the dep array. Suppressing the lint with `// eslint-disable-next-line react-hooks/exhaustive-deps` is a finding unless the comment explains why the dep is intentionally excluded

## Render-Time Identity

Re-creating objects, arrays, or functions on every render breaks downstream memoization and causes effect re-runs.

- **Inline `{}`, `[]`, arrow functions as props** — new reference every render. Any memoized child (or hook with these in deps) sees them as "changed" every render
- **Inline component declarations** — `function Inner()` declared inside a parent component creates a *new component type* each render. React treats it as a different component and unmounts/remounts the entire subtree, throwing away its state
- **Module-scope first** — functions that don't close over component state belong at module scope. Same for objects, arrays, and constants

## Memoization Smell

`useMemo` / `useCallback` are not free — they add allocations, deps tracking, and reader friction.

- **Cargo-cult memoization** — wrapping every value in `useMemo` "to be safe" is a smell. Memoize only when you've measured an actual issue or you're stabilizing a reference for a downstream `React.memo` / hook dep
- **Primitive memoization is wrong** — `useMemo(() => count + 1, [count])` is more expensive than re-computing
- **Stale closures** — a `useCallback` with the wrong deps captures stale values. Reviewers should verify deps match every reactive reference inside
- **Prefer deriving over caching** — most "memoized" computations are cheap enough to run every render; cache only when profiling shows a problem

## Effect Lifecycle

- **Cleanup is mandatory** for timers, intervals, listeners, subscriptions, observers, animation frames, and `AbortController`s
- **Async effects need cancellation** — `useEffect(() => { let ignore = false; fetchX().then(d => { if (!ignore) setX(d) }); return () => { ignore = true } }, [...])` or an `AbortController`. Otherwise `setState` fires after unmount and on stale data when deps change mid-flight
- **Don't fetch in effects when a data lib exists** — React Query / SWR / RTK Query handle cancellation, dedup, retry, caching, and stale logic. Hand-rolled fetch-in-effect is a finding when a lib is already in the codebase
- **Effects are not lifecycle hooks** — flag `useEffect(() => { /* setup */ }, [])` that's really doing constructor work. Consider `useMemo`, derived state, or moving the work to event handlers / route loaders

## Refs

- **For DOM / imperative escape hatch only**, not for state. Mutating a ref doesn't re-render
- **Don't read `.current` during render** — refs may not match render output. Read in effects or event handlers
- **`useImperativeHandle` sparingly** — exposing imperative methods on a child is a strong coupling signal; declarative props are usually a better factoring

## Context

- **`value` must be stable** — passing `{ user, setUser }` as an inline object causes every consumer to re-render on every parent render. Memoize the value
- **Split contexts by update frequency** — auth state (rarely changes), theme (rarely changes), live cursor position (changes constantly) should not share a context. Consumers of slow-changing data should not re-render when fast-changing data updates
- **Context is not a state manager** — for global mutable state with selector-based reads, use a state library; context broadcasts every change to every consumer

## List Keys

- **Stable keys, never index** for lists that can reorder, insert, or delete in the middle. Index-as-key causes stale state and DOM in re-orderable lists
- **Duplicate keys** are silent bugs — React picks one to render and discards the others. Verify keys are unique across siblings

## Conditional Rendering Footguns

- **`array.length && <X/>`** renders `0` when the array is empty — `0` is falsy in JS but renderable in JSX. Use `array.length > 0 && <X/>` or a ternary with explicit `null`
- **`string && <X/>`** renders the string when truthy. Same fix
- **Ternary with explicit `null`** is the safest pattern for fall-through: `cond ? <X/> : null`

## Component Size & Decomposition

- **A component doing many jobs is a finding** — fetching, deriving, orchestrating, *and* rendering several distinct regions in one component means each concern is hard to test and reuse in isolation. Recommend extracting one responsibility per unit (a presentational child, a hook for the logic, a util for the pure transform)
- **A diff too large to review is itself a problem** — if a single component file grows so big that a reviewer can't hold it in their head, the right first step is "split this before we review further," not a line-by-line pass. Stacked `useState`/`useEffect`/`useMemo` at the top of one component is the usual tell
- **Extraction is a render boundary too** — pulling a heavy subtree into its own component is both a comprehension and a performance win
- **Feature-flag branching belongs at the composition boundary** — a component that reads a flag to decide whether to render itself carries the rollout in its own body, so it can't be tested or reused without the flag, and the flag's lifetime is invisible from the parent. Let the parent read the flag and conditionally render; the component stays flag-free. When the same surface already does this correctly elsewhere in the codebase, inconsistency between the two sites is itself the finding

## Component & Hook Typing

TS-React specifics not covered by the general TS reference:

- **`ComponentProps<typeof X>`** — for forwarding props to an existing component without redeclaring its shape
- **`PropsWithChildren<P>`** over manually adding `children?: React.ReactNode`
- **`forwardRef` typing** — generic ref-forwarded components are notoriously tricky; verify the generic is preserved through forwarding
- **Polymorphic `as` prop** — generic `as` typing usually needs `ElementType` + conditional types. If the diff adds one, scrutinize the type ergonomics — many implementations silently allow `as={"div"}` to accept invalid props
- **Event handlers** — `React.MouseEvent<HTMLButtonElement>`, not `any` or bare `Event`. The element generic narrows `e.currentTarget`
- **`e.persist()`** — leftover from synthetic-event pooling, removed in React 17+. Flag as dead code

## State Design

- **Derived state stored in state is a smell** — if `fullName` is derived from `firstName + lastName`, it should be computed (or `useMemo`'d if measured), not stored in `useState` and kept in sync via `useEffect`
- **Lift only as far as needed** — state lifted higher than necessary causes broader re-renders
- **URL state for shareable views** — filters, tabs, search queries, pagination belong in the URL when sharing/reloading matters
- **Reducer once interactions couple** — when multiple `useState` values must update together to maintain invariants, `useReducer` makes the invariants explicit

## Concurrent Features

- **`useTransition` / `startTransition`** for non-urgent updates — typeahead filtering, tab switches where the new tab is expensive
- **`useDeferredValue`** when consuming an expensive value derived from a fast-changing input
- **Suspense boundaries scoped to fetches** — a single top-level Suspense means one slow fetch blocks the whole tree

## Error Boundaries

- **Around async surfaces and third-party widgets**, not the whole app — a global boundary turns every render error into a full white screen
- **Fallback UI + telemetry** — the boundary should report the error somewhere and offer a recovery action
- **Not a substitute for proper error states** — explicit "request failed, retry" UI for known failure modes; the boundary is for unexpected crashes

## Data Fetching

When the codebase uses a query library (React Query, SWR, RTK Query):

- **Hierarchical query keys** — `["users", userId, "permissions"]` over flat strings. Enables targeted invalidation
- **Invalidate on mutation success** — every mutation should declare which query keys it invalidates; missing invalidation means stale UI after the mutation succeeds
- **Stale time per data type** — real-time data (seconds), user data (minutes), static config (hours). A single `staleTime` for everything is a smell
- **Centralized error mapping** — a single `displayError` (or equivalent) translates query/mutation errors to user-facing messages; scattered `error.message` rendering leaks internals
- **Suspense vs `isLoading`** — pick one per surface; mixing both produces double-loading-state UI
- **Don't mirror server state into local state** — copying fetched data into `useState` (then syncing it with an effect) forks the source of truth; the copy goes stale the moment the cache updates. Read from the query cache directly; keep `useState` for UI-only state
- **Cache write XOR invalidate** — a mutation either writes the cache optimistically *or* invalidates the affected keys, not both. Doing both is redundant and the manual write races the refetch it just triggered

## Loading / Empty / Error States

Any async UI must handle all three. The most common gap is **empty state** — the design covers "loading spinner" and "happy path with data" and forgets "request succeeded, list is empty".

For lists, mutations, and queries:

- **Loading** — visible feedback within ~100ms; skeleton or spinner
- **Empty** — a state that explains *why* and offers a next action (create, search, invite)
- **Error** — actionable message and a retry path

## Forms

- **Controlled vs uncontrolled** — controlled for validation-on-change; uncontrolled (`ref` based) for simple forms or large forms where every keystroke re-render is too costly
- **Validation timing** — on-blur for individual fields, on-submit for cross-field rules. On-change validation produces premature "this is invalid" while the user is still typing
- **Accessible errors** — `aria-describedby` linking the input to its error message, `aria-invalid="true"` on invalid fields. Color alone is not an accessible error indicator
- **Submit button state** — disabled during in-flight mutation; loading indicator inside the button; never let the user double-submit

## Testing

- **Selector hierarchy** — `getByRole(name)` > `getByLabelText` > `getByText` > `data-testid` > CSS selectors. Each step down is a regression in resilience and accessibility coverage
- **No `if` in tests** — set state explicitly through mocks / fixtures; tests should be straight-line and deterministic. Conditional logic in tests hides what's actually being asserted
- **Test user behavior, not internal state** — `expect(screen.getByText("Saved"))` over `expect(wrapper.state("saved")).toBe(true)`. Internal state assertions break on refactors that don't change behavior
- **Conditional JSX is invisible to V8 coverage** — `{x && <Y/>}`, ternaries in JSX, and early-return `if (!data) return null` are not always counted by V8-based instrumentation (used by Playwright and similar). If integration tests are the main test bed, conditional branches need supplementary unit tests for coverage
- **Mock at the network layer** — MSW or equivalent beats mocking the data lib; tests cover the same path production uses
- **Over-mocking signals the wrong level** — a test that mocks every collaborator exercises the mocks, not the integration; it's expensive to maintain and proves little. If a unit can only be tested by mocking everything around it, that's a hint the test (or the design) is at the wrong seam
- **Fewer, denser tests over many redundant ones** — collapse cases that assert the same behavior through a different path; one test per distinct behavior, not one per line. A reviewer should be able to name what each test uniquely protects
- **Don't test styling or framework internals** — asserting class names, inline styles, or that a library renders its own markup couples the test to implementation and breaks on cosmetic refactors. Test the behavior a user observes