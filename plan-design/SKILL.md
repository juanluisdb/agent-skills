---
name: plan-design
description: Turn an idea into a real plan — frame, explore, decide, craft, sequence, validate. Grills you on the open decisions, product-first, and lands on work a builder can pick up. Use for a feature idea, refactor, UI where taste and polish matter, or to be grilled before building.
---

# Plan & Design

Planning is **triage, not a march**. The shape of the work — raw idea vs detailed spec vs half-implemented — decides which lenses to apply and in what order. This skill diagnoses where you are and how you want to work, then applies lenses (Frame / Explore / Decide / Craft / Sequence / Validate) and loads stack-specific design prompts only where relevant.

**Lenses are tools, not steps.** Skip what doesn't apply. A one-line fix doesn't need five lenses; a greenfield feature might cycle through Frame and Explore three times before reaching Sequence.

**Planning converges.** When you have enough to recommend, recommend — don't re-derive settled decisions, gather context past the point where it changes the plan, or survey options you won't pursue.

The output is *thinking* — what shape it takes (a conversational reply, a sketch, sometimes a structured plan) depends on what the user asks for. Persistence is opt-in, not default.

**Planning stops at the plan.** The deliverable is an agreed design and the ordered work to build it; writing that code is a separate job with its own concerns. Ending here is what keeps the decisions visible instead of dissolving into a diff.

---

## Stance

Work *with* the user: apply lenses, propose, ask back, iterate. The plan lives in the conversation unless a file is explicitly requested.

Cadence is your call from the user's signal — a heavy spec earns a full draft, fragmented input earns smaller slices proposed one at a time. No announcement boilerplate; make the stance evident from how you engage.

---

## Grill

Planning isn't just proposing and iterating — it's **grilling**. The lenses surface a decision tree; grilling walks it *with* the user, branch by branch, resolving dependencies one at a time until you reach shared understanding. Calibrate intensity to blast radius: a one-line fix earns no grilling; an expensive-to-undo design earns a relentless pass.

**Order: product branches first, then technical.** Agree on *what* we're building from the user's point of view before *how* it's built. Triage every open decision the lenses surface into one bucket:

| Bucket | Test | Action |
|---|---|---|
| **Product-observable** | The user sees, feels, or behaves differently by the answer | Grill first, in product terms |
| **Consequential technical** | Shape, trade-off, or anything expensive-to-undo — no product-visible difference, but the engineer should weigh in | Grill second. You're planning *with* a product engineer, not a black box — surface these, don't hide them |
| **Trivial engineering** | No observable difference, cheap, reversible | Decide it yourself, don't raise it |

The failure to avoid: burying a product-observable decision as "trivial" because it was easier not to ask — *and* its mirror, black-boxing a consequential technical call the engineer would want to make.

For every branch you grill:

- **One thread at a time, highest-leverage first** — the decision that unlocks or dissolves the most others. A later question often dissolves once an earlier one is answered.
- **Always offer a recommended answer** so the user can say "yes, that" instead of inventing one. Recommend from the code and the lenses, not a coin flip.
- **Explore the codebase instead of asking** whenever the answer is discoverable there — never ask what a grep or an `Explore` subagent can settle. Ground each branch in how the code actually works; a wrong guess buried in the plan is worse than an open question. When something genuinely can't be inferred, say so plainly and name exactly what you need.
- **Surface trade-offs as scope levers** — when a choice meaningfully changes cost, hand over the lever in the user's currency (time, risk, scope): *"drop the animation and this ships today; keep it and it's another day."* Let the user trade scope for speed deliberately.

Grill until every consequential branch is resolved or explicitly deferred — not until the first plausible answer.

---

## Entry-state triage

Diagnose where the user is starting from. This decides which lenses to apply and in what order. **Do this before anything else.**

