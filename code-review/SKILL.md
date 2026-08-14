---
name: code-review
description: Deep code review workflow for merge requests and diffs. Use when the user says "review MR", "review this code", "code review", "check this MR", or provides an MR URL to review. Not for triaging feedback received on your own MR — that's review-feedback.
---

# Code Review

A staged review run by a **lead reviewer** (the orchestrator) with **expert subagents** doing parallel deep dives. The lead synthesizes everything into a unified view. Findings are discussed in chat first; comments are drafted only on request.

A review verifies; it does not build. The project's pre-completion rituals — run the full suite, meet a coverage gate, format the tree — belong to the author and do not apply to the reviewer. Run only what a specific question needs.

## Review Surface

Identify what is being reviewed:

- a GitLab MR
- a GitHub PR
- a local branch against a base branch
- an explicit diff or patch
- a set of changed files

Figure out base and head when needed. If ambiguous, inspect the repo or link and state the assumption you are using.

**Resolve the diff first.** Before diff stat, scope claims, or "this MR bundles X" findings, confirm you are reviewing the intended change set — not a stale or wrong base.

- For MRs/PRs: fetch the stated target branch and diff source against the **remote** target, not an unqualified local `master`/`main`.
- For local reviews: use the base the user named; if none, ask or state your assumption.
- **Sanity check:** commits and files should line up with the MR/PR description or the user's intent. A mismatch usually means the wrong base — fix that before framing, not a scope finding.
- **State what you used** in the review output (e.g. `origin/master…HEAD` after fetch).

This is separate from **merge-base / conflict-risk triage** in Phase 1: that checks whether the target moved since fork; this checks whether you are looking at the right diff.

---

The review has 4 phases. They are the **minimum** — the lead may expand in Phase 4 (spawn additional experts on a hint, verification subagents, dig in personally).

## Phase 1 — Frame

High-level understanding of the MR's scope.

1. Pull MR/PR metadata: title, description, linked issue/ticket, commit messages. For GitLab use `glab` (see the `glab` skill). If a CI pipeline is attached, pull it too: its jobs already carry the test results, lint output, and coverage for this change, so read them instead of reproducing them locally. Check the pipeline ran on head — a result for an older commit says nothing about the diff you're reviewing.
2. Read any docs referenced from the description or ticket. Read project conventions: `AGENTS.md`, `CLAUDE.md`, and `docs/` entries that the change touches. Convention violations are findings.
3. Get the diff stat against the resolved base (see **Resolve the diff first**): files touched, LOC added/removed, areas affected. Don't read file contents yet.
4. **Merge-base / conflict-risk triage** (cheap, no file reading): find the merge base against the target (`git merge-base HEAD <target>`) and how far the target advanced (`git log --oneline <target> ^HEAD`). If the base lags, check whether the target changed the same files since the fork (`git log <target> ^<merge-base> -- <files from the diff stat>`). Any overlap is a **conflict-risk hint** that decides whether Phase 3 spawns the merge-base expert — don't analyze semantics yet, just flag the overlap.
5. Build an internal frame: what the MR claims to do, declared scope, natural slices (by subsystem, layer, or feature), and the **stakes** of the surface it touches — what breaks if this is wrong, who notices, and what already absorbs failure around it (a retry, a queue, a dedupe key, a nightly rerun, a human in the loop). Stakes are read from the code and the deploy config, not guessed, and they are what makes severity mean something in Phase 4: the same defect is CRITICAL on a payment path and MEDIUM in a batch job that reruns tonight. Name the stakes once here so the whole review is calibrated to the same bar.
6. Build a **claim inventory** — the author's **load-bearing** claims, from the description, ticket, commit messages, docstrings, and comments. The test for load-bearing: *pull the claim out — does the change still stand?* If the justification, the safety argument, or the rollout plan rests on it, it's in. Incidental numbers nobody acts on (coverage percentages, test counts, line counts, timings quoted as colour) are **out** — precision drift there is not review surface. Order the inventory by leverage:

   - **The premise** — the problem the change claims to exist for: *"X is broken"*, *"this path leaks"*, *"callers hit Y"*, *"the enum drifted"*. Verify this first and hardest, against the code as it stood **before** the diff. A refuted premise moves the conversation one step back — whether to make the change at all, not how it was made — and is the highest-value finding a review can produce. A premise that holds but is narrower than the fix is the same class of finding.
   - **Safety claims** — *"X is a no-op"*, *"this can't happen"*, *"backward compatible"*.
   - **Benefit claims** — *"faster"*, *"fixes Y"*, *"simplifies Z"*. Watch the asymmetry: safety claims trigger scrutiny naturally, while benefit claims read as motivation and slip through unverified — both are claims. Capture a number and how it was measured when **the number is the argument**, not when it's decoration.
   - **Rollout and rollback claims** — *"deploys inert"*, *"dark by default"*, *"rollback is a flag flip, no redeploy"*, *"staged"*. An operator acts on those, so a description that promises a reversible staged rollout over what is actually a hard cutover is a finding even when every line of code is correct.

   The inventory travels through the review: Phase 3 experts get the claims relevant to their topic, and Phase 4 must dispose of every entry.
