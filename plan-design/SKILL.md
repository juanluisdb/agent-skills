---
name: plan-design
description: Turn an idea into a real plan — frame, explore, decide, craft, sequence, validate. Grills you on the open decisions, product-first, and lands on work a builder can pick up. Use for a feature idea, refactor, UI where taste and polish matter, or to be grilled before building.
---

# Plan & Design

Planning is **triage, not a march**. The shape of the work — raw idea vs detailed spec vs half-implemented — decides which lenses to apply and in what order. This skill diagnoses where you are and how you want to work, then applies lenses (Frame / Explore / Decide / Craft / Sequence / Validate). The engineering judgement the lenses apply lives in the `software-design` skill, which this one always loads.

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

Planning isn't just proposing and iterating — it's **grilling**. The lenses surface a **design tree**: every decision branches into the decisions that hang off it. Grilling walks that tree *with* the user until you reach shared understanding. Calibrate intensity to blast radius: a one-line fix earns no grilling; an expensive-to-undo design earns a relentless pass.

### Which decisions become nodes

Triage every open decision the lenses surface into one bucket:

| Bucket | Test | Action |
|---|---|---|
| **Product-observable** | The user sees, feels, or behaves differently by the answer | A node. Ask it in product terms |
| **Consequential technical** | Shape, trade-off, or anything expensive-to-undo — no product-visible difference, but the engineer should weigh in | A node. You're planning *with* a product engineer, not a black box — surface these, don't hide them |
| **Trivial engineering** | No observable difference, cheap, reversible | Not a node. Decide it yourself, don't raise it |

The failure to avoid: burying a product-observable decision as "trivial" because it was easier not to ask — *and* its mirror, black-boxing a consequential technical call the engineer would want to make.

### Work the tree in rounds

The **frontier** is every node whose prerequisites are already settled: the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for the answers. A question whose answer depends on another question open in this round belongs to a *later* round, not this one.

Each round of answers reshapes the tree — settled decisions push the frontier outward, unblock what depended on them, and dissolve questions that no longer matter. Recompute the frontier from the answers you actually got. That reshaping is the whole mechanic: never walk a question list drawn up before the user started answering.

**Order the frontier product-first, but prerequisites win.** Usually the product-observable decisions root the tree and the technical ones hang off them, so the early rounds are about *what* we're building from the user's point of view. When a technical answer is genuinely a prerequisite — the storage model decides which product behaviours are even on the table — ask it first and say why it comes first.

**Set the context the round needs, once.** Open with the shared setup the questions hang off — the area we're in, what the code does there today, what the last round settled — then let each question name only what's specific to it. One explanation can serve several questions and several rounds; repeating it under each one is a wall to read, and dropping it makes the round unanswerable. Name a thing before asking about it, wherever that naming lands.

Format each question:

```
❓ **Q1** - **<question title>**: <question body, may run to several paragraphs, including the choices>

➡️ <your recommended answer>
```

### Per question

- **Always offer a recommended answer** so the user can say "yes, that" instead of inventing one. Recommend from the code and the lenses, not a coin flip.
- **Put the competing choices in one notation** — the discipline the Explore lens applies to alternatives, applied inside a question. Two choices in prose aren't comparable; in one notation they are, and that comparison is what the question is asking for. Pick from the menu in *Output* below, plus the one it doesn't list: a worked example traced end to end with real values, which often lands better than any diagram. Every question with a shape gets its own, carrying only what that question turns on. A notation on Q1 and prose from there has shown the easy part — the questions late in a round are the ones the user can least rebuild from paragraphs.
- **When a question doesn't land, diagnose what to change.** The same content in different words fails the same way it failed the first time, so pick the axis. *"What?"* or a sentence carrying three unexplained terms wants plainer words. *"Tell me more about X"* wants more detail, and answering a request for depth with a summary is the most common way to miss twice. Several moving parts, an order of events, or who calls what means the medium is wrong: switch notation, or trace one real example through with actual values. Drop the jargon and keep the level — the user lost one thread, not the field.
- **Facts are your job, never the user's.** When a frontier question turns on something the environment can settle — the filesystem, the code, a tool — dispatch an `Explore` subagent and find out; never ask what a grep can answer. Don't block the round on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait, and the rest of the frontier goes out now. When something genuinely can't be inferred, say so plainly and name exactly what you need.
- **Surface trade-offs as scope levers** — when a choice meaningfully changes cost, hand over the lever in the user's currency (time, risk, scope): *"drop the animation and this ships today; keep it and it's another day."* Let the user trade scope for speed deliberately.

