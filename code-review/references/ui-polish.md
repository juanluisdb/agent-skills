# UI Polish & Motion

Concrete rules for interfaces that feel considered. Great UI is a compounding stack of small, mostly-invisible details — this is the reference for the exact values and patterns that make the difference. Load it when building or reviewing any browser-facing UI with motion, interaction, or visual detail.

Taste is trained, not innate: these are the defaults exceptional work converges on. Ship good defaults over configuration — most users never customise, so the out-of-the-box easing, timing, and spacing must already be right.

---

## Motion: decide before you animate

Motion is a cost, not a free garnish. Walk these four questions in order before adding any animation.

### 1. Should this animate at all?

Frequency decides. The more often an action happens, the less it should animate.

| How often the user triggers it | Animation |
|---|---|
| 100+ times/day (list rows, menu items) | None — it becomes friction |
| Tens of times/day | Remove or drastically reduce |
| Occasional | Standard animation |
| Rare / first-time (onboarding, empty→filled) | Room for delight |

**Never animate keyboard-initiated actions** (⌘K palette open, Enter-to-submit). A power user firing the keyboard wants instant; animation reads as lag.

### 2. What is its purpose?

Valid purposes: spatial continuity (where did this come from / go to), state indication, feedback, explaining a change, preventing a jarring jump. *"Looks cool"* is not a purpose for anything triggered more than rarely.

### 3. What easing?

| Motion | Easing |
|---|---|
| Entering / exiting | `ease-out` |
| Moving / morphing on screen | `ease-in-out` |
| Hover, color change | `ease` |
| Constant motion (spinner, marquee) | `linear` |

**Never `ease-in` for UI** — the delayed start feels sluggish. Prefer custom curves over the CSS built-ins:

```css
--ease-out:    cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

### 4. How fast?

| Element | Duration |
|---|---|
| Button press feedback | 100–160ms |
| Tooltip / small popover | 125–200ms |
| Dropdown / select | 150–250ms |
| Modal / drawer | 200–500ms |

**Keep UI animations under 300ms.** Faster animations make the whole app feel snappier regardless of actual load time (perceived performance).

**Asymmetric enter/exit.** Exits are shorter and softer than enters — the user's focus is already moving on. Where the *user* decides (hold-to-delete), go slow; where the *system* responds (release), snap back fast.

---

## Springs (when to use)

Reach for springs over duration-based easing for: drag with momentum, elements that should feel "alive", interruptible gestures, decorative mouse-tracking. Springs keep velocity when interrupted; CSS keyframe animations restart.

Two config styles:

```ts
// Apple-style (simpler) — prefer this
{ type: "spring", duration: 0.5, bounce: 0.2 }
// Physics — when you need precise control
{ type: "spring", mass: 1, stiffness: 300, damping: 30 }
```

Keep `bounce` subtle (0.1–0.3), and **0 for most UI** — bounce reads as playful, wrong for crisp/professional surfaces. Match motion personality to the component's vibe.

---

## Transitions vs keyframes

| | CSS transitions | Keyframe animations |
|---|---|---|
| Interruptible | Yes — retargets to latest state mid-flight | No — restarts from frame 0 |
| Use for | Interactive state (hover, toggle, open/close, rapidly-triggered) | One-shot staged sequences (page enter, loading) |

**Rule:** transitions for anything a user can re-trigger before it finishes; keyframes only for run-once sequences. A toast list or a drawer must use transitions or it snaps when re-triggered.

```css
/* Interruptible — clicking again mid-animation smoothly reverses */
.drawer { transform: translateX(-100%); transition: transform 200ms var(--ease-out); }
.drawer.open { transform: translateX(0); }
```

For programmatic control with CSS-grade performance, use the Web Animations API (WAAPI) — hardware-accelerated, interruptible, no library.

---

## Enter / exit

**Enter — split and stagger.** Don't animate one big container. Break content into semantic chunks (title, description, actions) and stagger each ~100ms; split hero titles into words at ~80ms. Combine `opacity` + `translateY(12px→0)` + `blur(4px→0)`.

**Exit — subtle.** Small fixed `translateY(-12px)` (not full height), shorter than the enter. Keep a little directional movement so context is preserved; never just `display: none`.

**Skip enter on page load.** Elements already in their default state shouldn't animate in on first render — only on later state changes. With Framer Motion use `initial={false}` on `AnimatePresence`. Verify a full refresh still looks right (don't break an intentional staggered hero).

**Stagger** is decorative — never block interaction while it plays.

---

## Component patterns

**Scale on press.** `scale(0.96)` on `:active` with a 150ms `ease-out` transition gives tactile feedback on any pressable element. Always `0.96`; never below `0.95` (feels exaggerated). Offer a `static` prop to disable where motion distracts.

```tsx
<button className="transition-transform duration-150 ease-out active:scale-[0.96]">
```

**Never animate from `scale(0)`.** Full disappearance is unreal — start at `scale(0.95)` + opacity.

**Origin-aware popovers.** A popover should scale out *from its trigger*, not from center: `transform-origin: var(--radix-popover-content-transform-origin)` (or Base UI's `--transform-origin`). Exception: modals stay `transform-origin: center` — they're viewport-centered.

**Tooltips — skip delay on subsequent hovers.** First tooltip has an open delay; once one has shown, sibling tooltips open instantly with no animation (track with a `data-instant` attribute). Matching real cursor intent.

**Contextual icon swaps** (play→pause, like→liked). Animate with `opacity`, `scale`, `blur` — exact values, do not deviate:
- `scale`: `0.25 → 1`
- `opacity`: `0 → 1`
- `filter`: `blur(4px) → blur(0px)`
- With Motion: `transition: { type: "spring", duration: 0.3, bounce: 0 }` — **bounce always 0**
- No Motion dep: keep both icons in the DOM (one `absolute`), cross-fade with `transition` using `cubic-bezier(0.2, 0, 0, 1)` — gives enter *and* exit with no library

Check `package.json` for `motion`/`framer-motion` before choosing; don't add a dependency just for icon swaps.

**Enter states with `@starting-style`** — modern CSS entrance without a JS `mounted` flag:

```css
.popover { opacity: 1; transition: opacity 200ms var(--ease-out); }
@starting-style { .popover { opacity: 0; } }
```

**Blur to mask imperfect crossfades.** A brief `filter: blur(2px)` during a two-state crossfade blends them and hides overlap. Keep blur < 20px for performance.

---

## clip-path techniques

`clip-path: inset(top right bottom left)` clips to a rectangle; animate the insets. GPU-compositable.

- **Reveal:** hidden `inset(0 100% 0 0)` → visible `inset(0 0 0 0)`.
- **Tabs with seamless color transition:** duplicate the tab list styled as the active state, clip the copy to only the active tab, animate the clip on change. Achieves color transitions individual-property timing can't.
- **Hold-to-delete:** overlay at `inset(0 100% 0 0)`; on `:active` transition to `inset(0 0 0 0)` over ~2s linear; on release snap back 200ms ease-out. Add `scale(0.97)` for press feel. (Asymmetric: slow while held, fast on release.)
- **Scroll reveal:** start `inset(0 0 100% 0)`, animate to `inset(0 0 0 0)` on viewport entry (`IntersectionObserver` / `useInView`).
- **Comparison slider:** overlay two images, clip the top one `inset(0 50% 0 0)`, drive the right inset from drag position. No extra DOM.

---

## Gesture & drag

- **Momentum dismissal** — dismiss when velocity (`abs(distance)/elapsedTime`) exceeds ~0.11, regardless of distance. A quick flick should suffice.
- **Boundary friction, not hard stops** — dragging past a limit keeps moving with increasing resistance (damping), which feels natural; invisible walls don't.
- **Pointer capture** — capture pointer events once a drag starts so it continues when the pointer leaves the element bounds.
- **Multi-touch guard** — ignore additional touch points after the first; switching fingers otherwise jumps position.

---

## Surfaces

**Concentric border radius.** `outerRadius = innerRadius + padding`. Mismatched nested radii are the most common thing that makes UI feel off. If the gap is > 24px, treat layers as separate surfaces and pick radii independently.

```tsx
<div className="rounded-2xl p-2">   {/* 16px radius, 8px pad */}
  <div className="rounded-lg">      {/* 8px = 16 − 8 ✓ */}