7. Build a **prior-art inventory**: the existing record of what's already known or discussed about this change — MR/PR review threads and their resolution state, prior review rounds, linked-ticket comments, and any in-repo registry of known issues (e.g. `tech_debt/`). For each item capture the concern and its apparent status (open / claimed-resolved / deferred). This is a first-class Phase 1 input, not an end-of-review courtesy: the highest-value findings often live *inside* this record — a thread marked resolved that the current diff didn't actually fix, or the gap a partially-addressed thread left behind. Like the claim inventory, it travels to Phase 4, where every finding is disposed against it.

If the description is empty, misleading, or contradicts the diff stat — that's a **hint** for Phase 4, not a finding yet.

---

## Phase 2 — Map

Deep understanding of what changed. Read the affected files in full — diff hunks lie about context.

The lead decides solo or delegated based on size and coupling:

- **Small / tightly coupled change** → lead reads the diff and affected files in full.
- **Large / multi-slice change** → spawn one mapping subagent per slice. Each reads its slice's files in full and reports: what changed, contracts/invariants touched, surprising behavior, callers and dependents.

No hard threshold. A 1000-line MR in one module may stay solo; a 200-line MR touching API + DB + tests is worth slicing.

Clear bugs that surface during mapping are **hints for Phase 4**, not findings. The bug expert in Phase 3 will verify and ground them properly. Don't suppress them; don't promote them to findings either.

---

## Premise gate (between Map and Deep dive)

The map is the first point where the premise is checkable — you can now read the pre-diff code the claim describes. Check it here, before spending the expert fan-out.

Read the code **as it stood before the diff** and confirm the problem the MR exists to fix was real there. Reproduce it if it's reproducible.

**If the premise doesn't hold, stop. Do not run Phase 3.** A line-level review of a change that shouldn't exist wastes everyone's time, and a long findings list buries the one thing that matters. Report to the user instead:

> "Before going further: the MR says [premise]. Reading `path/file.py:LINE` at the base commit, [what you actually found]. If that's right, the change may not be needed — or it's fixing something narrower than described. Want me to ask the author to clarify before I run the full review?"

Then wait. If the user says post, draft **one** short clarifying question — question style, no findings list attached — and let the author answer before the review continues.

Only stop for a premise that breaks the MR's purpose. A premise that's merely imprecise, or one narrower than the fix, is a Phase 4 finding: note it and carry on to Phase 3.

---

## Phase 3 — Deep dive

Always spawn expert subagents in parallel. The lead can't deep-dive into multiple topics at once — that's why this phase exists.

Decide the full expert set first (see expert selection below), then **spawn all of them in a single message** — one tool block with multiple Agent calls. They are independent; sequential batches only waste wall-clock.

The lead's main thinking step here is **expert selection**: *what topics in this MR deserve a dedicated expert?*

**Minimum experts, always:**

- **Bug expert** — adversarial bug hunter. "How would I break this?" Logic errors, edge cases, race conditions, broken invariants, unintended deletions from a botched merge, missed callers.
- **Security expert** — trust boundaries, injection, auth/authz, secret handling, permission widening, sensitive data leaks.
- **Architecture & design expert** — ambitious about structure, not just correctness. Look for "code-judo" reframings that delete whole branches, helpers, modes, or layers rather than rearrange them. Flag feature logic leaking into shared paths, file growth without decomposition, thin wrappers and identity abstractions, unnecessary sequential orchestration, special-case branches bolted onto unrelated flows, and casts/optionality/`any` that obscure the real contract. The bias is *"could this be done meaningfully better?"* not *"is this acceptable?"*. Settle the wrapper and indirection questions with the checklist's Module Depth & Seams checks instead of trading opinions about them: the **deletion test** (inline it at every call site — does complexity vanish, or reappear at N callers?), **one adapter means a hypothetical seam, two means a real one**, and the internal seam promoted into the interface because a test reached for it.