**Done when the frontier is empty** — every branch visited, every consequential decision resolved or explicitly deferred, nothing left silently assumed. Not when the first plausible answer arrives. Don't move on to the plan until the user confirms you have reached shared understanding.

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

- **Which surfaces does this touch?** Code only, or a user-visible surface as well? Drives which knowledge loads (next section).
- **What product surface is affected?** User-facing? Internal tool? Infrastructure? Shapes the Frame lens heavily.
- **What's the blast radius?** Reversible (rename, internal helper) or expensive-to-undo (DB schema, public API, auth model)? Calibrate effort to blast radius.

**Subagent opportunity:** in a large or unfamiliar repo, delegate codebase exploration to a subagent before triage — surface agent-rule files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, etc.), READMEs, and contributing docs; map relevant modules and conventions; note recent changes. Keeps main context lean.

Name the entry state and what you loaded in passing as you start — a natural sentence, not a ceremonial block.

---

## Load the design knowledge

**Load `software-design` before applying any lens.** It holds the judgement the lenses apply: module depth and seams, interfaces and error models, data and state, security, test strategy, rollout and idempotency, observability. Load its own references by its load conditions, and load them generously — a skipped reference drops a whole dimension from the plan (the trust boundary, the replay path, what the tests actually pin).

**Load `visual-design` when a user-visible surface is in scope** — a new screen, a redesign, "make this nicer", or any work where motion and visual detail matter. The Craft lens below is what puts it to use.

Anything below the level of that judgement belongs to the repo, not to a skill: the agent-rule files, the type and lint config, and the code around the change. Stack-level convention is read from there rather than carried here. See *Repo-convention exploration*.

**Surface what you loaded** — a single natural mention at the start (*"loaded software-design, plus its security and operations references"*) or interspersed as you apply prompts (*"per the dependency categories in software-design..."*). This is the forcing function against lazy reading; the user can catch silent skipping without any ceremonial output blocks.

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
- **If the consumer is a program or an agent, the envelope is part of the design** — and on failure paths as much as success. Decide the status, exit-code, and format contract here, at framing time; retrofitting it is how a rejected result ends up reported as a success. `software-design`'s interfaces reference has the specifics.

---

## Lens: Explore

*Two-plus approaches before converging. The design-it-twice principle.*

Apply heavy when the approach is undecided. Skip when the user has explicitly committed to an approach.

- **Generate alternatives with meaningfully different trade-offs.** Not minor variants — distinct shapes: the cheap MVP, the polished long-term design, the build-vs-buy alternative.
- For each: shape sketch, what it makes easy *now*, what it makes easy/hard *later*, product implications (not just technical).
- **Write each alternative in its own notation, not as a paragraph about it.** Types and signatures, a call tree, a component tree, a file-tree diff — whichever the change is shaped like. Two alternatives described in prose aren't comparable; the same two in one notation are, and that comparison is what this lens exists to produce. It also moves the disagreement earlier: a shape the user can read is a shape they can reject while rejecting is still free.
- **Coupling & cohesion check** — what would have to change if X changes? Prefer depth: a lot of behaviour behind a small interface, so callers learn little and change concentrates in one place.
- **Test the indirection each alternative adds, don't argue it.** The **deletion test** and the **one-adapter-versus-two** check both settle it mechanically (`software-design`), and *where* the seam goes is its own decision rather than something inherited from the current file layout.
- **Design so the two can't disagree, rather than detecting when they do.** When the shape lands in two places — a model and its wire mirror, a rule and the lint that checks it, a registry and its per-variant maps — the choice is between one definition and two definitions plus a drift test. Take the detector deliberately if you take it (`software-design`).
- **Decide how you'd test it while the shape is still open.** Classify the dependencies each alternative needs (`software-design`). The remote and external categories each buy a port and two adapters, so the classification is a cost that separates the alternatives, not a detail to discover later. And if an alternative's only testable form is mocking everything, that's a verdict on the design — reject it here, where changing shape is still free.
- **Naming as design** — if you can't name the concept cleanly, the domain isn't settled. Try writing the docstring or one-line description first.
- **Offer the cheaper path explicitly.** Don't just enumerate alternatives — name the trade-off as a choice the user can take: *"if we drop X we gain Y now, at the cost of Z later."* The simplest version that still delivers the value is a first-class option, not a fallback; surface it so the user decides the scope/effort trade rather than having it decided for them.
- **Build-vs-borrow ladder.** Before designing custom code, walk the rungs: does the standard library, the platform/framework, or an *already-installed* dependency already do this? Reach for a new dependency only when none do — it's a long-term cost (transitive weight, upgrades, CVEs), while custom code is a maintenance cost. Name which you're taking on and why.
- **UI components are the strongest rung on that ladder.** Dialogs, popovers, menus, comboboxes, command palettes, toasts, virtualized lists, drag-and-drop, animated numbers, code-verification inputs: a solved component almost always exists, and hand-rolling one is the default mistake. The reason isn't typing time — focus management, dismissal, keyboard semantics, and interruption handling are the actual difficulty, and they fail late, in production, on someone else's device. Read `package.json` before naming anything; if a competitor of your preferred pick is already installed, use it and flag the mismatch rather than churning the dependency.

