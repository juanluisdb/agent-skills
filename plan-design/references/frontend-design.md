# Frontend Design Prompts

Design-time frontend / web-platform prompts — decisions to make and questions to ask before implementing.

## Accessibility as design input

A11y belongs at design time, not as a retrofit.

- **Semantic HTML choice** — `<button>` for actions, `<a>` for navigation, `<nav>` / `<main>` / `<header>` / `<footer>`, headings in order. Decide the semantic structure *before* styling.
- **Focus order** — what's the keyboard tab sequence? Where does focus go after a modal closes / a route changes / a row is deleted / a submit succeeds?
- **Keyboard model** — every interactive element reachable with Tab/Shift+Tab; primary action on Enter/Space; menus and listboxes navigated with arrow keys. Custom widgets follow ARIA Authoring Practices patterns.
- **Screen-reader narrative** — what does assistive tech announce as the user moves through the UI? Plan the labels, live regions (`aria-live`), and roles up front.
- **Reduced-motion variant** — what's the still version of any animation? `prefers-reduced-motion` consumers see it.
- **Color-mode variant** — if dark mode is in scope, design tokens cover it from the start.

## Performance budget

Commit to numbers before writing the code.

- **LCP target** — what's the largest above-the-fold element? Budget: `< 2.5s` on a mid-range device with throttled network for a Good rating.
- **Bundle delta** — what does this feature add to the JS payload? Static-imported (joins the initial bundle) or dynamic-imported (lazy-loaded)?
- **INP-sensitive interactions** — which interactions need to feel instant? Budget: `< 200ms` from input to next paint for Good.
- **What goes dynamic?** PDF viewers, rich charts, rich text editors, code editors, video players, map libraries — default to dynamic import. These are first-paint killers when static.

## i18n model

If the product is or will be multilingual:

- **String catalog** — keys with English (or source-language) fallback, never raw user-facing strings in JSX.
- **Plural rules** — `Intl.PluralRules`. Russian has three forms, Arabic has six. `"1 item" / "N items"` is English-only thinking.
- **Numbers / dates / currency** — `Intl.NumberFormat` / `Intl.DateTimeFormat` with explicit locale + time zone.
- **RTL** — logical properties (`margin-inline-start`, `padding-inline-end`) over physical (`margin-left`, `padding-right`) wherever bidi matters.
- **Text expansion** — German / French can be 30–50% longer than English; design for it (no fixed-width text containers without overflow plan).

## Image & media strategy

For visual-heavy surfaces:

- **Formats** — AVIF / WebP with appropriate fallbacks; `<picture>` with `<source>` for negotiation.
- **Dimensions** — `width` / `height` attributes always; prevents CLS, hints aspect ratio before load.
- **Loading boundary** — above-the-fold gets `fetchpriority="high"` and eager loading; below the fold gets `loading="lazy"`.
- **Responsive** — `srcset` + `sizes` for varied viewports / DPRs.
- **Decoding** — `decoding="async"` on non-LCP images.

## Styling system

How does this feature look and theme?

- **Design tokens** — spacing / color / typography / radius / shadow from a system, not magic numbers. Tokens give one place to retune the entire system. What the values *should be* (scale, type system, colour discipline) is `visual-design.md`.
- **CSS-in-JS strategy** — runtime (emotion, styled-components) costs hydration time and INP; static extraction (vanilla-extract, Linaria, CSS modules) is zero-runtime. Decide per-project.
- **Theming hooks** — how does dark mode / brand variants flow through? Plan the system, not per-component overrides.
- **`!important` policy** — usually none. If you need it, the cascade is wrong.
- **Internal-wrapper boundary** — if the repo wraps an upstream UI kit / SDK with an internal module, app code uses the wrapper. Decide this convention up front.

## Routing model

For multi-page experiences:

- **Auth guards** — where does the guard run? Route loader, layout, or page-level? It must run *before* the protected page renders, not as an effect after mount.
- **Redirect placement** — in loaders or route guards, not in render (which causes re-render loops).
- **Prefetch strategy** — link-hover, in-viewport, or none? Bandwidth cost vs latency benefit.
- **URL state model** — what's in the URL (filters, tabs, IDs) vs what's local? See `react-design.md` § State boundary.

## Browser security at design time

Security decisions that belong at design, not review:

- **Token storage** — cookies (`HttpOnly` + `SameSite`) vs JS-readable storage. If XSS is in the threat model, JS-readable tokens are exfiltratable.
- **`postMessage` design** — origin allowlist decided up front; never trust `event.source`.
- **Untrusted URLs** — `href` / `src` / `Location` taking user-influenced URLs requires scheme + host allowlist. Block `javascript:`, `data:`, `vbscript:`.
- **`dangerouslySetInnerHTML`** — only with a sanitizer (DOMPurify or equivalent). If untrusted HTML is in scope, the sanitization layer is part of the design.
- **`target="_blank"`** — always with `rel="noopener noreferrer"`.

Cross-cutting security design (threat model, authn/authz, crypto, multi-tenancy) lives in `security-design.md`.

## Hydration & SSR (when applicable)

- **Mismatch sources** — `Date.now()`, `Math.random()`, `window` access, `localStorage` reads during render produce different server vs client output. Plan client-only escape paths.
- **Client-only widgets** — `useEffect` for setup; render `null` during SSR if needed; never interleave server-rendered content with `typeof window` checks deep in the tree.

## Motion & interaction design

Decide *whether* and *why* something moves at design time — the concrete curves, durations, and patterns live in `ui-polish.md`.

- **Should it animate at all?** Frequency decides: a thing triggered 100+ times/day should not animate; a rare/first-time moment has room for delight. Never animate keyboard-initiated actions (palette open, Enter-to-submit) — they must feel instant.
- **What's the purpose?** Spatial continuity, state, feedback, or softening a jarring jump. *"Looks cool"* is not a purpose for anything frequent — name the purpose or cut the motion.
- **Asymmetric enter/exit** — plan exits shorter and softer than enters; slow where the *user* decides, fast where the *system* responds. This is a design decision, not an implementation afterthought.
- **Reduced-motion variant** — see § Accessibility above; `prefers-reduced-motion` means gentler, not zero.

When a surface has real motion or visual-detail work, load `ui-polish.md` for the exact values.

## What good looks like

A frontend feature designed well at planning time produces:

- Semantic HTML scaffold decided before any styling
- Focus order, keyboard model, and screen-reader story documented
- LCP / INP / bundle-delta targets stated, not aspirational
- i18n / RTL / reduced-motion plans whenever the product needs them
- Image strategy explicit (formats, dimensions, lazy boundary)
- Styling system that scales (tokens, theme hooks, wrapper-boundary discipline)
- Routing model with auth guards in the right place and URL state designed