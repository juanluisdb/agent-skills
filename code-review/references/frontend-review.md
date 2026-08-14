# Frontend Review Practices

Web-platform and browser-environment review guidance. Load when reviewing browser-facing code — UI components, public pages, anything served to end users.

Generic to web frontends. Framework-specific React concerns live in `react-review.md`. Pure TS concerns in `typescript-review.md`. Cross-cutting security in `security-review.md`.

## Accessibility

- **Semantic HTML first** — `<button>` for actions, `<a>` for navigation, `<nav>`, `<main>`, `<header>`, `<footer>`, headings in order. Avoid div soup with `role` attributes
- **ARIA only to fill gaps** — `aria-label`, `aria-describedby`, `aria-live` when semantic HTML can't express the intent. Wrong ARIA is worse than no ARIA
- **Labels on every form control** — `<label for>`, `aria-label`, or `aria-labelledby`. Placeholder is not a label
- **Visible focus** — never `outline: none` without a replacement focus style. Keyboard users navigate by focus ring
- **Keyboard reach** — every interactive element must be reachable and operable with Tab/Shift+Tab/Enter/Space/Arrow keys. Custom widgets (combobox, menu, dialog) follow ARIA Authoring Practices patterns
- **Tap-target size** — ≥ 24×24 CSS pixels (WCAG 2.5.8); ≥ 44×44 is the iOS HIG recommendation for primary actions
- **Color contrast** — 4.5:1 for normal text, 3:1 for large text and UI components (WCAG 2.1 AA)
- **Honor `prefers-reduced-motion`** — disable or reduce animations for users who set the preference
- **Honor `prefers-color-scheme`** if the design has both themes

## Web Vitals

### LCP (Largest Contentful Paint)

- **Hero image** — explicit `width`/`height`, `fetchpriority="high"`, modern format (AVIF/WebP), no JS-dependent placeholder above the fold
- **No JS-blocking resources** in the critical path for above-the-fold content — async/defer scripts, prefetch fonts, inline critical CSS
- **Font loading** — `font-display: swap` or `optional`; avoid FOIT

### CLS (Cumulative Layout Shift)

- **Image / video dimensions present** — `width`/`height` attributes or aspect-ratio CSS prevent layout shift on load
- **Reserve space** for ad slots, async-loaded widgets, and late-arriving content
- **Font fallback metrics** — set `size-adjust`, `ascent-override`, `descent-override` to match fallback to web font
- **No content insertion above existing content** after the page is rendered — banners, cookie notices, "new message" toasts go below or overlay

### INP (Interaction to Next Paint)

- **Long event handlers** block the main thread — `requestIdleCallback` or `scheduler.postTask` for non-urgent work
- **No synchronous storage / layout reads** in hot handlers — `localStorage`, `getBoundingClientRect` in a tight loop, etc.
- **Debounce / throttle** for input-driven handlers (search, validation)

## Bundle Weight

- **Barrel imports pull heavy trees** — `import { x } from "./index"` may pull every export's transitive deps unless tree-shaking is perfect (it rarely is). Import from the leaf module when bundle weight matters
- **Dynamic import for heavy surfaces** — PDF viewers, rich charts, rich text editors, code editors, video players, map libraries. These are first-paint killers if static-imported
- **Tree-shake-friendly libraries** — flag full-library imports like `import _ from "lodash"` (use `lodash-es` and named imports), `import moment from "moment"` (use `date-fns` / `dayjs` / `Intl`), full icon packs (import single icons)
- **Polyfills** — only ship what the target browsers need; check the polyfill matrix against the actual browserslist

## Images & Media

- **`width` / `height` attributes** on `<img>` and `<video>` — prevents CLS, hints aspect ratio before load
- **Modern formats** — AVIF, WebP with appropriate fallbacks; `<picture>` with `<source>` for negotiation
- **`srcset` + `sizes`** for responsive images
- **`loading="lazy"`** for below-the-fold images
- **`decoding="async"`** for non-LCP images
- **`fetchpriority="high"`** on the LCP image; `"low"` on offscreen images

## Browser Security

Frontend-specific security patterns. (Cross-cutting security topics in `security-review.md`.)

- **`dangerouslySetInnerHTML` requires a sanitizer** — DOMPurify or equivalent, with an allowlist. Never render untrusted HTML directly
- **`target="_blank"` requires `rel="noopener noreferrer"`** — without it, the opened page can navigate the opener (reverse tabnabbing) and gets referrer leak
- **User-controlled URLs in `href` / `src`** need scheme validation. Block `javascript:`, `data:`, and `vbscript:`
- **`postMessage`** — always check `event.origin` against an allowlist. Never trust `event.source` alone
- **Token storage** — JS-readable storage (`localStorage`, `sessionStorage`) is XSS-exfiltratable; if the threat model allows XSS, JS-readable tokens are game over. Cookies with `HttpOnly` + `SameSite` preferred when the backend supports it
- **`window.open` / `window.opener`** — when opening untrusted URLs, set `opener` to null (`noopener`)
- **CSP** — content security policy headers and `<meta>` directives constrain inline scripts, eval, and external resources. Flag any `unsafe-inline` / `unsafe-eval` introduction
- **Mixed content** — HTTPS pages loading HTTP resources are blocked; flag any hardcoded `http://` URLs

## i18n & Localization