Apply the judgement already loaded — depth and seam placement, the interface and its error model, the data shape, the threat boundary if an alternative crosses one. This lens does not introduce new criteria; it *uses* them to separate the alternatives.

**Subagent opportunity — design it twice.** Your first idea is unlikely to be the best one, so develop the alternatives in parallel rather than iterating on the first. Vary the subagents along whichever axis is genuinely open:

- **Scope open** — one explores the MVP, one the long-term design, one a buy-or-borrow path.
- **Scope fixed, shape open** (most refactors and extractions) — give each a different interface constraint: *minimise the interface, one to three entry points, maximum behaviour behind each* · *maximise flexibility and extension* · *make the most common caller's case trivial* · *ports and adapters, when a dependency crosses a network or vendor seam*.

Brief each with the file paths, the coupling details, and the dependency category — not with your own preferred answer. Ask each for the interface *including* its invariants, ordering constraints and error modes; a usage example written from the caller's side; what the implementation hides; the adapters it needs; and where its leverage is thin. Then compare the returns on depth, on where change concentrates, and on seam placement, and recommend one — a hybrid if elements combine well.

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

The judgement is in `visual-design` — hierarchy, spacing, type, colour, copy, the state stories, the motion values, and the discipline of saying *why* each choice feels right. Load it and use it. What this lens adds is the planning that has to happen around it:

- **State the quality bar as scope.** Everyone ships things that work, so "it works" doesn't distinguish the result — how it looks, reads, and feels does. Decide what level of finish this surface gets, and name the polish you're deliberately dropping so it reads as a choice rather than an omission. Craft deferred without being named never lands.
- **Agree the reference product up front.** Which shipped product does this pattern well, and what specifically are we taking from it? Ask the user if they have one in mind; propose two or three if they don't. A surface planned without a reference converges on the generic answer, and this is the cheapest moment to settle it.
- **Hand over the polish trade-off as a scope lever.** *"Drop the animation and this ships today; keep it and it's another day."* Let the user trade finish for speed deliberately.
- **Budget a fresh-eyes pass in the sequence.** Timing and spacing flaws you're blind to on build day are obvious the next morning. That pass is planned work with a place in the order, not optional rework.
- **The awkward states are increments, not details.** Empty, exactly one, far too many, the longest plausible string, missing data, no permission. They are cheap to plan and expensive to retrofit, so they get named in the sequence rather than discovered during the build.

---

## Lens: Sequence

*Turn the design into ordered, atomic work.*

- **Atomic increments** — each commit / PR leaves main green. No "partial state" landings.
- **Refactor-first ordering** — shape changes before behavior changes. Easier to review, easier to revert independently.
- **Test strategy upfront.** What makes a test worth writing is in `software-design`'s testing reference; what Sequence adds is that the strategy becomes part of the plan rather than a build-time improvisation:
  - **Each increment carries its tests as cases, not intentions.** "Cover the validator" is an intention. A case is a name, the input that drives it, and the observable outcome asserted — enough that someone else could write it and get the test you meant. Stopping at the intention leaves the test to be invented alongside the code, which is how a test ends up shaped to whatever got built instead of to the behaviour agreed here. A property is named the same way when the guarantee is a property.
  - **When tests get written — recommend, don't ask.** A bug fix opens with the test that reproduces it; new behaviour gets its test before the code. State that in the plan rather than leaving it open, and say so explicitly when the behaviour genuinely can't be stated until something is built.
  - **One test per load-bearing guarantee, and name the layer this retires.** A plan carrying more test than the change is worth gets quietly trimmed at build time by whoever is tired, which is not a decision anyone made. A plan that adds a test layer without naming the one it deletes has doubled the maintenance cost.
  - **The dependency classification is a cost in the sequence.** A port and two adapters is work to schedule, not a detail to discover. And if the only testable form of the design is mocking everything, that's a verdict — back to Explore, where the shape is still free.
