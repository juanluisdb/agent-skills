---
name: build-on-pi
description: "Guides coding agents building on top of Pi and pi-mono: choosing between pi-ai, pi-agent-core, pi-coding-agent, RPC, TUI, skills, extensions, and resource loading. Use when embedding Pi, writing Pi extensions or skills, or designing integrations around Pi. Not for generic agent architecture unrelated to Pi."
---

# Build On Pi

Use this skill to make sound implementation choices when building with Pi. Treat Pi as a minimal agent runtime with strong primitives, not as a batteries-included framework that dictates one product shape.

## Pi Mental Model

- Pi is layered. The usual stack is `pi-ai` -> `pi-agent-core` -> `pi-coding-agent` -> product shell such as TUI, RPC host, web UI, or embedded app.
- Pi is intentionally small at the core. Many workflows that other systems bake in are meant to live in files, skills, extensions, or host applications.
- Pi is built around observability and agent malleability. Prefer designs where tools, session state, prompts, and operator interventions stay visible and inspectable.
- Pi is contrarian on purpose. Do not add abstractions just because they are common elsewhere; first check whether Pi already wants that concern handled by a lighter mechanism.

## Choose The Right Layer

- Use `pi-ai` for multi-provider model access, streaming, tool-call schemas, and model portability without adopting Pi's agent runtime.
- Use `pi-agent-core` when you want Pi's agent loop and event model, but your product owns tools, persistence, and UX.
- Use `pi-coding-agent` when you want the coding-agent runtime: sessions, compaction, built-in tools, resource loading, settings, and extensibility.
- Use `pi-tui` when you are building a terminal-native experience, custom dialogs/widgets, or richer operator workflows.
- Use RPC mode when a non-Node host or subprocess controller needs structured control over a Pi session.
- Prefer SDK embedding over shelling out to the CLI when building a serious product integration.

Load [architecture.md](./references/architecture.md) if you need the deeper package and runtime model.

## Core Concepts The Agent Must Preserve

- Sessions are tree-structured, not just linear chats. Do not flatten that model away without a reason.
- Context is assembled deliberately through `AGENTS.md`, system prompt files, skills, prompt templates, compaction, and extension hooks.
- Built-in tools are constrained on purpose. Prefer structured tools over `bash` when possible.
- Resource loading is a first-class integration seam. Extensions, skills, prompts, and themes are meant to be discovered and reloaded.
- Models, providers, auth, and settings are distinct concerns. Avoid hard-wiring them together in app-specific code unless necessary.

Load [sessions-context.md](./references/sessions-context.md) when the task touches session design, prompt assembly, or context management.

## Skills vs Extensions vs Tools vs Prompts

- Use a skill for domain knowledge, repo conventions, procedural know-how, or guidance on using existing CLIs and workflows.
- Use an extension for runtime behavior: custom tools, slash commands, shortcuts, UI widgets, dynamic context injection, or provider registration.
- Use a tool when the LLM should invoke a structured capability during the loop.
- Use a prompt template for reusable operator-facing prompt expansions, not for durable system behavior.
- Start with the lightest mechanism that works. Prefer `AGENTS.md` or a skill before writing an extension; prefer an extension before forking core packages.

Load [mechanisms.md](./references/mechanisms.md) for more detailed decision rules.

## Building On Pi: Decision Guide

- If the task is "add product logic around Pi", keep product concerns in the host app and let Pi own agent runtime concerns.
- If the task is "teach Pi how to work in this repo or domain", prefer `AGENTS.md`, skills, or prompts before code.
- If the task is "add an agent capability with UI or runtime hooks", write an extension.
- If the task is "integrate Pi into another app", start from `createAgentSession()` and explicitly wire `SessionManager`, `ModelRegistry`, `AuthStorage`, `SettingsManager`, and a resource loader when needed.
- If the task is "support a new workflow that another ecosystem would call MCP/subagents/plan mode", first ask whether Pi wants this as a skill, extension, CLI wrapper, or host-level orchestration.

## Common Build Patterns

- Embedded app: SDK-based session creation plus custom tools, host identity/policy, and explicit session storage.
- Repo-local distribution: `AGENTS.md`, `.pi/` config, project skills, and a few focused extensions.
- Extension-first enhancement: add tools, commands, UI, or dynamic context without changing core packages.
- OpenClaw-style host integration: Pi as the runtime kernel, host app owning delivery semantics, channel identity, policy, and orchestration.
- Thin automation wrapper: print/JSON or RPC mode when the host only needs structured interaction and not deep embedding.

Load [build-patterns.md](./references/build-patterns.md) if you need examples and tradeoffs.

## Guardrails And Anti-Patterns

- Do not treat community writeups as canonical API guarantees.
- Do not turn every capability into a tool call if a skill or file-based convention would be simpler.
- Do not reach for `bash` first when `read`, `edit`, `grep`, `find`, or `ls` would be safer and more legible.
- Do not erase Pi's session tree, compaction, or steering model unless the host product truly cannot expose them.
- Do not force Pi into another framework's mental model without checking Pi's native seams first.
- Do not assume Pi's anti-MCP, anti-plan-mode, or anti-subagent philosophy means those workflows are impossible. It usually means Pi expects them to be built outside the minimal core.

## Source Hierarchy And Trust Rules

- Prefer first-party docs, the `pi-mono` source, and official API references when making implementation claims.
- Treat `pi.dev` as product-level positioning and entry-point guidance.
- Treat community posts and examples as useful patterns, not guaranteed contracts.
- Treat `pi-book` as a high-signal architecture map for `pi-mono v0.66.0`, not as canonical API docs.
- When sources disagree, follow the most primary and most implementation-near source.

Load [sources.md](./references/sources.md) if you need the current source map and caveats.

## Implementation Checklist

- Identify which Pi layer should own the work before writing code.
- Decide whether the behavior belongs in the host app, `AGENTS.md`, a skill, a prompt, an extension, or a core package change.
- Preserve Pi's session and context model unless the user explicitly wants a different product abstraction.
- Prefer structured built-in tools and workspace-scoped execution boundaries.
- Check source quality before relying on a claim, especially for fast-moving APIs or ecosystem examples.
- If the task touches extension APIs, sessions, or embedding, load the relevant reference file before implementation.
