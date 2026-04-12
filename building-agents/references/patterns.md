# Agent Patterns: Orchestration, Harness, Long-Horizon, Evaluation, Guardrails

Supplementary reference for `building-agents`. Read this when working on agent orchestration, harness infrastructure, long-running execution, evaluation strategy, or safety.

---

## Orchestration

Orchestration is how you structure the relationship between models, tools, and execution flow. The choice is not "single agent vs multi-agent" — it's a spectrum of patterns, each with trade-offs.

### Single-agent patterns

A single model in a loop, calling tools until an exit condition is met. This is the simplest pattern and should be the default starting point. A single agent with well-designed tools handles more than people expect.

**When it works well**: The task has a manageable number of distinct tools, instructions fit in one coherent prompt, and the workflow doesn't need parallel exploration of independent paths.

**Prompt templates over prompt proliferation**: When a single agent handles related but varying scenarios, use one base prompt with variables (customer tier, product type, region) rather than maintaining separate prompts. This scales better and ensures consistency.

**When to split**: Consider splitting when the prompt accumulates too many conditionals, when tools overlap and confuse selection, or when the context window fills with information irrelevant to most steps. Splitting is a response to observed problems, not a preemptive design choice.

### Multi-agent patterns

**Manager pattern (agents-as-tools)**: A central agent delegates to specialist agents via tool calls. The manager maintains conversation context and synthesizes results. Specialists run in isolated contexts with focused tools. Best when you want one agent to own the user interaction and others to handle specific capabilities.

**Decentralized pattern (handoffs)**: Agents transfer control to peers. No central coordinator — each agent decides when to pass to another. Works well for routing scenarios (triage agent identifies intent, hands to specialist) but loses central oversight.

**Agent-as-tool**: Treat sub-agents as deterministic functions — call with structured input, get structured output. This flattens complexity and keeps the calling agent's context clean. The sub-agent's full reasoning trace stays isolated; only the result flows back.

### Trade-offs to weigh

- Multi-agent buys you context isolation and parallelism. It costs coordination overhead, token multiplication, and the inability for agents to see each other's decisions. Independent actions can lead to conflicting outputs.
- Parallelism helps most when subtasks are truly independent (different research questions, different data sources). It helps least when tasks have sequential dependencies or need shared understanding.
- Agents communicating with each other to resolve conflicts remains unreliable. If coherence across outputs matters, prefer a single agent or a manager that synthesizes.
- The right amount of structure sits between chaos (flat, uncoordinated agents duplicating work) and rigidity (over-specified graphs that break on unexpected inputs). Hierarchical patterns with clear role separation tend to scale better than flat peer networks.

---

## Harness Engineering

The harness is everything around the model: the code that calls the API, manages the loop, handles tools, processes context, and implements lifecycle logic. Agent quality depends as much on harness design as on the model or prompt.

### Core components

**The agent loop**: A while-loop where the model is called, tool calls are executed, results are appended, and the model is called again — until an exit condition (final output, max turns, error). This loop is universal. What the model does inside it is learned behavior, not hardcoded.

**Filesystem abstraction**: Durable storage for state, context offloading, and multi-session continuity. Agents that can read and write files gain unlimited persistent memory. The filesystem is also the natural collaboration surface for multi-agent systems.

**Code execution environment**: Giving agents the ability to run code (shell commands, scripts) makes them dramatically more capable. It turns them from pure text generators into actors that can verify their own work by running tests, inspect environments, and manipulate data directly.

**Sandboxes**: Isolated execution environments providing security boundaries. Important when agents have shell or browser access. Allow-listed commands, network isolation, and resource limits prevent agents from causing unintended damage.

### Harness patterns

**Build-verify loops**: Agents naturally skip verification. Adding a pre-completion check ("before responding, run the tests / check the output / validate against the spec") dramatically improves output quality. This can be implemented as middleware that intercepts completion attempts and forces a verification step.

**Context injection at startup**: Agents struggle with environmental discovery. Injecting directory structure, available tooling, and project conventions at the start of each session saves multiple rounds of exploration. This is the equivalent of onboarding a new team member.

**Loop detection**: Track repeated actions (editing the same file many times, retrying the same failing command). After N repetitions, inject a prompt suggesting the agent reconsider its approach. This prevents "doom loops" where the agent applies the same failing strategy indefinitely.

**Session startup routines**: For multi-session work, each new session should follow a consistent startup: read progress files, check git history, run smoke tests, then pick up the next task. This gives the agent state awareness despite starting with a clean context window.

### The "build to delete" principle

Harness complexity that compensates for model limitations today may become unnecessary as models improve. Design harness components to be removable. Test periodically whether each piece still carries its weight by disabling it and measuring impact. Over-engineering the harness is as harmful as under-engineering it.

---

## Long-Horizon Execution

Long-running tasks (multi-hour, multi-session, multi-window) are where agent systems most commonly fail. The core challenge: maintaining coherence and progress when context is finite and sessions are discrete.