```

**Optical over geometric alignment.** When geometric centering looks off, adjust by eye:
- Text+icon button: icon-side padding = text-side − 2px.
- Play triangle: nudge `margin-left: 2px` (its visual center isn't its geometric one).
- Asymmetric icons (stars, carets): fix the SVG viewBox/path directly where possible.

**Shadows over borders** — for depth/elevation on buttons, cards, containers, dropdowns, modals. Shadows use transparency so they adapt to any background; solid borders don't. **Not** for dividers, table cell boundaries, input outlines, or hairline separators — those stay borders. Layer three shadows: a 1px ring, a subtle lift, an ambient depth.

```css
--shadow-border: 0 0 0 1px rgb(0 0 0 / .06), 0 1px 2px -1px rgb(0 0 0 / .06), 0 2px 4px 0 rgb(0 0 0 / .04);
/* Dark mode: single white ring — layered depth is invisible on dark */
--shadow-border-dark: 0 0 0 1px rgb(255 255 255 / .08);
```

**Image outlines** — subtle 1px inset outline gives images consistent depth. Colour is **non-negotiable**: pure black `rgb(0 0 0 / .1)` in light, pure white `rgb(255 255 255 / .1)` in dark. Never a tinted near-black/near-white (slate/zinc/neutral) — it picks up the surface colour and reads as dirt on the edge. Use `outline` + `outline-offset: -1px` (doesn't affect layout).

```tsx
<img className="outline outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10" />
```

**Minimum hit area** — interactive elements ≥ 40×40px (WCAG target ≥ 44×44 for primary). Extend a small visible control with a pseudo-element; never let two hit areas overlap.

---

## Typography

- **`text-wrap: balance`** on headings — evens line lengths, kills orphans. Only works ≤ 6 lines (Chromium) — silently ignored on long text.
- **`text-wrap: pretty`** — default for short-to-medium text (paragraphs, captions, list items); prevents a lone orphan word. No line limit. Skip both on 10+ line text.
- **`-webkit-font-smoothing: antialiased`** on the root (`html`) — macOS renders text heavier than intended; this crisps it. Apply once at root, not per-element. No-op on other platforms, safe universally.
- **`font-variant-numeric: tabular-nums`** on any dynamic number (counters, prices, timers, table columns) — equal-width digits prevent layout shift as values change.

---

## Performance

- **Animate only `transform` and `opacity`** (and `filter`, `clip-path`) — they skip layout/paint and run on the GPU. Animating `width`/`height`/`top`/`left`/`margin`/`padding` triggers all three rendering phases.
- **Never `transition: all`** (nor Tailwind's bare `transition`) — it watches every property, causes unintended transitions, and blocks browser optimisation. Name exact properties: `transition-property: scale, opacity`. (Tailwind `transition-transform` = `transform, translate, scale, rotate`.)
- **`will-change` sparingly** — only `transform`/`opacity`/`filter`/`clip-path`, and only when you actually see first-frame stutter (Safari benefits most). Never `will-change: all`; each layer costs memory.
- **For frequent drag, set `transform` directly** on the element, not via an inherited CSS variable (a variable change recalculates all children).
- **Framer Motion caveat** — shorthands `x`/`y`/`scale` run on the main thread via rAF, not GPU. Under load (e.g. during a page transition) use the full `transform` string for hardware acceleration.
- **CSS beats JS under load** — CSS/WAAPI animations run off the main thread and hold frame rate while JS drops frames. Use CSS for predetermined animations, JS only for genuinely dynamic ones.

---

## Accessibility

- **`prefers-reduced-motion`** means *fewer/gentler*, not zero. Keep opacity and colour transitions that aid comprehension; drop movement (slides, scale, parallax).
- **Gate hover animations** behind `@media (hover: hover) and (pointer: fine)` so touch devices don't fire false hover states.

---

## Debugging motion

- **Slow-mo** — temporarily 2–5× the duration (or use the DevTools animation inspector) to check easing, transform-origin, and that coordinated properties stay in sync.
- **Frame-by-frame** — Chrome DevTools Animations panel to catch timing drift between properties invisible at full speed.
- **Real devices** — test touch/gesture on physical hardware via remote DevTools; simulators lie about gesture feel.
- **Review the next day** — fresh eyes catch timing imperfections you're blind to after building them. The `opacity`+`height` list enter/exit combo in particular has no formula — tune it until it feels right.