# Agent Context Review Practices

Deep-dive reference for reviewing **model-facing surfaces** — the strings and structures an LLM reads at runtime. Load this alongside the review checklist when the diff touches any of:

- tool / function definitions (names, descriptions, parameter schemas)
- system or task prompts, prompt templates, enriched-message construction
- tool result / output strings returned into the model's context
- error messages that reach a model (error-as-data), as opposed to internal/terminal errors
- typed-schema field descriptions (Pydantic `Field(description=...)`, JSON Schema `description`) used as a tool contract

Distilled from agent context-engineering principles — the subset that shows up as findings *in a code diff*. Orchestration, harness design, evaluation, and long-horizon execution are out of scope here; this is about the tokens a diff adds to or removes from a model's window. Generic by design — examples are named *as examples* of a pattern, not requirements.

The premise underneath every check: **everything the model reads is a prompt.** A tool description, a parameter name, a result footer, and an error string all shape behavior with the same force as the system prompt. Review them with prompt-level scrutiny, not as inert plumbing.

## The Cost Model (why these findings matter)

Three forces make model-facing text different from human-facing text:

- **Context rot / pollution** — model accuracy degrades as the window fills, well before any token limit. Every irrelevant or redundant token competes for attention with every useful one. "More context" is not "better context."
- **Cache economics** — stable prefixes (system prompt, tool definitions) can be cached an order of magnitude cheaper than uncached tokens. Per-result output text is the *expensive*, uncached, repeated-every-call copy.
- **Lost in the middle** — models attend most to the start and end of context. Buried instructions get missed.

A reviewer's job on these surfaces: every added token should earn its place. The bar is not "is it accurate?" but "does this token change what the model does next, and is this the cheapest place to say it?"

## Redundancy & the Cached-Prefix Rule

The highest-yield check, and the easiest to miss.

- **Don't repeat in per-result output what the stable tool/prompt definition already teaches.** If the tool description says "documents are available for single-company queries," a result footer repeating "call again with one id to get documents" pays uncached, per-call tokens to restate the cached prefix — *and* adds pollution. Say durable facts once, in the stable (cacheable) location.
- **Trace each runtime string back to the definition.** For any instructional string emitted in a result, ask: is this already in the tool description / system prompt? If yes, it's a candidate for deletion, not duplication.
- **Watch for the same fact in three places** — description, schema field description, and output. Pick the one the model reads at the moment it needs the fact.

## Output Discipline — What the Next Step Needs

Tool output is context that shapes the next action. It should carry what the agent needs to decide its next step — no more, no less.

- **Semantic over raw** — resolve internal IDs to human-readable names before returning. A bare UUID forces a follow-up call or a guess.
- **Trim to relevance** — a 200-field response where the agent uses 5 fields is pollution. Filler cells, repeated boilerplate, and decorative structure all spend attention.
- **Verbose tool outputs are a leading cause of context rot** — flag large dumps that could be summarized or paginated. The model re-reads them every turn until compacted.
- **Cryptic is as bad as verbose** — encoded blobs, unexplained codes, and raw structures the model must reverse-engineer waste recovery attempts.

## Hints Must Be Responsive to Intent

Teaching the agent "how to get more" is a good pattern — *when the missing thing is plausibly wanted.* This is the subtle judgment call, not a rule.

- **Pagination / truncation hints are usually justified** — an agent that asked for page 1 plausibly wants page 2. "Showing first 20 of 347; pass `offset` to see more" teaches recovery instead of silently hiding data.
- **Off-intent nudges are pollution** — a hint that fires on *every* result steering the agent toward an action that's rarely relevant to why it called the tool (e.g. nudging a market-wide discovery query toward a single-entity drill-down) costs tokens on every call and is usually ignored.
- **The test**: is the suggested next action responsive to the intent that produced *this* result, or is it a generic "you could also…" that fires unconditionally? The former earns its place; the latter is a candidate to cut or make conditional.
- **Don't silently truncate.** If output is capped, sampled, or filtered, say so — silent truncation reads to the model as "this is everything."

## Error Messages — Two Audiences, Two Standards

