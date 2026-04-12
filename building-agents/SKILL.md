---
name: building-agents
description: Reference for building AI agents — context engineering, tool design, and prompting principles. Use when designing, reviewing, or implementing agent systems, agent tools, prompt strategies, or context management logic.
---

# Building AI Agents

Reference knowledge for building agent systems. This is not a step-by-step guide — it explains the forces, trade-offs, and principles behind effective agent design so you can make good decisions in context.

For orchestration patterns, harness engineering, long-horizon execution, evaluation, and guardrails, see `references/patterns.md`.

---

## Context Engineering

Context engineering is the discipline of curating what information enters the model's context window at each step. It is the single most impactful lever in agent performance — more than model choice, more than prompt wording. A mediocre prompt with the right context outperforms a brilliant prompt with the wrong context.

### Why context matters

The context window is the agent's working memory. Everything the model knows about the current task, the tools available, prior actions, and their results lives here. Unlike a database, it is finite, expensive, and degrades with scale.

Key forces to understand:

- **Context rot**: Model performance degrades as the window fills, well before the technical token limit. The effective window is smaller than advertised. Accuracy on retrieval and reasoning tasks drops as token count grows — the model's attention gets spread thinner across more content.
- **Context pollution**: Irrelevant, redundant, or conflicting information actively harms performance. More context is not better context. Every token competes for attention with every other token.
- **Lost in the middle**: Models attend more strongly to the beginning and end of context. Information buried in the middle is more likely to be missed. This matters for where you place instructions vs. data.
- **Cache economics**: In production, prompt tokens that remain stable across calls can be cached. Changes to the prefix invalidate downstream cache. This has direct cost implications — cached tokens can be an order of magnitude cheaper than uncached ones. Stable prefixes (system prompt, tool definitions) that don't change between turns are key to cost-efficient agents.

### Strategies for managing context

These are not mutually exclusive — effective agents combine several:

**Write context externally**: Save information outside the window for later retrieval. Scratchpads, progress files, todo lists — the filesystem is unlimited persistent memory. When an agent writes a plan to a file and reads it back later, it sidesteps context limits entirely. This is especially important for long-running tasks where accumulated context would exceed the window.

**Select context just-in-time**: Don't pre-load everything. Maintain lightweight references (file paths, IDs, queries) and retrieve full content only when needed. This mirrors how humans work — you don't memorize every file, you know where to look. Progressive disclosure through exploration beats upfront context dumping.

**Compress context**: When the window is filling up, reduce what's there. A priority order: first, compact by replacing verbose content with pointers to external storage (reversible, no information loss). Then summarize older turns (lossy but retains key decisions). Keep recent interactions in raw form — they carry the model's "rhythm" and maintain output quality. Tool result clearing (dropping raw tool outputs already processed) is the lightest form of compression.

**Isolate context**: Split work across separate context windows. Sub-agents with focused tasks and clean windows avoid the pollution problem. Each sub-agent gets only the tools and instructions relevant to its job. The trade-off: you gain context cleanliness but lose shared understanding between agents. Information must be explicitly passed, and conflicting decisions across agents become possible.

### Principles

- **Preserve error traces.** Failed actions and stack traces are some of the most valuable context. They enable the model to update its beliefs and avoid repeating mistakes. Erasing failures removes the evidence the model needs to adapt. Resist the urge to clean up error history.
- **The filesystem is extended context.** For anything that exceeds window limits — large files, accumulated state, research notes — treat the filesystem as the primary store. Read from it on demand. Write to it proactively. The context window is for active reasoning, not for storage.
- **Stability enables caching.** Keep the structure of system prompts, tool definitions, and instruction blocks stable across turns. Avoid injecting timestamps, random IDs, or per-request data into prefix positions. Small changes to the beginning cascade into full reprocessing of everything after.
- **Recitation fights attention decay.** For long-running tasks, having the agent periodically restate its current goals (via a todo file, plan update, or progress summary) keeps objectives in the recent attention window. This counteracts the "lost in the middle" problem naturally.

---

## Tool Design

Tools are the agent's hands. A well-designed tool makes the agent more capable; a poorly designed one makes it confused, wasteful, or wrong. Tool design deserves as much care as prompt design — often more, because tool definitions are read by the model on every single turn.

### Tools are prompts

This is the most under-appreciated insight in agent development. Everything the model reads is context that shapes its behavior:

- **Tool names** guide which tool gets selected. A name like `get_data` is ambiguous; `search_customer_orders` is self-selecting.
- **Tool descriptions** are instructions. If the description doesn't explain when to use the tool, the model guesses. If it doesn't explain when NOT to use it, the model over-triggers.
- **Parameter names and descriptions** are micro-prompts. `user` is ambiguous — is it a username, user ID, email? `user_email_address` is unambiguous. In typed schemas (Pydantic, JSON Schema), field descriptions are prompts too. The `description` field on a Pydantic model attribute is read by the model and directly influences how it fills that parameter.
- **Tool outputs** are context that shapes next actions. Verbose outputs waste the window. Cryptic outputs (raw UUIDs, encoded blobs) force the model to guess at meaning. Outputs should contain what the agent needs to decide its next step — no more, no less.
- **Error messages** are instructions for recovery. `Error: 403` tells the model nothing. `Error: Permission denied — the API key does not have write access to this resource. Use a read-only operation or request elevated permissions.` tells it exactly what to try next.