| Starting point | Heavy on | Light on |
|---|---|---|
| **Raw idea** — vague feature wish, problem statement, "wouldn't it be cool if…" | Frame, Explore | Sequence (premature) |
| **Detailed spec** — requirements done, approach undecided | Explore, Decide | Frame (already done) |
| **Decided approach** — knows what to build, needs the plan | Sequence, Validate | Explore (already done) |
| **Half-implemented** — partial code, needs the rest planned | Frame (re-scope), Sequence (continue), Validate | Explore (committed) |
| **Stuck mid-implementation** — something's wrong but unclear what | Diagnose first: is it a design problem, a sequence problem, or just hard work? Then apply the right lens | — |

Also identify, before applying lenses:

- **Which stacks does this touch?** TypeScript / React / frontend (browser) / security / something else. Drives reference loading (next section).
- **What product surface is affected?** User-facing? Internal tool? Infrastructure? Shapes the Frame lens heavily.
- **What's the blast radius?** Reversible (rename, internal helper) or expensive-to-undo (DB schema, public API, auth model)? Calibrate effort to blast radius.

**Subagent opportunity:** in a large or unfamiliar repo, delegate codebase exploration to a subagent before triage — surface agent-rule files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, etc.), READMEs, and contributing docs; map relevant modules and conventions; note recent changes. Keeps main context lean.

Name the entry state and the references you loaded in passing as you start — a natural sentence, not a ceremonial block.

---

## Reference loading

Read every reference whose load condition matches the triage result, before applying any lens — they hold the shape-level prompts the lenses use, and a skipped reference drops whole dimensions from the plan (state boundary, threat model, a11y). The conditions are inclusive: a plausible match is a match.

| Reference | Load when (inclusive triggers) | Contains |
|---|---|---|
| `references/module-design.md` | Any module's interface is being designed or reshaped — a new module, an extraction, a refactor that moves responsibilities, or a decision about where a seam goes. Language-agnostic; loads alongside the stack references | Depth vocabulary, the deletion test, seam placement, dependency categories that decide the test strategy, replace-don't-layer |
| `references/typescript-design.md` | Any TS file is touched, or types are being designed | Domain shape, boundary model, error model, escape-hatch isolation, module shape, inference policy |
| `references/react-design.md` | Any React component / hook / page is touched, or any UI state is in scope | State boundary, data fetching, render boundaries, loading/empty/error stories, composition, effect discipline |
| `references/frontend-design.md` | Any browser-facing UI is touched (visible to end users), or perf / a11y / i18n / routing is in scope | A11y as design input, perf budget, i18n, image strategy, styling system, routing, browser security |
| `references/visual-design.md` | Any user-visible surface is being designed or reshaped, or the UI should *look* considered — a new screen, a redesign, "make this nicer", anything where taste is part of the ask | Hierarchy, spacing scale and density, type system, colour discipline, content-extreme states, microcopy, greenfield direction, restraint |
| `references/ui-polish.md` | Any visual-detail, motion, animation, or micro-interaction work is in scope (UI that should *feel* considered) | Motion decision framework, easing/duration values, springs, enter/exit, clip-path, gestures, surfaces (radius, shadows, outlines), typography, perf, reduced-motion |
| `references/security-design.md` | Anything user-facing, authenticated, persisting data, calling external services, handling secrets, or touching crypto / PII | Threat model, authn/authz, data classification, validation boundary, failure-mode design, crypto choices |

**Surface what you loaded** — a single natural mention at the start (*"loaded react-design.md and security-design.md"*) or interspersed as you apply prompts (*"thinking about the state boundary per react-design..."*). This is the forcing function against lazy reading; the user can catch silent skipping without any ceremonial output blocks.

---

## Lens: Frame

*Make sure we're solving the right problem before exploring solutions.*

Apply heavy when the input is a raw idea or fuzzy feature request. Apply light when a clear spec exists.

### Problem & users (product framing, not just technical)

