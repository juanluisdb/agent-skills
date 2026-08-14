# React Design Prompts

Design-time React prompts — questions to ask and shapes to consider before writing components.

## State boundary

Where does each piece of state live? Cheapest decision to make early, expensive to undo later.

- **URL state** — anything shareable / bookmarkable / back-button-friendly: filters, tabs, search queries, pagination, selected item ID. If reload-shareable matters, it goes in the URL.
- **Server state** — fetched data. Lives in the query lib's cache, not component state. Don't mirror it into `useState` — that creates two sources of truth.
- **Context** — cross-cutting but stable values (auth, theme, feature flags). Memoize the value or pay re-render tax on every consumer. Split by update frequency.
- **Local** — UI-only state that doesn't outlive the component (input draft, hover, open/closed, animation).

Lift only as far as needed. State lifted higher than necessary broadens re-renders and couples unrelated children.

## Data fetching strategy

How does this surface get its data?

- **Which library?** React Query, SWR, RTK Query, or hand-rolled — pick one for the surface, don't mix.
- **Query key hierarchy** — `["users", userId, "permissions"]` over flat strings. Enables targeted invalidation later. Plan the key shape with the data, not later.
- **Mutation → invalidation map** — every mutation declares which queries it invalidates. Plan this with the mutation, not as cleanup.
- **Suspense vs `isLoading`** — pick one per surface. Mixing produces double-spinner UI.
- **Optimistic update story** — when does the UI assume success before the server confirms? What's the rollback if the server rejects?
- **Polling / live data** — needed? `staleTime` / `refetchInterval` configured against the data's actual volatility.

## Render boundaries

What are the units of re-render?

- **What's a memoized leaf?** Pure, frequently-rendered, expensive — candidate for `memo`. Most components aren't. Memoize when measured, not preemptively.
- **What's its own component?** Anything reused, anything with independent state, anything visually-distinct enough to deserve a name. Components are also a perf boundary — extracting a heavy subtree is a render fence.
- **What needs concurrent features?** `useTransition` for expensive non-urgent updates (typeahead filtering, tab switch with heavy content); `useDeferredValue` for derived values from fast-changing inputs.

## Loading / empty / error stories

Every async surface needs all three, designed up front.

- **Loading** — visible feedback within ~100ms. Skeleton (when the shape is predictable) or spinner (when it isn't).
- **Empty** — explains *why* the list/result is empty (no data yet, filtered out, never created) and offers a next action (create, search, invite, adjust filter). The most commonly missed state.
- **Error** — actionable message and a retry path. Generic "Something went wrong" is a finding.

If the design only covers loading + happy path, it's incomplete.

## Form model

If this surface accepts input:

- **Controlled vs uncontrolled** — controlled for cross-field validation and dynamic UI; uncontrolled (refs) for simple forms or perf-sensitive large forms.
- **Validation timing** — on-blur per field, on-submit for cross-field rules. Avoid on-change (premature "invalid" while user is still typing).
- **Accessible error pattern** — `aria-describedby` linking the field to its message, `aria-invalid="true"` on bad fields. Plan the markup, not just the styling. Color alone is not an accessible indicator.
- **Submit state** — disabled during in-flight, loading indicator inside the button, idempotent submission (no double-submit bugs).

## Composition pattern

How do components compose? Pick one for the feature and apply consistently.

- **Slots / children** — flexible, composable, harder to constrain. Good when the consumer needs freedom.
- **Render props** — when the parent needs to render with child-owned state.
- **Compound components** — when a UI primitive has multiple coordinated pieces (`<Tabs><Tabs.List/><Tabs.Panel/></Tabs>`). Good for design systems.
- **Hooks as the API** — when the logic is reusable but the UI varies. Headless components live here.

Mixing patterns within a feature creates cognitive overhead. Pick the one that fits the primary use case.

- **Decompose up front, not after it sprawls.** Sketch the component tree before writing it: which units render a distinct region, own independent state, or get reused. A single component that fetches, derives, orchestrates, and renders several regions is a design smell *before* it's written — plan the split (presentational children, a hook for the logic, a util for the pure transform) rather than letting one file accumulate stacked `useState`/`useEffect`/`useMemo`.

## Solved-component mismatches

Planning-time tells that a feature is about to rebuild something already solved. Each is a cue to take the library rung of the build-vs-borrow ladder, not a style preference:

- **A `div`-based dropdown, dialog, or menu with hand-written focus handling** — focus trapping, restore-on-close, escape and outside-click dismissal, and ARIA semantics *are* the difficulty, and they fail late.
- **Hand-built toasts** — stacking, timers that pause when the tab is hidden, swipe-to-dismiss, and smooth interruption when several arrive at once.
- **A thousand-plus rows rendered directly** — virtualization before pagination workarounds.
- **A number animated by re-rendering the text** — digit-level transitions need a component built for them.
- **A `useState` web threaded through props to share state** — a store, or state relocated to the URL / server cache (§ State boundary).
- **A `className` ternary three conditions deep** — a class-composition util, or a typed variant API if the component genuinely has variants (size, intent, state).
- **A custom verification-code input, date picker, or combobox** — keyboard, paste, autofill, and locale behaviour run far deeper than they look.

Read `package.json` before naming a library and prefer what's already there. If the repo wraps a UI kit in an internal module, the wrapper is the boundary app code uses.

## Effect discipline

Plan effects rather than reaching for `useEffect` reflexively.

- **Does this need an effect, or is it derived state?** Computing from props/state is not an effect — it's a value or `useMemo`.
- **Does this need an effect, or is it an event handler?** Reacting to a user click is the handler's job, not an effect's.
- **Does this need an effect, or is the data lib already doing it?** Fetching in `useEffect` when React Query / SWR is in the codebase duplicates work and skips cancellation/dedup/cache.
- **What's the cleanup?** Listeners, timers, subscriptions, observers, async cancellation. Plan teardown alongside setup.

## Routing & navigation (when applicable)

- **Auth guards** — where do they run? Route loader, layout, or page-level effect? Must run *before* the protected page renders.
- **Route-level data loading** — does the data fetch on navigation, or after the page mounts? Loaders avoid waterfalls.
- **URL state model** — what's in the URL vs in local state? See State boundary above.
- **Prefetching** — link-hover or in-viewport prefetch for next-likely routes.

## What good looks like

A React feature designed well at planning time produces:

- State at the right level (URL / server / context / local), not duplicated
- Query keys hierarchical, invalidation map planned with each mutation
- Loading + empty + error designed for every async surface
- Components that have one job and one re-render reason
- Effects only where there's no better mechanism (event handler, derived state, route loader)
- Composition pattern picked and applied consistently