**Add experts when the frame and map justify them:**

- **Tests expert** — coverage of new behavior, determinism, regression risk, missing critical-path tests. On a refactor, also whether the superseded tests were retired: tests that pin pieces the change just hid now pin the implementation, and layering the new interface's tests on top of them doubles the maintenance instead of moving it.
- **Contracts & API expert** — schema/DTO/enum changes, breaking changes, serialization compatibility. The interface is wider than the signature: an invariant, a call-ordering rule, a new error mode, a newly required config key, or a performance characteristic callers lean on can change with no type diff at all, and each is still a breaking change.
- **Performance expert** — hot paths, fan-out, memory/leaks, blocking I/O.
- **Consumer experience expert** — when the change exposes a public/SDK/LLM-facing surface.
- **Agent context expert** — when the diff touches a model-facing surface (tool/function definitions, prompts, tool outputs, error-as-data strings, schema field descriptions). Reviews them as prompts: redundancy with the cached prefix, output that pollutes the window, off-intent hints, actionable-vs-internal errors, micro-prompt field descriptions. Loads `references/agent-context-review.md`.
- **Merge-base / divergent-target expert** — when Phase 1's triage flags a stale base with target commits touching the same regions. Reads those target commits (message + diff) to learn what they changed, then names the specific invariant a careless conflict resolution would silently drop and the test that pins it. A *detector, not a resolver*: it surfaces the semantic regression risk so the author rebases and resolves intentionally — it doesn't touch conflict markers.
- **Other** — concurrency, migrations, observability, i18n, accessibility — spawn whichever fits.

### Default is run

**Never silently skip experts.** If you genuinely believe the change is so trivial that experts are overkill (one-line typo, comment-only edit, version bump, pure formatting), STOP and ask the user — quote the specific reason, then wait:

> "This looks like [trivial reason — be specific]. Spawning bug + security + architecture experts feels like overkill. Want me to skip and synthesize directly, or run them anyway?"

Default behavior is **run experts without asking**. The ask is only the escape hatch for cases you can name precisely.

### Anti-pattern — lone-orchestrator review

*"I read the files myself, the experts would just re-read the same code"* is the failure mode, not a reason to skip: a lead anchored to the map stops seeing what's *missing from* the diff (botched merges, deleted callers, dropped contracts, adversarial inputs). The map is the *input* to the experts, not a substitute for them.

### Briefing each expert

Pass each expert subagent the frame, the map, its role, the affected files, and the **resolved diff base** (so experts do not re-derive scope from a stale local ref). **Do not pass the prior-art inventory** — keep experts blind to what was already raised. An expert that independently rediscovers a known issue is *confirming it's real*, which is more valuable than biasing it toward or away from the existing discussion. Reconciliation against prior art is the lead's job in Phase 4, not the expert's. Mutating a test to prove a guarantee is the tests expert's beat — another expert that suspects a weak test says so and moves on rather than running it too. Each expert still runs whatever its own topic needs: a repro for a suspected bug, a script, a benchmark. Instruct it to:

1. Load `references/review-checklist.md`. Add stack overlays as the diff demands:
   - **Python diff** → load `references/python-review.md`.
   - **TypeScript diff** → load `references/typescript-review.md`. If `.tsx`/JSX or React hooks are touched, also load `references/react-review.md`. If a browser-facing surface is touched (UI components, public pages, anything served to end users), also load `references/frontend-review.md`; if that surface has visual-detail, animation, or micro-interaction work, `frontend-review.md` points to `references/ui-polish.md` — load it too.
   - **Security expert** → always load `references/security-review.md` in addition to the above.
   - **Model-facing surface in the diff** → load `references/agent-context-review.md`. Trigger when the diff touches tool/function definitions, system or task prompts, prompt templates, tool result/output strings returned into a model's context, error messages that reach a model, or typed-schema field descriptions used as a tool contract.
