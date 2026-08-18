---
name: visual-design
description: "Judgement on how a user-visible surface should look, read, and be usable: hierarchy, spacing, type, colour, microcopy, motion and easing values, state stories, accessibility (semantics, focus order, keyboard, screen readers). Use when a UI should feel considered, when taste is part of the ask, or when motion, visual detail, or accessibility is in question."
---

# Visual Design

Shipping something that works no longer distinguishes a product, because everyone can now do that. What people judge is how it looks, reads, and feels. That makes visual quality part of the spec rather than polish that follows delivery.

This skill holds the judgement, not the stance. Whether you are designing a surface, building one, or saying why someone else's does not land yet is decided by the context that loaded it.

## Decide the bar, then say why

- **State the quality bar as scope.** Decide what level of finish this surface gets, and name the polish being deliberately dropped so it reads as a choice rather than an omission. Craft deferred without being named never lands.
- **Name the reference.** Which shipped product does this pattern well, and what specifically are you taking from it: its density, how it handles the empty state, the way it moves? A surface designed without a reference converges on the generic answer. Ask for one if the user has a product in mind; propose two or three if they do not.
- **Say the *why* behind every visual and motion decision.** Taste is articulable. `scale(0)` feels wrong because nothing in the real world appears from nothing, and even a deflated balloon has a visible shape. "It feels better" is an unfinished thought: the reason is the part that transfers to the next decision, and it is what makes this one reviewable. If you cannot state it, the choice is not settled.
- **The obvious answer is suspicious.** A big number with a small label, three feature cards, a gradient accent: that is what you would produce for *any* brief. Work out what the generic version of this request would look like, and wherever the design matches it, change that part. Where the brief pins a direction, the brief wins, including when it asks for something conventional.
- **Match the mood.** Crisp and fast for a dense professional tool; softer or playful only where the brand earns it. Motion personality and visual personality belong to the same system as the product's voice.
- **Good defaults beat options.** Most consumers of a component never configure it, so the shipped easing, spacing, and copy have to already be right. A configuration option is not a substitute for a decision.
- **Spend boldness in one place.** One memorable element, everything around it quiet and disciplined. Two signature elements compete and both lose.

## Design the states, not the screen

A screen is a family of states, and the awkward ones are where UI actually breaks. They are cheap to decide up front and expensive to retrofit: zero items, exactly one, far too many, the longest plausible string, missing or partial data, no permission, loading, error. Handling them invisibly is most of what makes software feel considered, and the user never notices, which is the point.

## Look at it again

Timing and spacing flaws you are blind to on build day are obvious the next morning, and slowing motion to two to five times its duration exposes the rest. That pass is planned work, not optional rework. Before shipping, remove one thing: the decoration that survives only because you made it.

## References

| Reference | Load when |
|---|---|
| `references/look.md` | How the surface looks and reads: hierarchy, spacing scale and density, type system, colour and contrast, content-extreme states, microcopy, greenfield direction, restraint. |
| `references/motion.md` | How it moves and the micro-detail values: whether to animate at all, easing and duration numbers, springs, enter and exit, transforms, clip-path, gestures, surfaces (radius, shadows, outlines), typographic properties, motion performance, reduced-motion. |
| `references/accessibility.md` | Whether the surface can be used at all: semantic elements, focus order and where focus lands after a transition, the keyboard contract, labels, what assistive tech announces, tap-target size. Load it whenever a surface is built or judged, not only when someone asks about a11y. |