- **Turn the shipping dimensions into ordered work.** Replay and idempotency, coexisting states, out-of-diff dependencies, external referencers that bind by convention, migration ordering, and whether durable machinery is earned are all judged in `software-design`'s operations reference. Sequencing is where each one becomes a step someone does: the provisioning that ships *ahead*, the sibling change to coordinate merge order with, the referencer to confirm rather than assume before merge, the backfill and the reader switch as separate landings, the dedupe key decided with the step that emits, the rollback path written down.
- **Rollout shape is part of the sequence.** Feature flag, phased, dark launch, blue-green — and the transitional window is designed, not discovered. Any "this is safe because `<condition>`" gets an owner and a check, not a nod.

**Subagent opportunity:** in a large repo, delegate dependency analysis or test-coverage inventory to a subagent — *"what depends on this module, and what tests cover it?"* — and have it return a structured report.

---

## Lens: Validate

*Build verification into the plan, not bolted on.*

- **Acceptance evidence per increment** — what proves this slice landed correctly? Telemetry, screenshots, integration test, manual QA, customer signal.
- **A guardrail counts only once it runs.** When part of the plan's safety story is a drift test, contract test, or lint rule, the plan says where it executes in CI. A guard in a package outside the pipeline's project set protects a laptop while everyone believes it protects the branch.
- **Observability is a deliverable, not a follow-up.** What new metric, log, or alert does the changed surface need so someone can tell it's healthy, and which terminal paths does it have to cover? `software-design`'s operations reference has the failure-path enumeration; the plan's job is to give it an increment.
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

**The one non-negotiable: surface what you loaded.** A single line, naturally placed: *"loaded software-design plus its security and testing references"* — or interspersed: *"per the dependency categories..."*. This is the forcing function against lazy reading; the user can catch silent skipping without any ceremonial block.

**Conventions and limitations cite inline** where they're relevant to the discussion. Don't promote them into structured blocks unless explicitly asked for a written plan.

### Persistence (explicit trigger only)

Don't volunteer to write a file. Persist only when the user explicitly asks — *"write this to PLAN.md"*, *"draft a doc"*, *"put this in the ticket"*, *"create an RFC"*.

When persistence is requested, ask once where it should go if the destination isn't obvious (file path, ticket key, comment location), then commit to that destination.

---

## Guardrails

One-line anchors — each rule lives in full in its own section above.

- Load `software-design` before applying lenses, and `visual-design` when a surface is user-visible; a plan that skips a whole dimension means a reference went unread — load it and continue.
- Planning stops at the plan; the deliverable is the design and the ordered work, not the code.
- Conversational by default; persist to a file / ticket / RFC only when explicitly asked.
- Match depth to blast radius — no ceremony for trivial tasks, relentless grilling for expensive-to-undo ones.
- Grill in rounds: ask the whole frontier at once, numbered, each with a recommended answer; recompute the frontier from the answers, and stop only when it's empty.
- Find facts yourself with a subagent rather than asking, and don't hold the rest of the round while it runs.
- Don't invent acceptance criteria the user didn't state — ask.
- Each increment carries its tests as cases (name, input, observable outcome), one per load-bearing guarantee rather than one per function.
- Show the shape instead of narrating it, and put competing alternatives in one notation so they can be compared.
- Don't decide before exploring, or sequence before deciding.
- Don't keep a wrapper that fails the deletion test, or place a seam nothing varies across.
- Don't hand-roll a solved UI component; check what's already installed first.
- A user-visible surface earns the Craft lens: name the reference, state the quality bar, say why each visual choice feels right.
- Don't enshrine accidental patterns; repo frequency is not endorsement.
- Engineering success isn't user success until a user notices.