2. Read the relevant files itself — don't trust the map's summary alone.
3. **Verify or refute the inventory claims assigned to its topic** — with evidence, never by adopting the author's reasoning. "The description says it's safe/faster/equivalent" is not evidence; a docstring asserting an invariant is a claim to test, not a fact to cite.
4. Be **exhaustive within its topic**. Enumerate the checks performed, not only the findings raised. "No concerns after checking X, Y, Z" is a valid result and surfaces gaps the lead can challenge.
5. Ground every finding with **evidence**: file path + line, code/doc snippet, reasoning that connects evidence to concern.
6. **Report everything, filter nothing.** Include findings it is uncertain about or considers low-severity — the expert's job is coverage; materiality is decided by the lead in Phase 4. Each finding carries an estimated severity and a confidence (high / medium / low). Report findings as plain factual claims, not hedged questions — the lead needs clean signal to triangulate across experts; collaborative phrasing is applied later, at presentation and comment time. If a question is empirically decidable (a benchmark, a repro, a dependency-source read would settle it), flag it as **measurable** — the lead runs the experiment in Phase 4 (*Measure, don't ask*) instead of forwarding it to the author.

---

## Phase 4 — Synthesize

The lead assembles a unified view from the experts' reports and the map-time hints.

**Findings only exist in Phase 4.** Anything spotted earlier is a hint until it reaches Phase 4 grounded with evidence. This boundary is what keeps the lead honest — you cannot ship findings without the deep dive supporting them.

Phase 4 is **active work**, not just assembly:

- **Dedupe** findings raised by multiple experts.
- **Filter for materiality.** The experts report coverage — everything they saw, low-confidence items included. Deciding what survives is the lead's job: drop or demote what changes no decision, and keep the list proportional — a few high-conviction findings beat a long tail of cosmetic ones. A low-confidence report that a second expert independently corroborates is signal, not noise — triangulate before dropping.
- **Filter the remedy, not the finding.** An expert reports a concern and usually the fix it imagined; those are two judgements and only the first is its job. When the concern holds but the remedy it implies is out of proportion to the stakes — a retry layer, an abstraction, a config knob and three new states, to close a case nothing reachable produces — keep the finding and carry the cheapest thing that would settle it instead: an assertion on the unexpected state, a narrowed type that makes it unconstructable, one line naming the invariant and why it holds, a test that fails the day it stops holding, or a tracked follow-up. Never drop a finding because its fix looks expensive; a real risk that only a heavy remedy closes is a DESIGN finding about the shape. Hold the bar in the other direction too — where the tail is expensive (security boundaries, data loss, money, PII, published contracts other deploys depend on) low probability doesn't shrink it, so harden without arguing.
- **Resolve contradictions** between experts — look at the evidence and pick, or escalate to the user.
- **Spot gaps.** An expert that returned light may have missed something the frame flagged as risky. Push back, rerun, or dig in yourself.
- **Drop ungrounded findings.** Anything without file:line + evidence gets dropped or sent back for grounding. This is the hallucination check.
- **Verify CRITICAL and HIGH.** Open the cited files and confirm the claim against the actual code.
- **Dispose of the claim inventory.** Every claim from Phase 1 ends in exactly one state: **verified** (with evidence), **refuted**, or **unverified** (stated explicitly in the output; silence is not a state). Start with the premise: if it doesn't hold, or holds only over a narrower case than the fix covers, that outranks every other finding — say so first and frame the review around whether this is the right change, not how it's written.
- **A refuted claim becomes a finding only when it changes a decision.** Before writing one up, name what the reader does differently. A refuted premise reopens whether the change is needed. A refuted safety or rollout claim changes how it ships. A refuted benefit removes the reason to merge. If the answer is *nothing* — the description says 91% and it's 91.1%, says 1000 tests and it's 1002, rounds a timing — correct it in one line in the Claims Audit and drop it. Never a finding, never a comment. Litigating decimals spends the credibility the real findings need.
- **Reconcile against prior art — classify, don't suppress.** Dispose every finding against the Phase 1 prior-art inventory, and give each a disposition relative to prior discussion (silence is not a state). A small open vocabulary: **new** (not previously raised) · **already-raised** (duplicate — link the thread and drop it unless you have materially new evidence or framing) · **partially-addressed** (the thread's core was fixed but a gap remains — *the gap is the finding*) · **deferred** (author acknowledged and punted — re-raise only if severity now justifies escalation) · **claimed-resolved** (verify against the *current* diff before trusting; a thread marked done that the diff didn't actually fix is a high-value finding). The point is to annotate, not delete: presenting an already-settled point as a fresh discovery wastes the author's time, but suppressing a duplicate that's actually a live gap hides the most valuable findings. Independent rediscovery by a (prior-art-blind) expert *raises* confidence — note it as confirmation, don't discount it.
- **Measure, don't ask.** If a question — yours or an expert's — is empirically decidable with a cheap experiment (run the code, benchmark the two variants, read the installed dependency's source, write a 10-line repro), run the experiment and report the result. Reserve questions for genuine judgment calls. Experts often surface these as *"worth profiling?"* / *"does this actually happen?"* — those are work items for the lead, not questions to forward to the author. Bootstrap experiments from the project's own test setup (conftest, fixtures, env stubs) rather than fighting app configuration. Measure what the expert reports left open — re-running an experiment an expert already ran buys nothing. The one to reach for by default is the **deploy repo read**: when a finding hinges on whether a setting, secret, route, index, or event registration exists in an environment, check the deploy/GitOps repo instead of asking the author to confirm it.
- **Follow hints.** If an expert report hints at something outside its topic, expand the work: spawn an additional expert, a verification subagent, or check yourself. The 4 phases are the floor — expand as the evidence demands, but expansion needs a **named hint** from the evidence, not thoroughness for its own sake.
- **Simplification sweep.** Even if experts came back clean on their topics, ask the meta-question nobody owns: *is there a reframing that would make this dramatically simpler?* A diff can pass every topical check and still miss the inevitable-in-hindsight structure. Look for: branches/layers/modes that could disappear with a different model, feature logic that should live elsewhere, file growth that should have been a decomposition, sequential orchestration that's serial for no reason. If something surfaces, raise it as a DESIGN finding — don't bury it because "the change works."

Then present the **lead's unified view** in chat (next section). Don't expose individual expert reports — the user wants the synthesis, not committee minutes.

---

## Present Findings

#### TL;DR

This is the reader's whole model of the change. Assume they will not open a file: when they finish these ~200 words they should be able to predict where things live and argue about the design. Four slots, in this order:

- **Ships**: one or two sentences. The capability in the product's own words, who calls it, and the problem or ticket it exists for.
- **Mechanism**: the path a call takes through the change, entry point to storage, in 3 to 6 steps. A path is an ordering, so draw it as one — a call chain, not a paragraph the reader has to re-order in their head. Every step names something the reader could grep (a module, class, method, route, table, queue, event, or flag key) *and* what crosses it: the value passed in, what comes back or gets written. A step with no name in it is describing the shape instead of the change; a chain with no values on it shows the order and hides the thing that actually moves. Where the change isn't a call path — a state machine, a migration — draw the shape it is.
- **Reach**: what this touches outside its own files (contracts, published models, shared paths, other services) and the switch that turns it on (flag key and default, env var, config). One line each; the per-change detail goes in Contract Changes below, so do not restate it here.
- **Risk**: one line. Count the blocking findings and point at their numbers. No detail, no mechanism, no argument. The reader has the Findings section for that.

Report mechanism, not appraisal. Nothing here judges the change, the author, or the MR description, and nothing here is a claim the reader could not check for themselves. Assessment of the description belongs in the Claims Audit, and so does the work the review did to earn its confidence (mutations, repros, deploy-repo reads).

#### Contract Changes
Changes to domain models, DTOs, DB schemas, enums, type definitions, constants. Every entry is a before and after, so show it as one: a table (field, before, after, breaking?) or the declaration diff, with the compatibility note in the row rather than a paragraph after it. Prose is worst at exactly this shape, because it makes the reader hold the old declaration in memory while reading the new one. Omit if none.

#### Claims Audit
The MR's load-bearing claims and their fate: **verified** (with the evidence), **refuted** (link the finding, or state the correction in one line where it changes no decision), or **unverified** (with why it wasn't checked). One row per claim, verdict before evidence — the reader scans this section for what wasn't checked, and a paragraph per claim buries it. Lead with the premise. Omit if the MR makes no load-bearing claims.

#### Findings

One block per finding, sorted CRITICAL > HIGH > MEDIUM > DESIGN > LOW > SMELL:

```
#### Finding #N
- **Priority**: CRITICAL | HIGH | MEDIUM | DESIGN | LOW | SMELL
- **Location**: `path/to/file.py:LINE`
- **Issue**: brief description
- **Why it matters**: impact — what could go wrong, what invariant is violated, or what a simpler structure would buy
- **Evidence**: the code/doc snippet the finding rests on
- **Reachability** (whenever the finding asserts a failure mode): what actually produces the bad state — a traced caller, an input the user controls, a retry path, a record that predates the change — or `not traced`, said explicitly. This is what lets the next reader price the fix, and it keeps the review honest in both directions: a guard against a state nothing can construct misleads whoever preserves it later, and "this can't happen" is a claim needing the same trace a fix would.
- **Prior discussion** (optional): the finding's disposition relative to prior art — `new` / `already-raised` / `partially-addressed` / `deferred` / `claimed-resolved` — with a link to the thread when it isn't new. Omit only when the change has no prior-art record at all.
- **Proposed fix** (optional): include only for CRITICAL/HIGH bugs where the correct fix is obvious from the diff. Omit for DESIGN/SMELL — pose the concern as a question and let the author decide. When included, phrase collaboratively (*"I think the fix is X because Y — does that line up?"*), not as a directive.
```

**Priority guidance:**

| Priority | Use when |
|---|---|
| CRITICAL | Data loss, security vulnerability, logic error that will cause incorrect behavior in production |
| HIGH | Bug likely to surface, significant type regression, broken contract |
| MEDIUM | Correctness risk under non-obvious conditions, missing test for critical path |
| DESIGN | The change works, but a meaningfully simpler structure is available. Code-judo reframings that delete branches/layers, missed decompositions, feature logic in shared paths, thin wrappers, casts/optionality obscuring the real contract. Pose as a question — exploring the design *is* the value. |
| LOW | Style, readability, minor inconsistency |
| SMELL | Something looks wrong or fragile but full impact is unclear — flag for human investigation |

#### Comment style

Two rules, both about making the author think rather than comply.

**Write in simplified technical English (ASD-STE100).** One idea per sentence. Short sentences, active voice, present tense. Simple everyday words. No idiom, no metaphor, no hedging stack ("it might perhaps be worth possibly"). The reader may not share your first language; ambiguity in a review comment costs a round trip.

**Ask, don't assert.** Many readers are junior. A confident directive gets followed without thought — you get the edit you asked for and lose the reasoning that would have caught your mistake. So point at the code, say what you observed, and ask what they intended:

- state the observation, then the question — *"this runs inside the retry loop. was that intended?"*
- ask about intent or invariant, not about obedience — *"what keeps `x` non-null here?"* beats *"add a null check"*
- give your reasoning so they can refute it — a claim they can check is a claim they can push back on
- leave the conclusion to them, even when you are confident. If you are certain and it's a CRITICAL/HIGH bug, still write *"I think this drops the second call — does that match your reading?"*

Never phrase a judgment call as settled. Never argue a decimal (see the Phase 4 materiality gate).

#### Example phrasing

Aim for collaborative, question-led findings. The author lives in this code daily; the review opens a conversation, it doesn't issue verdicts.

- *"this grows the file materially without splitting anything out — should we decompose first?"*
- *"this adds a special case into an already busy flow — could it move behind its own abstraction?"*
- *"this works, but it makes the surrounding code more tangled. is there a way to keep the behavior and restructure the implementation?"*
- *"this feels like feature logic leaking into a shared path — can we isolate it?"*
- *"this abstraction looks like it's mostly pass-through — would the direct call be clearer?"*
- *"why the cast / optional here? could the boundary be made explicit instead?"*
- *"i think there's a reframing here that makes these branches disappear — worth exploring?"*
- *"this refactor moves complexity around, but doesn't really delete it — is there a simpler underlying model?"*

Avoid: *"X is happening, do Y."* Avoid prescriptive fixes for anything that isn't a clear bug.

---

## Discuss

Back-and-forth conversation. The user may challenge a finding, drop one, reprioritize, ask for reasoning, or add new concerns. Adjust based on the discussion. No files to edit — the conversation is the working medium.

---

## Re-review (after the author pushes fixes)

A second pass is a review of the *new head*, not of the changelog. The failure mode is accepting "fixed in `<sha>`" and resolving.

- **Verify at head, from the code.** Re-read the changed lines at the current commit. A commit message is a claim; the diff is the evidence.
- **Re-run the experiment that found it.** If the finding came from a repro, a mutation, or a measurement, run that same thing again against the new head — a fix can address the symptom you described while leaving the mechanism intact. Where the fix's whole point is a new guarantee, mutate *the fix* and confirm a test now fails.
- **Give every thread a disposition.** `fixed` (with what you verified) · `fixed differently` (the author took another shape — say whether it holds) · `acknowledged, non-blocking` · `deferred` (with where it's tracked) · `still open` (with what's missing). Silence reads as agreement.
- **Resolve your own `fixed` threads; leave everyone else's alone.** Once posting is authorized, close threads *you* opened whose disposition is `fixed`. Never resolve a thread someone else started — note its disposition in the summary and let them close it (see the `glab` skill's Resolving a Discussion Thread).
- **Resolving doesn't need a comment.** A `fixed` thread that's genuinely done just gets resolved — skip the filler reply ("verified, looks good") before closing it. Reply only if there's something substantive to say (what you verified, a caveat, a partial fix).
- **Watch for the fix that moves the problem.** A repair one layer up, a guard that now covers the reported case but not its sibling, a test that pins the function but not the wiring — these are new findings, not resolved ones.
- **Retract your own refuted claims explicitly, in the thread where you made them.** If the author shows your premise was wrong, check *their* correction against the code and then say plainly that yours doesn't survive. Never re-raise a claim you've retracted, and don't leave a wrong claim standing because the finding was directionally right — the record is what the next reader trusts.
- **Re-sample before writing.** On a long review, re-read the head and the thread state before posting; asking for something the author pushed an hour ago costs their trust in the whole pass.