### Failure modes

- **Premature completion**: The agent declares the task done when it's partially finished. Often caused by lack of a comprehensive task specification to check against.
- **Goal drift**: After summarization or context reset, the agent subtly shifts direction. The original intent was in the context that got compressed away.
- **Context anxiety**: As the window fills, agents rush to wrap up rather than continuing methodically. They sense the approaching limit and try to conclude prematurely.
- **Lost state between sessions**: A new session starts with no memory of prior work. Without structured handoff artifacts, the agent must rediscover state from scratch.

### Mitigation strategies

**Structured task tracking**: Maintain a feature list or task file in a structured format (JSON works well — models are less likely to corrupt it). Initialize all items as incomplete. The agent checks this file to know what's done and what's next. Protect the file from casual modification — the agent should only update status fields, not redefine tasks.

**Progress artifacts**: Three complementary records: a narrative progress log (what was done, decisions made, open questions), git history with descriptive commits (what changed), and a setup script that recreates the working environment. Together these let a new session reconstruct full context quickly.

**Compaction over reset**: When approaching context limits, summarize and continue rather than starting from zero. But when summarization quality is poor (goal drift, lost details), a full reset with filesystem-based state recovery can be more reliable. Models that can rediscover state from files and git history often recover better than models working from lossy summaries.

**One unit of work per session**: For multi-session projects, scope each session to one feature, one fix, or one well-defined chunk. Complete it, commit, update progress, and stop. This prevents half-finished work from spanning context boundaries.

**Verification tools**: As autonomy duration grows, the agent needs ways to check correctness without human feedback. Browser automation for UI testing, test suites for code, linters for style — these give the agent feedback loops that substitute for human review.

---

## Evaluation

Agent evaluation is harder than LLM evaluation because agents take sequences of actions, and the same goal can be achieved through different valid paths. Focus on outcomes over process.

### Practical approach

**Start small and iterate.** Begin with a small set of representative tasks that reflect real usage. Early development has abundant low-hanging fruit — prompt tweaks can cause large jumps in success rate. Don't delay evaluation waiting for large test sets.

**Evaluate end-state, not trajectory.** For agents that modify state (code, files, databases), check the final result rather than validating every intermediate step. Agents find alternative valid paths. Score against "does the output meet the spec" rather than "did it follow the expected sequence."

**LLM-as-judge for subjective quality.** A separate model call evaluating output against a rubric (factual accuracy, completeness, source quality, task efficiency) is often the most consistent approach. Output scores plus pass-fail. Most reliable when test cases have clear expected answers.

**Stress-test context management.** Artificially trigger compaction or summarization more aggressively than production defaults. This amplifies signal about whether your compression strategies preserve essential information. Needle-in-the-haystack tests (embed a fact early, force compression, require retrieval later) catch recoverability failures.

**Track the right metrics.** Accuracy is table stakes. Also track: tool call count (efficiency), token consumption (cost), error recovery rate (resilience), time to completion (latency). A correct answer that takes 50 tool calls and burns through the context window is a different problem than an incorrect answer.

### Iteration methodology

Trace analysis is powerful: collect failed runs, analyze patterns across failures, propose targeted harness or prompt changes, verify on held-out examples. This mirrors machine learning's boosting approach — focus each iteration on what the previous iteration got wrong. But verify that fixes don't regress passing cases.

---

## Guardrails

Guardrails manage the risks that come with giving models autonomy: data leaks, harmful outputs, unintended actions, runaway costs.

### Layered defense

No single guardrail is sufficient. Combine:

- **Input validation**: Classify incoming messages for relevance (is this in scope?), safety (is this a jailbreak attempt?), and content policy compliance. Rules-based filters (regex, blocklists, length limits) catch known patterns cheaply. LLM-based classifiers catch novel ones.
- **Tool risk ratings**: Assess each tool by impact — read-only vs. write, reversible vs. permanent, internal vs. external-facing. Use these ratings to trigger additional checks before high-risk tool execution. A search is low risk; deleting a database record is high risk.
- **Output validation**: Check responses for PII exposure, brand alignment, factual grounding, and policy compliance before delivering to the user.
- **Resource limits**: Cap maximum turns, token spend, and execution time per task. Agents can enter infinite loops or pursue increasingly expensive strategies without realizing the cost.

### Human intervention

Plan for it from the start. Two primary triggers:

- **Failure thresholds**: After N failed attempts at the same step, escalate rather than continuing to retry. The agent is likely stuck in a way that more attempts won't solve.
- **High-risk actions**: Irreversible or high-stakes operations (financial transactions, data deletion, external communications) should require confirmation until confidence in the agent's reliability is established in that specific domain.

The goal is not permanent human oversight but a graduated trust model: start with tight guardrails, loosen as you build evidence of reliability through evaluation and production monitoring.