- What's the user problem in one sentence? Who experiences it?
- What signals success from the **user's** perspective, not the engineer's? (A faster query is engineering success; a user noticing it isn't.)
- What's the **simplest thing that delivers value**? Resist scope creep at the framing step.
- Are we solving the symptom or the cause? If the symptom, is that an explicit, justified choice?
- What's the user journey before vs after this change?

### Scope

- What's in scope and explicitly out of scope?
- What's the cost of being wrong? Reversible decisions deserve less debate than expensive ones.
- **Spike vs build** — if the question is *"is this even possible"*, spike. If *"what's the right shape"*, design and build.

### Consumer of the result

- Who consumes the resulting interface — end users, other engineers, an LLM, another system?
- What does "first-try success" look like for them?
- **If the consumer is a program or an agent, the envelope is part of the design** — and on failure paths as much as success. Decide the status/exit/format contract up front: what a machine reads to know it failed, how categories map to codes, whether a requested output format holds on every path, and how two different causes stay distinguishable enough that the consumer knows which recovery to attempt. Retrofitting this is how a rejected result ends up reported as a success.

---

## Lens: Explore

*Two-plus approaches before converging. The design-it-twice principle.*

Apply heavy when the approach is undecided. Skip when the user has explicitly committed to an approach.

- **Generate alternatives with meaningfully different trade-offs.** Not minor variants — distinct shapes: the cheap MVP, the polished long-term design, the build-vs-buy alternative.
- For each: shape sketch, what it makes easy *now*, what it makes easy/hard *later*, product implications (not just technical).
- **Write each alternative in its own notation, not as a paragraph about it.** Types and signatures, a call tree, a component tree, a file-tree diff — whichever the change is shaped like. Two alternatives described in prose aren't comparable; the same two in one notation are, and that comparison is what this lens exists to produce. It also moves the disagreement earlier: a shape the user can read is a shape they can reject while rejecting is still free.
- **Coupling & cohesion check** — what would have to change if X changes? Prefer depth: a lot of behaviour behind a small interface, so callers learn little and change concentrates in one place.
- **Test the indirection each alternative adds, don't argue it.** Two checks, both from `module-design.md`: the **deletion test** — inline the proposed module at every call site; if complexity vanishes it was a pass-through, if it reappears at N callers it earns its keep. And **one adapter means a hypothetical seam, two means a real one** — don't design a port, interface, or injection point where nothing actually varies across it. Also decide *where* the seam goes as its own question, rather than inheriting it from the current file layout.
- **Design so the two can't disagree, rather than detecting when they do.** When the shape lands in two places — a model and its wire mirror, a rule and the lint that checks it, a registry and its per-variant maps — the choice is between one definition (derive one from the other, construct with named arguments a type-checker verifies) and two definitions plus a drift test. The detector is a real option, but it costs a second thing to maintain and it only guards what it happens to compare. Take it deliberately, and if you do, decide *what artifact* it compares: the serialized payload the consumer really receives, not two self-consistent halves.
- **Decide how you'd test it while the shape is still open.** Classify the dependencies each alternative needs (`module-design.md`): in-process, local-substitutable, remote-but-owned, true external. The last two each buy a port and two adapters, so the classification is a cost that separates the alternatives, not a detail to discover later. And if an alternative's only testable form is mocking everything, that's a verdict on the design — reject it here, where changing shape is still free.
- **Naming as design** — if you can't name the concept cleanly, the domain isn't settled. Try writing the docstring or one-line description first.
- **Offer the cheaper path explicitly.** Don't just enumerate alternatives — name the trade-off as a choice the user can take: *"if we drop X we gain Y now, at the cost of Z later."* The simplest version that still delivers the value is a first-class option, not a fallback; surface it so the user decides the scope/effort trade rather than having it decided for them.
- **Build-vs-borrow ladder.** Before designing custom code, walk the rungs: does the standard library, the platform/framework, or an *already-installed* dependency already do this? Reach for a new dependency only when none do — it's a long-term cost (transitive weight, upgrades, CVEs), while custom code is a maintenance cost. Name which you're taking on and why.
- **UI components are the strongest rung on that ladder.** Dialogs, popovers, menus, comboboxes, command palettes, toasts, virtualized lists, drag-and-drop, animated numbers, code-verification inputs: a solved component almost always exists, and hand-rolling one is the default mistake. The reason isn't typing time — focus management, dismissal, keyboard semantics, and interruption handling are the actual difficulty, and they fail late, in production, on someone else's device. Read `package.json` before naming anything; if a competitor of your preferred pick is already installed, use it and flag the mismatch rather than churning the dependency. `react-design.md` § Solved-component mismatches lists the planning-time tells.

Apply the design prompts from the references loaded at triage — `module-design.md` for depth and seam placement, `typescript-design.md` / `react-design.md` / `frontend-design.md` for shape-level questions; `security-design.md` if a threat boundary is crossed by an alternative. The references are already loaded; this lens just *uses* them.

**Subagent opportunity — design it twice.** Your first idea is unlikely to be the best one, so develop the alternatives in parallel rather than iterating on the first. Vary the subagents along whichever axis is genuinely open:

- **Scope open** — one explores the MVP, one the long-term design, one a buy-or-borrow path.
- **Scope fixed, shape open** (most refactors and extractions) — give each a different interface constraint: *minimise the interface, one to three entry points, maximum behaviour behind each* · *maximise flexibility and extension* · *make the most common caller's case trivial* · *ports and adapters, when a dependency crosses a network or vendor seam*.

Brief each with the file paths, the coupling details, and the dependency category (`module-design.md`) — not with your own preferred answer. Ask each for the interface *including* its invariants, ordering constraints and error modes; a usage example written from the caller's side; what the implementation hides; the adapters it needs; and where its leverage is thin. Then compare the returns on depth, on where change concentrates, and on seam placement, and recommend one — a hybrid if elements combine well.

Write the problem-space framing (the constraints any design must satisfy, the dependencies and their categories, a rough sketch to make the constraints concrete) to the user *before* spawning, then spawn immediately. The user reads and thinks while the subagents work.

---

## Lens: Decide

*Convergence with explicit reasoning.*

- **Pick an approach.** State *why*, including alternatives rejected and *why rejected*.
- **Doc-driven check** — write the README / API surface / ticket description in one paragraph. If it doesn't write cleanly, the design isn't ready; back to Explore.
- **Stop condition** — what signals "done"? Beyond "merged": deployed, telemetry confirms healthy, customers haven't paged, follow-ups filed.
- **Known-limitations register** — what this *isn't* fixing. Captured where (issue, comment, TODO).
- **Reversibility note** — for any decision expensive to undo, capture why we're confident now (or that we accept the risk explicitly).

---

## Lens: Craft

*Working is table stakes. Decide the quality bar, and be able to say why it feels right.*

Apply whenever a user-visible surface is in scope. Skip for plumbing with no human on the other end.

- **State the quality bar as scope.** Everyone ships things that work, so "it works" doesn't distinguish the result — how it looks, reads, and feels does. Decide what level of finish this surface gets, and name the polish you're deliberately dropping so it reads as a choice rather than an omission. Craft deferred without being named never lands.
- **Name the reference.** Which shipped product does this pattern well, and what specifically are we taking from it — its density, how it handles the empty state, the way it moves? A surface planned without a reference converges on the generic answer. Ask the user for one if they have a product in mind; propose two or three if they don't.
- **Say the *why* behind every visual and motion decision.** Taste is articulable, not a gut call: `scale(0)` feels wrong because nothing in the real world appears from nothing, and even a deflated balloon has a visible shape. "It feels better" is an unfinished thought — the reason is the part that transfers to the next decision, and it's what makes this one reviewable. If you can't state it, the design isn't settled.
- **Design the states, not the happy path.** Empty, exactly one, far too many, the longest plausible string, missing data, no permission. Handling these invisibly is most of what makes software feel considered — the user never notices, which is the point. See `visual-design.md` § States, not screens.
- **Good defaults beat options.** Most consumers of a component never configure it, so the shipped easing, spacing, and copy have to already be right. A configuration option is not a substitute for a decision.
- **Match the mood.** Crisp and fast for a dense professional tool; softer or playful only where the brand earns it. Motion personality and visual personality belong to the same system as the product's voice.
- **Budget a fresh-eyes pass in the sequence.** Timing and spacing flaws you're blind to on build day are obvious the next morning, and slowing motion to 2–5× duration exposes the rest. That pass is planned work, not optional rework.

`visual-design.md` holds the look decisions (hierarchy, spacing, type, colour, copy); `ui-polish.md` holds the exact motion and micro-detail values.

---

## Lens: Sequence

*Turn the design into ordered, atomic work.*

- **Atomic increments** — each commit / PR leaves main green. No "partial state" landings.
- **Refactor-first ordering** — shape changes before behavior changes. Easier to review, easier to revert independently.
- **Test strategy upfront**:
  - Which level catches what — unit, integration, e2e?
  - Where they live and what surface they exercise.
  - **When tests get written — recommend, don't ask.** The default: a bug fix opens with a test that reproduces it, and a new behaviour gets its test written before the code that satisfies it. State that in the plan rather than leaving it open. Deviate where the behaviour genuinely can't be stated until something is built, and say so.
  - **Give each increment its tests as cases, not intentions.** "Cover the validator" is an intention. A case is a name, the input that drives it, and the observable outcome asserted — enough that someone else could write it and get the test you meant. A plan that stops at the intention leaves the test to be invented alongside the code, which is how a test ends up shaped to whatever got built instead of to the behaviour agreed here.
  - **One test per guarantee, not one per function.** Tests are scope: they cost writing, running, and reading, and they are maintained for as long as the code lives. Pin the load-bearing guarantees and the cases the design itself says are hard; don't enumerate one for every branch a reader can already see. A plan carrying more test than the change is worth gets quietly trimmed at build time by whoever is tired, which is not a decision anyone made.
  - **Some guarantees are properties, not cases.** A parser, a smart constructor, a state machine, a serialization roundtrip, a normalization that must be idempotent — for these, enumerating examples samples the space badly and a property covers it: parse-then-render returns the input, normalizing twice equals normalizing once, no legal sequence of transitions reaches an invalid state. Name the property in the plan the way you'd name a case; whether it runs under `hypothesis`, `fast-check`, or a loop over generated values is a build-time detail.
  - **Classify each dependency to pick the approach** — in-process, local-substitutable (a real stand-in runs inside the suite), remote-but-owned (port plus an in-memory adapter), or true external (injected port plus a mock pinned to a captured real response). See `module-design.md`. The last two each add a port and two adapters to build and maintain, so they belong in the sequence, not the margin.
  - *If the only way to test the design is mocking everything, the design is wrong — back to Explore.* The classification above is the constructive version of this check: it names what to substitute instead.
  - **Name the tests this retires.** When a refactor deepens a module, the tests that pinned the old pieces one by one become waste once tests exist at the new interface — they pin the implementation you just chose to hide, so they break on the next internal change. Replace, don't layer: a plan that adds a test layer without naming the layer it deletes has doubled the maintenance cost.
  - **Name the load-bearing guarantee and the test that pins it.** For each invariant the design relies on ("the validator rejects stale keys before projection," "this fires on every failure path"), decide the test that would *fail* if that guarantee regressed — exercising the real collaborator, not a mock of the thing under contract, and asserting the invariant itself, not an incidental proxy. A guarantee with no such test will silently rot. The bar is deletion: if removing the guarantee from the implementation leaves the suite green, it isn't pinned. Pin it at the site that *computes* the load-bearing value, not only at the function that receives it — a test that passes the value in leaves the call site free to stop computing it.
- **Durable machinery is a decision, not a default.** Plain calls or a single database transaction cover a simple one-boundary operation. A saga or durable workflow is *earned* when progress must survive process loss or redelivery, or when the operation needs long delays, compensation, resumability, timers, human approval, cross-service coordination, or more than one transaction boundary; a short-lived retry on its own doesn't earn it. Decide retry ownership in the same pass — an adapter owns a safe short technical retry, the application decides whether the whole operation is attempted again, and only a durable workflow owns retries that must survive a crash or a redelivery. Keep transactions closed across network calls and long-running steps: one held open for someone else's latency holds its locks for exactly that long.
- **Replay & idempotency** — does any step emit an external side effect (a payment, a published event, a notification, a downstream write) or persist an accumulated value? Then design for the unit running **more than once** — a retry, a resume after interruption, an at-least-once redelivery — not just once. The side effect needs a dedupe key derived from the work itself and stable across attempts (not from the attempt); a persisted aggregate that should be cumulative must be merged across attempts, not overwritten on completion. This is the "more than one execution" sibling of the coexisting-states problem in *Rollout shape* below, and like it, it's invisible to mock-based unit tests — plan the replay scenario and its guard at design time.
- **Out-of-diff dependencies** — does this change need something *outside the code change* to land with it? Provisioned infrastructure that can't be altered in place (a secondary-index projection, a cache/search schema), a sibling in-flight MR it assumes or collides with, or existing tests/callers that pin a shape you're renaming. Identify these at planning time and sequence them to land together — they're invisible to mock-based unit tests and surface only on merge or in production.
- **External referencers that bind by convention, not by import** — map who depends on your surface through a contract no repo grep or unit test can see: deploy/infra config keyed on a config/env-var *name*, monitors/alerts keyed on a log *substring*, a downstream service that deserializes your payload (strictly — an added field can be rejected), a public/SDK client depending on the *current default semantics*, an analytics consumer reading an event/property *shape*. Renaming, rewording, reshaping, or default-flipping any of these is a contract change to a system outside the diff. Plan to confirm or coordinate it before merge — don't assume it's unaffected.
- **Rollout shape** — feature flag, phased, dark-launch, blue-green? What's the rollback path? A change that doesn't flip atomically has **more than one state live at once** — a flag's off and on paths, old and new code during a rolling deploy, old and new schema mid-migration, two API versions in flight. Design for correctness in *every* coexisting state and in the transitional window where they overlap, not just the end state. Any "this is safe / a no-op because `<condition>`" rests on an assumption about state you may not control (the flag is on for *every* tenant, every caller is already on the new version) — name the assumption and plan to verify it, don't assume uniformity.
- **Migration pattern** (when data or contracts change) — additive first (new alongside old), switch readers, remove old. Never delete-and-replace under live traffic.

**Subagent opportunity:** in a large repo, delegate dependency analysis or test-coverage inventory to a subagent — *"what depends on this module, and what tests cover it?"* — and have it return a structured report.

---

## Lens: Validate

*Build verification into the plan, not bolted on.*

- **Acceptance evidence per increment** — what proves this slice landed correctly? Telemetry, screenshots, integration test, manual QA, customer signal.
- **A guardrail counts only once it runs.** If part of the plan's safety story is a drift test, contract test, or lint rule, decide where it executes in CI — a new package or directory is often outside the pipeline's project set or below its configured test paths, so the guard protects a laptop and everyone believes it protects the branch. Same for a check that only passes under one terminal, locale, or clock: an irreproducible guard gets disabled, not fixed.
- **Observability** — what new metric / log / alert does the changed surface need so someone can tell it's healthy in production? Enumerate the terminal paths it must cover — success, retries-exhausted, mid-stream failure, cancellation — so the instrumentation measures the failures it exists to surface, not just the happy path. A metric that only fires on success makes a broken system look healthy.
- **Rollback path** — concrete steps, not "we can revert the PR." If rollback requires a data fix, plan it now.
- **Follow-up register** — known limitations get filed as issues / TODOs *as part of "done."*

---

## Repo-convention exploration

When the work touches existing code, **read the repo before designing.** But don't enshrine accidental patterns.

The principle: **respect intentional convention, challenge emergent convention.**

- **Documented convention** — start with agent-rule files if present (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md`, or similar — these are usually the most current and explicit statement of repo conventions). Then `README.md`, `CONTRIBUTING.md`, ADRs in `docs/`, lint configs, codified style guides. These are deliberate; follow them.
- **Undocumented repeated patterns** — treat as *evidence, not authority*. A pattern repeated 50 times might be a chosen style, or it might be tech debt no one had time to fix. Look for rationale — comment, doc, recent commit message. If none, the pattern is *emergent*, not chosen.
- **Local consistency, edge improvement** — new code added to an existing module mostly follows local style. New modules can adopt better patterns. Don't fight at the molecule level; do better at the boundary.

Cite conventions inline when they shape a decision. No ceremonial block unless the user explicitly asks for a written plan.

**Subagent opportunity:** this work parallelizes well — delegate the convention scan to a subagent. Brief: *"find documented conventions in the affected area, surface emergent patterns, note anything that looks like tech debt. Return structured."* Keeps the main context focused on planning.

---

## Output

**Default: conversational.** The plan lives in the response, shaped by whatever serves the user — prose, bullets, a sketch, sometimes nothing more than the next step. No mandatory structure.

**Structure when it helps.** A complex multi-step plan benefits from explicit lens sections; a small refactor doesn't. Use judgment.

**Keep it lean.** If a paragraph defending a choice is longer than the choice itself, cut it — prose that argues a decision is not the decision.

**Show the shape rather than narrating it.** A design has a shape, and prose is the worst medium for it: pseudocode for an algorithm, a call tree annotated with what goes in and what comes back, a component tree carrying the state boundaries that matter, a shallow file tree for where things live, a sequence or state diagram for interaction over time, a diff when the surrounding shape already exists and the point is what changes. Notation replaces the paragraphs, it isn't decoration on top of them, and it carries only what the current decision turns on.

**The one non-negotiable: surface which references you loaded.** A single line, naturally placed: *"loaded react-design.md and security-design.md"* — or interspersed: *"per react-design's state-boundary prompt..."*. This is the forcing function against lazy reading; the user can catch silent skipping without any ceremonial block.

**Conventions and limitations cite inline** where they're relevant to the discussion. Don't promote them into structured blocks unless explicitly asked for a written plan.

### Persistence (explicit trigger only)

Don't volunteer to write a file. Persist only when the user explicitly asks — *"write this to PLAN.md"*, *"draft a doc"*, *"put this in the ticket"*, *"create an RFC"*.

When persistence is requested, ask once where it should go if the destination isn't obvious (file path, ticket key, comment location), then commit to that destination.

---

## Guardrails

One-line anchors — each rule lives in full in its own section above.

- Load the references matching the stacks touched before applying lenses; a shallow plan for an in-scope stack means one was skipped — load it and continue.
- Planning stops at the plan; the deliverable is the design and the ordered work, not the code.
- Conversational by default; persist to a file / ticket / RFC only when explicitly asked.
- Match depth to blast radius — no ceremony for trivial tasks, relentless grilling for expensive-to-undo ones.
- Grill to resolution, product branches first, one thread at a time, each with a recommended answer; explore the code before asking, and ask freely.
- Don't invent acceptance criteria the user didn't state — ask.
- Each increment carries its tests as cases (name, input, observable outcome), one per load-bearing guarantee rather than one per function.
- Show the shape instead of narrating it, and put competing alternatives in one notation so they can be compared.
- Don't decide before exploring, or sequence before deciding.
- Don't keep a wrapper that fails the deletion test, or place a seam nothing varies across.
- Don't hand-roll a solved UI component; check what's already installed first.
- A user-visible surface earns the Craft lens: name the reference, state the quality bar, say why each visual choice feels right.
- Don't enshrine accidental patterns; repo frequency is not endorsement.
- Engineering success isn't user success until a user notices.