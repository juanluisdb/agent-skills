# Accessibility

Access belongs in the design, not in a retrofit pass. Almost everything here is decided by choosing an element and a focus order, which costs nothing at design time and is expensive to unpick once the markup exists.

Contrast ratios are in `look.md` § Colour. Reduced motion is in `motion.md` § Accessibility.

## Semantics carry most of it

- **Pick the element for the job.** A button for an action, a link for navigation, the landmark elements (`nav`, `main`, `header`, `footer`) for regions, headings in order without skipping a level. Decide the semantic structure *before* styling it.
- **A div with a role is a worse button than a button.** Div soup patched with `role` attributes has to reimplement focusability, Enter and Space handling, and the disabled state, and it usually reimplements two of the three.
- **ARIA fills gaps, it does not replace semantics.** `aria-label`, `aria-describedby`, and `aria-live` are for intent that HTML cannot express. Wrong ARIA is worse than none, because assistive tech believes it.
- **Every form control has a real label.** A `<label for>`, `aria-label`, or `aria-labelledby`. A placeholder is not a label: it disappears exactly when the person needs it.

## Focus and keyboard

- **Decide the tab order,** and decide where focus lands after each transition: a modal closes, a route changes, a row is deleted, a submit succeeds. Focus left on a removed element sends a keyboard user back to the top of the document.
- **Every interactive element is reachable and operable from the keyboard.** Tab and Shift-Tab to reach, Enter or Space for the primary action, arrow keys inside a menu, listbox, or grid.
- **Visible focus, always.** Removing the outline without providing a replacement style is the single most common accessibility regression, and it is invisible to anyone testing with a mouse.
- **Custom widgets follow the ARIA Authoring Practices pattern** for their role. Combobox, menu, dialog, tabs, and tree each have a specified keyboard contract, and a widget that invents its own is a widget nobody can use.
- **Tap targets are at least 24 by 24 CSS pixels** (WCAG 2.5.8), and 44 by 44 for a primary action on touch.

## What assistive tech says

Plan the narrative, not just the labels. Move through the surface as a screen reader would and ask what gets announced: the region you entered, the name and state of the control you are on, the fact that a result set changed.

- **Async changes need a live region** or an equivalent announcement, or they are silent. A search that updates results, a save that succeeds, a validation that fails.
- **State is announced, not implied.** Expanded, selected, checked, busy, invalid: each has an attribute, and a visual-only treatment of it exists for sighted users alone.
- **An icon-only control has an accessible name.** The tooltip is not it.

## Variants are part of the design

- **The reduced-motion version is a design decision.** What is the still version of this animation? Someone will see it.
- **Both colour modes, or one deliberately.** If dark mode is in scope, the tokens cover it from the start rather than being derived later by inversion.