---

## Draft & Post Comments (on demand)

Only when the user explicitly says to post, submit, or draft comments:

1. Load `references/conventional-comments.md`
2. Map agreed-upon findings to the format
3. For each finding, decide placement: **new thread** by default; **reply on an existing thread** instead when the finding fits one already open on that file/line or topic — yours from a prior round, or a colleague's. Don't fork a duplicate thread next to a live conversation that already covers the ground. Skip `already-raised` findings entirely; reframe `partially-addressed` / `deferred` ones around the live gap or the escalation reason, not the original point.
4. Show the full batch to the user for final confirmation
5. Post via the platform's API (for GitLab see the `glab` skill — Draft Notes workflow, and Resolving a Discussion Thread for closing threads per the Re-review step below)

**Do NOT post anything until the user explicitly says to.**

---

## Save Artifact (on demand)

Only if the user explicitly asks for a review file, save findings to `review-<MR_IID>.md`. Conversation is the default medium.

---

## Guardrails

One-line anchors — each rule lives in full in its own section above.

- Always spawn the experts; if the change seems too trivial for them, ask — never skip silently.
- Findings exist only in Phase 4, grounded with file:line evidence; everything earlier is a hint.
- Verify the premise before the solution — a premise that breaks the MR's purpose halts the review.
- Experts report coverage; the lead filters. Materiality calls happen in Phase 4, not in expert reports.
- Filter the remedy, not the finding — stakes named in Phase 1 calibrate severity, and a real risk with an expensive fix is a DESIGN finding, never a dropped one.
- Measure over asking — forwarding an empirically decidable question to the author is a review gap.
- A review verifies, it doesn't build: read the pipeline, run only what an open question needs, and don't repeat a run another expert already made.
- Dispose every claim and every prior-art thread explicitly; silence is not a state.
- Comments are question-led, in simplified technical English. Never post or resolve without explicit go-ahead, and only resolve threads you opened.
- Expand beyond the 4-phase floor only on a named hint from the evidence.
- Project conventions (`AGENTS.md` / `CLAUDE.md` / `docs/`) are review surface — violations are findings.
- Scope findings require the resolved diff base; a wide diff against a stale local target is a wrong-base mistake, not a finding.