- **Strings live in a catalog, not literals** — translation keys with fallback text, never raw user-facing strings hardcoded in JSX
- **Plurals via `Intl.PluralRules`** — `"1 item" / "N items"` rules differ per locale (Russian has three forms; Arabic has six)
- **Numbers and dates via `Intl.NumberFormat` / `Intl.DateTimeFormat`** — locale, currency, time zone all matter
- **RTL considerations** — `dir="rtl"` flips margins, padding, transforms. Use logical properties (`margin-inline-start`) over physical (`margin-left`) for bidi-safe layouts
- **Text expansion** — German and French strings can be 30–50% longer than English; UI must accommodate without truncation

## Internal-Wrapper Boundaries

Generic principle, common pattern across mature codebases:

- If the repo wraps an upstream library (UI kit, telemetry SDK, feature-flag SDK, analytics, payment SDK) with an internal module, application code must use the wrapper, not the upstream package directly
- Reviewer signal: any direct import from the upstream package (e.g. `@mui/material`, `launchdarkly-react-client-sdk`, `@sentry/browser`) inside app code when an internal wrapper exists
- Wrappers exist for centralized configuration (theming, error reporting, telemetry tagging) — direct imports bypass that

## Styling

- **Design-token usage over magic numbers** — `theme.spacing(2)` / `var(--space-md)` over `16px`. Tokens give one place to retune the system
- **Runtime CSS-in-JS cost** — emotion / styled-components inject CSS at runtime, costing hydration and INP. Static extraction (Linaria, vanilla-extract) or CSS modules are zero-runtime alternatives
- **Ergonomic prop systems** (`sx`, `css` prop) over inline `style={{}}` for theme integration and pseudo-class support
- **Avoid `!important`** — usually a sign of specificity gone wrong; fix the cascade instead

## Event Handlers

- **Passive listeners** for `scroll`, `wheel`, `touchstart`, `touchmove` — `addEventListener('scroll', fn, { passive: true })`. Prevents jank from default-prevention checks
- **Debounce / throttle** for typing-driven and scroll-driven handlers; 150–300ms for typing, frame-throttle for scroll-derived layout
- **Remove listeners on unmount** — long-lived listeners on `window` / `document` registered in components are memory leaks if not torn down

## Client-Side Storage

- **`localStorage` / `sessionStorage` are synchronous and SSR-unsafe** — `typeof window === "undefined"` guards or storage-access via effects, not render
- **Size quotas vary** — ~5–10MB typical; large blobs belong in IndexedDB or Cache Storage
- **Sensitive data caveats** — see Browser Security above
- **Schema versioning** — stored values outlive code; reading old shapes after a refactor is a forward-compat concern

## Routing

- **Anchor vs router-link** — `<a href>` causes full reload; the router's `Link` component does client-side navigation. Mixing them produces inconsistent UX
- **Redirects in render are render loops** — `navigate("/login")` during render re-enters render with the same condition. Put redirects in effects or route-level loaders
- **Auth route guards** — verify the guard runs *before* the protected page mounts; an effect-based redirect lets the protected page render briefly with stale data
- **Prefetching** — link-hover or in-viewport prefetch for next-likely routes; flag missing prefetch on common navigation paths

## Hydration & SSR (when applicable)

- **Mismatch sources** — `Date.now()` / `Math.random()` / `window` access / `localStorage` reads during render produce different output server-side and client-side
- **Conditional rendering on `typeof window`** — only at the top level (returning `null` during SSR for client-only widgets), not interleaved with server-rendered content
- **`useEffect` runs only on the client** — use for client-only setup; never expect server-side execution

## UI Polish & Motion

When the diff touches visual detail, animation, or micro-interaction, **load `ui-polish.md`** — it holds the exact values (easing curves, durations, `scale(0.96)`, concentric-radius math, pure-black/white image outlines, spring config). Review against those; the checklist below is the fast scan.

- [ ] `transition: all` (or bare Tailwind `transition`) — flag; name exact properties
- [ ] `scale(0)` entrance — should be `scale(0.95)` + opacity
- [ ] `ease-in` on UI motion, or a raw CSS built-in where a custom curve is warranted
- [ ] Popover `transform-origin: center` instead of trigger-anchored (modals are exempt)
- [ ] Animation on a keyboard-initiated action (should be instant)
- [ ] Duration > 300ms for a standard UI animation
- [ ] Hover animation without `@media (hover: hover)` gating
- [ ] Keyframes on a rapidly re-triggered element (should be interruptible transitions)
- [ ] Same enter/exit speed (exit should be shorter/softer)
- [ ] Elements entering together with no stagger (~100ms)
- [ ] Nested rounded elements without concentric radii
- [ ] Dynamic numbers without `tabular-nums`
- [ ] Tinted image outline (must be pure black/white at low opacity)
- [ ] `will-change: all`, or on non-compositable properties
- [ ] Interactive control below a 40×40px hit area

**Present polish findings as a before/after table**, grouped by principle with a heading above each table, one diff per row. Cite file + property when not obvious from the snippet. Omit a principle's table entirely if nothing needed changing — no empty tables.

```
#### Concentric border radius
| Before | After |
| --- | --- |
| `rounded-xl` card + `rounded-xl` inner button (`p-2`) | `rounded-2xl` card (12+8), `rounded-lg` inner |
```

Polish findings are typically LOW/DESIGN — pose them collaboratively, don't inflate over correctness/security findings.

## Cross-References

- React-specific concerns (hooks, components, memoization, render perf, JSX patterns): `react-review.md`
- Cross-cutting security (CSRF, CORS, authn/authz, secrets, server-side input validation, multi-tenancy): `security-review.md`