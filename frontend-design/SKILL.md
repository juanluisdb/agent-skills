---
name: frontend-design
description: Design distinctive, polished frontend interfaces when the task is visually driven or asks to beautify/build UI for pages, apps, dashboards, or components. Default to a balanced blend of strong art direction and product clarity, then adapt to the user's goal and any existing design system.
---

# Frontend Design

Use this skill when the quality of the result depends on visual direction, hierarchy, typography, spacing, composition, motion, and overall taste.

Do not use this skill for routine bug fixes, small CSS nits, or non-visual frontend work unless the user is explicitly asking for a design upgrade.

## Goal

Ship frontend work that feels intentional, distinctive, and production-ready without drifting into generic AI-looking UI.

## Start By Choosing The Mode

Pick the mode that best matches the user's goal:

- `balanced hybrid` is the default; combine a clear visual idea with practical usability
- `bold art direction` for launches, landing pages, editorial surfaces, brand moments, and visually led work
- `practical product UI` for dashboards, settings, admin tools, internal apps, and operational workflows
- `preserve existing system` when working inside an established product, brand, or component system

If the user signals a goal clearly, follow that goal instead of the default.

## Working Model

Before coding, decide:

- visual thesis: the mood, material, personality, and aesthetic direction
- content structure: what each section or region needs to do
- interaction thesis: a small set of motion or interaction ideas worth emphasizing

Do not start by scattering components onto the page. Start with hierarchy, rhythm, and the dominant idea.

## Core Principles

- Give each section or surface one primary job
- Make hierarchy obvious in the first screen
- Let typography, spacing, and layout do most of the work
- Use cards only when they help the interaction or information model
- Use motion to reinforce structure, not to decorate
- Design mobile intentionally rather than collapsing the desktop layout
- Favor a small number of strong decisions over many weak ones

## Mode Guidance

### Balanced Hybrid

- Start from a clear composition and a memorable visual idea
- Keep the interface readable, scannable, and usable
- Use expressive details with restraint
- Let brand and usability support each other

### Bold Art Direction

- Pick a strong aesthetic direction and commit to it
- Use typography, contrast, layering, imagery, and atmosphere intentionally
- Prefer bold composition over safe component grids
- Accept more personality and tension if it produces a stronger result

### Practical Product UI

- Prioritize orientation, density, information hierarchy, and calm surfaces
- Keep copy short and utilitarian
- Use emphasis sparingly so important states stay legible
- Avoid marketing-page tropes unless the user asks for them

### Preserve Existing System

- Match the established spacing, component language, color behavior, and tone
- Improve polish without inventing a conflicting visual language
- Push harder only when the user explicitly wants a redesign

## Typography

- Do not default to `Arial`, `Inter`, `Roboto`, or generic system stacks when the work is visually led
- Choose type intentionally based on the mode and product context
- Prefer a purposeful pairing: one voice for display or emphasis, one for text if needed
- In product-heavy surfaces, readability wins, but the typography should still feel chosen rather than incidental
- Use scale, weight, and spacing to create hierarchy before reaching for extra color or decoration

## Color And Surfaces

- Start with a restrained palette and one clear accent direction
- Do not default to purple gradients on white
- Use contrast, temperature, and surface treatment deliberately
- Backgrounds should support the concept through gradients, texture, depth, or structure when appropriate
- In product UI, keep surfaces calm and let state colors carry meaning

## Layout And Components

- Build the page from composition first, then introduce components
- Avoid card-heavy layouts unless cards are functionally justified
- Avoid hero sections that are just a headline inside a floating card
- Use asymmetry, framing, negative space, or modular rhythm when it strengthens the concept
- Repetition is useful, but every repeated block should have a reason

## Motion And Interaction

- Add only a few meaningful motion ideas
- Favor staged reveals, transitions that clarify state, and motion that supports hierarchy
- Avoid ornamental animation, constant looping, or motion that competes with content
- On product surfaces, motion should make the UI feel responsive and calm

## Implementation Standard

- Produce code that is responsive, accessible, and ready to run
- Check contrast before relying on subtle color differences
- Make desktop and mobile both feel designed
- Keep visual decisions coherent across states, spacing, and breakpoints
- When working in an existing codebase, preserve local patterns unless the user asked for a broader redesign

## Hard Rules

- no generic SaaS card soup by default
- no unexamined font defaults
- no ornamental motion
- no random accent-color explosions
- no decorative ideas that weaken readability or hierarchy
- no breaking an established design system unless the user asked for it
- no desktop-only thinking

## Self Review

Before finishing, check:

- Is there one clear visual idea?
- Is the hierarchy obvious immediately?
- Does each section or region have one job?
- Are typography, spacing, and layout carrying the design?
- Are cards, colors, and motion actually necessary?
- Does the result match the user's goal: bold, practical, balanced, or system-preserving?
- Does the mobile version still feel intentional?
