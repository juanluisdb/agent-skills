# Visual Design Prompts

Design-time prompts for how a surface *looks* and *reads*: hierarchy, spacing, type, colour, states, copy. Load when any user-visible surface is being designed or reshaped.

The premise: shipping something that works no longer distinguishes a product, because everyone can now do that. What people judge is how it looks, reads, and feels. That makes visual quality part of the spec, not polish that follows delivery.

Stack-neutral — values are plain CSS, and where a stack changes the mechanics it's called out inline. Motion and micro-detail values live in `ui-polish.md`; platform concerns (a11y, perf, i18n, routing) in `frontend-design.md`.

---

## Hierarchy

Decide what the surface is *for* before deciding how it looks. One view, one job.

- **One primary action per view.** Everything else is secondary or tertiary and looks it. Two competing primaries means the view has two jobs — split it, or pick.
- **Rank the content before styling it.** List every element in importance order, then spend the strongest treatment on rank one. If there's no clear rank one, the framing isn't settled — back to the Frame lens.
- **Hierarchy tools in order: position, size, weight, colour, space.** Reach for position and size first, colour last. Colour-only hierarchy disappears in dark mode, in greyscale, and for colour-blind users.
- **Squint test.** Blur the design mentally (or literally, in the browser). What do you see first? If it isn't rank one, the hierarchy is wrong however good each element looks on its own.
- **The obvious answer is suspicious.** A big number with a small label, three feature cards, a gradient accent: that's what you'd produce for *any* brief. Use it only when it's genuinely the best fit for this one.

## Spacing & density

- **One spacing scale, no magic numbers.** A fixed scale (4, 8, 12, 16, 24, 32, 48, 64) with every gap taken from it. One scale is what makes retuning the whole surface possible later; arbitrary values are what makes it impossible.
- **Proximity encodes relationship.** Related things sit closer than unrelated things, and the gap *between* groups exceeds the gap *inside* a group. Most UI that reads as cluttered has uniform spacing, not too much content.
- **Density matches the task.** A tool used all day for scanning and comparing wants dense rows and tight leading; an onboarding step or a marketing surface wants air. Importing a marketing product's density into a data table is a common mismatch.
- **Whitespace is a signal.** Space around an element is part of what makes it read as important, so cutting it to fit more in costs hierarchy.
- **Alignment is a decision, not an accident.** Pick the edges things align to and hold them. Optical adjustments to those edges live in `ui-polish.md` § Surfaces.

## Type

- **Cap the measure at ~65ch.** Body text stretched to the full container is uncomfortable; long lines lose the return sweep.
- **Few sizes, deliberate steps.** Four to six sizes cover almost any product surface. A new size per context is how a UI stops looking like one system.
- **Weight and colour carry UI emphasis, not italic.** Italic hierarchy reads like print editorial. Keep italic for citations and linguistic stress in prose.
- **Underline is reserved for links.** Underlining non-link text trains people to click inert copy, which degrades the affordance everywhere else in the product.
- **In a greenfield direction, pair faces deliberately** — a characteristic display face used with restraint, a body face chosen to complement it, and a utility face for captions or dense data if the surface needs one. The type treatment is part of the personality, not a neutral delivery vehicle.

Property-level rules (`text-wrap`, `tabular-nums`, uppercase tracking, the `…` character, font-smoothing, fallback metrics) live in `ui-polish.md` § Typography.

## Colour

- **Neutral-dominant, one accent.** Most of a product surface is a neutral ramp; the accent marks the primary action and the active state. A second accent needs a reason and a third almost never has one.
- **Semantic colours stay semantic.** If red means destructive and amber means warning, neither can also be decoration, or the signal stops working.
- **Never colour alone.** Any state carried by colour also carries an icon, a label, or a weight change — for colour-blind users, greyscale output, and dim screens.
- **Contrast to numbers.** 4.5:1 for body text, 3:1 for large text (≥24px, or ≥19px bold) and for the boundary of interactive elements. Test the accent against both the light and the dark surface before adopting it; a mid-tone brand colour usually fails one of them.
- **Dark mode is not an inversion.** Elevation moves from shadow to lighter surface, saturated colours need desaturating, and pure white on pure black causes halation. Design the ramp for both modes, or scope dark mode out explicitly.

## States, not screens

A screen is a family of states. Design the awkward ones at planning time — they're where UI actually breaks, and they're cheap to plan and expensive to retrofit.

- **Content extremes** — zero items, exactly one, the expected number, far too many. Decide what paginates, what virtualizes, what truncates.
- **Longest plausible string** — the 60-character company name, the German label, the person with one name. Any fixed-width text container needs an overflow plan: truncate with the full value available on hover, wrap, or scroll.
- **Missing and partial data** — a null field, a failed sub-request that leaves the rest usable, a stale value. Decide what renders instead: a dash, a placeholder, or nothing at all.
- **Permission and role variants** — what does a read-only user see where the primary action sits? Hiding and disabling send different messages; pick deliberately and say which.
- **Async trio** — loading, empty, and error are covered in `react-design.md` § Loading / empty / error stories. Any fetching surface needs them.

## Copy

Words are design material. Templated copy makes a considered layout feel templated.

- **Name things by what the person controls,** never by how the system is built. Someone manages notifications, not webhook config.
- **Controls say what happens.** "Save changes", not "Submit". Keep the verb stable through the whole flow: a button that says Publish produces a toast that says Published.
- **Errors say what happened and how to fix it,** in the interface's voice. No apology, no vagueness, no blame.
- **An empty screen is an invitation to act** — it names why it's empty and offers the next step.
- **One job per element.** A label labels, helper text explains, an example demonstrates. Nothing quietly does double duty.
- **Sentence case, plain verbs, no filler.** Specific beats clever.

## Greenfield direction (no design system to inherit)

Decide the direction before any code and write it down in four parts:

- **Colour** — 4 to 6 named values with hex, including both ends of the neutral ramp and the accent.
- **Type** — the faces and their roles (display, body, utility).
- **Layout** — the concept in one or two sentences plus a rough ASCII wireframe, which is enough to compare two options without building either.
- **Signature** — the single element the surface will be remembered by.

Then review that plan *before* building: work out what you'd produce for a generic version of the same request, and wherever the plan matches it, change that part and say what you changed. Where the brief pins a direction, the brief wins — including when it asks for something conventional.

**Calibration.** Machine-generated UI clusters on a few looks: warm cream background with a high-contrast serif and a terracotta accent; near-black with a single acid-green or vermilion accent; hairline-ruled broadsheet columns at zero border radius. Each is legitimate for some brief and a default for most. Recognising them is what stops one shipping by accident.

## Restraint

- **Spend boldness in one place.** One memorable element, everything around it quiet and disciplined. Two signature elements compete and both lose.
- **Match complexity to the direction.** A maximalist direction needs elaborate execution; a minimal one needs precision in spacing, type, and alignment. Elegance is executing the chosen direction well, not choosing the smaller one.
- **Remove one thing before shipping.** Cut the decoration that survives only because you made it.

## What good looks like

- One job per view, one primary action, a content rank you can state out loud
- Every gap from one spacing scale; grouping carried by proximity, density matched to the task
- Four to six type sizes, measure capped, emphasis by weight and colour
- Neutral-dominant palette with one accent, contrast verified in both colour modes
- Content extremes, longest string, missing data, and permission variants designed rather than discovered
- Copy written from the user's side of the screen, verbs stable across the flow
- A stated reason behind each visual choice, not "it looks better"