Errors split into two kinds, and they have opposite requirements. Identifying *which path a raise takes* is part of the review.

- **Error-as-data (reaches the model)** — must be actionable for recovery: what went wrong, why, and what to try instead. `Error: 403` teaches nothing; "Permission denied — the API key lacks write access; use a read-only operation or request elevated permissions" tells the model its next move. These are prompts.
- **Internal / terminal errors (do not reach the model)** — raised to fail the request, logged for operators, never routed into model context. For these, leaking an internal identifier (a variable name, a config key) is *fine* — it aids debugging and the model never sees it. Don't "fix" an internal error string to be model-friendly; that's wasted effort and may weaken the operator signal.
- **Verify the routing, don't assume it.** Trace the raised type through the execution loop: is it converted to error-as-data, or re-raised as terminal? The right finding sometimes is "no change — this is correctly internal." A checklist that says "all error strings must be model-friendly" gets this wrong.
- **Preserve error traces in context where the model must adapt.** Failed actions and their errors are high-value context for a model deciding what to try next — don't strip them in the name of tidiness.

## Schema Field Descriptions Are Micro-Prompts

Every `description` on a parameter or model field is read by the model when it fills that field.

- **Names disambiguate first** — `user` is ambiguous (id? email? name?); `user_email_address` self-documents. The model pattern-matches names before reading descriptions.
- **Say when omitting is safe** — for optional params, state what happens when omitted so the model knows it's safe to leave out, without enumerating internal branching it can't act on. "If omitted, a best-effort default window is applied based on your other filters" beats both silence and a per-mode arithmetic spec.
- **Avoid micro-detail the model can't use differently** — if the model would behave identically whether or not it knows the exact default formula, the formula is noise. Announce the concrete choice in the *result* (post-call), not the schema.
- **State boundaries between overlapping params** — "cannot be combined with X" at the field level prevents invalid combinations the model would otherwise try.

## Tool Definitions — Naming, Selection, Overlap

Tool definitions are read on *every* turn — they deserve the most care.

- **Names drive selection** — `get_data` is ambiguous; `search_customer_orders` is self-selecting. Generic verbs alone (`get`, `run`, `process`) hurt selection accuracy.
- **Overlap causes inconsistent selection** — if two tools do similar things, the model picks between them unpredictably. Either consolidate behind a mode parameter, or make each description state the boundary explicitly ("use X for structured queries; use Y for natural-language search").
- **Descriptions must cover when NOT to use the tool**, not just when to. Otherwise the model over-triggers.
- **Consolidate over proliferate** — a workflow that always needs three calls in sequence is a candidate for one higher-level tool: fewer decisions, less intermediate-result pollution, fewer wrong-tool chances. Trade-off: less composable for novel combinations.
- **Few-shot examples in descriptions earn their tokens when they disambiguate** (e.g. a list of valid codes the model would otherwise guess). Don't trim high-value disambiguation to save tokens.

## Stability & Caching

- **Don't inject volatile data into stable prefixes** — timestamps, request IDs, random values, or per-request data placed in a system prompt or tool definition invalidate the cache and force full reprocessing downstream. Flag volatile interpolation into otherwise-stable text.
- **Keep the tool set stable across turns** — dynamically adding/removing tools breaks caching and can make the model hallucinate tools it saw earlier. Prefer masking (keep the definition, mark it unavailable) over removal.

## How to Raise These Findings

These are almost always **DESIGN / context** findings, not correctness bugs — pose them as collaborative questions and let the author weigh the trade-off:

- *"This footer repeats what the tool description already says — could it live only in the description so we don't pay for it on every call?"*
- *"This hint fires on every multi-entity result but nudges toward a single-entity query — is that responsive to what the agent was doing, or can it go?"*
- *"This field description spells out the per-mode default formula — does the model act on that, or would 'defaults applied when omitted' plus the post-call scope line be enough?"*
- *"Is this error string reaching the model? If it's internal/terminal, leaking the variable name is fine — just confirming the routing."*

Quantify when you can: a redundant per-call footer is "N tokens × every call," not just "a bit verbose." That framing makes the cost concrete and the decision easy.