### Design principles

**Consolidate over proliferate.** Fewer, higher-level tools outperform many granular ones. If a workflow always requires calling three endpoints in sequence, consider one tool that does all three. The model makes fewer decisions, wastes less context on intermediate results, and has fewer chances to pick the wrong tool. The trade-off: consolidated tools are less composable for novel combinations.

**Name for disambiguation.** When an agent has many tools, naming determines selection accuracy. Use consistent prefixes to group related tools (`customer_search`, `customer_update`, `customer_delete`). Avoid generic verbs alone (`get`, `run`, `process`). The agent reads the tool list and pattern-matches against names before reading descriptions.

**Return semantic content, not raw data.** Resolve internal IDs to human-readable names before returning. Include enough context for the agent to reason about the result without needing a follow-up call. But trim what's irrelevant — a 200-field API response where the agent needs 5 fields is context pollution.

**Control response size.** Implement pagination, filtering, and truncation with sensible defaults. When truncating, include a hint: "Showing first 20 of 347 results. Use the `offset` parameter or narrow the query to see more." This teaches the agent how to get what it needs rather than silently hiding information.

**Make errors actionable.** The model will try to recover from errors. Give it enough information to recover intelligently. Include what went wrong, why, and what to try instead. Opaque error codes or raw stack traces waste recovery attempts.

**Keep the tool set stable.** Dynamically adding and removing tools between turns breaks caching and can cause the model to hallucinate tools it saw earlier but that are no longer available. If you need conditional tools, prefer masking (keeping the definition present but indicating it's unavailable) over removal.

### When tools overlap

Overlapping tools are a common source of agent confusion. If `search_documents` and `query_knowledge_base` do similar things, the agent will inconsistently pick between them. The number of tools matters less than their distinctness. Some agents work well with 15+ tools when each has a clear, non-overlapping purpose. Others struggle with 5 tools that blur into each other. When overlap exists, either consolidate into one tool with a mode parameter, or make the descriptions explicitly state the boundary ("Use X for structured data queries. Use Y for natural language search over unstructured content.").

---

## Prompting for Agents

"Prompt" in agent systems means far more than the system message. It's every token the model reads: system instructions, tool definitions, tool outputs, error messages, schema descriptions, user messages, prior assistant turns, injected context. All of it competes for attention. All of it shapes behavior.

This section covers prompting considerations specific to agents. General prompting advice (be clear, use examples, provide structure) is assumed knowledge.

### System instructions

System prompts set the agent's identity, constraints, and behavioral defaults. They're read on every turn, so they should be stable (for caching) and concise (for attention).

**Find the right abstraction level.** Too rigid (hard-coded if-then rules for every scenario) makes the agent brittle — it fails on any case not explicitly covered. Too vague ("be helpful and smart") gives no useful guidance. The sweet spot: specific enough that you could verify compliance, general enough that the agent can adapt to novel situations. Teach principles and heuristics over exhaustive rules.

**Use existing knowledge artifacts.** Operating procedures, support scripts, policy documents, style guides — these already encode the decisions and edge cases your team has handled. Convert them into agent instructions rather than writing prompts from scratch. The model is good at following structured documentation.

**Template over duplicate.** When an agent handles multiple similar scenarios (different customer tiers, different markets, different product lines), use a single prompt template with variables rather than maintaining many nearly-identical prompts. This reduces maintenance burden and ensures consistency.

### Few-shot examples

Examples are powerful but carry risks in agentic contexts:

- **Imitation over reasoning.** The model may reproduce the surface pattern of examples rather than understanding the underlying principle. Uniform examples create brittle agents that fail on anything slightly different.
- **Introduce variation.** If you use examples, vary the format, phrasing, and complexity. This teaches the pattern rather than the specific instance.
- **Prefer showing over telling.** When the desired behavior is hard to describe (output format, tone, level of detail), one example communicates more than a paragraph of instructions.

### Agent-specific prompting patterns

**Scaling effort to complexity.** Not every query deserves the same investment. Embed heuristics that help the agent calibrate: a simple fact lookup shouldn't trigger multi-step research with sub-agents. Provide guidance on how to assess complexity and match effort accordingly.

**Start wide, then narrow.** For research or exploration tasks, agents tend toward overly specific queries that miss relevant results. Prompt for broad initial exploration followed by targeted deep dives. This mirrors how skilled humans research.

**Verification before completion.** Agents tend to declare victory early. Prompting for explicit verification steps — run the tests, check the output, validate against requirements — before marking work as done significantly improves reliability. The difference between a weak and strong agent is often not the implementation but whether it checked its own work.

**Interleaved reasoning.** When models support thinking or reasoning modes, use them strategically: heavier reasoning for planning (understanding the problem) and verification (catching mistakes), lighter for straightforward implementation. Not every step needs deep thought.

**Planning with external persistence.** For complex tasks, have the agent write a plan to a file rather than holding it in context. This makes the plan inspectable, editable, and persistent across context windows. It also keeps the plan in "recent attention" when re-read, rather than buried hundreds of turns back.
