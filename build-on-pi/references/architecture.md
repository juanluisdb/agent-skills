# Architecture

Use this reference when deciding which Pi package or runtime surface should own a change.

## Layered Model

- `pi-ai`
  Unified LLM layer: model registry lookups, provider abstraction, streaming, completions, tool-call schemas, reasoning levels, and auth-sensitive provider behavior.
- `pi-agent-core`
  Agent loop and transport layer: tool-calling loop, tool execution lifecycle, steering and follow-up behavior, and event stream semantics.
- `pi-coding-agent`
  Coding-agent runtime: built-in tools, session persistence, compaction, settings, resource loading, system prompt assembly, and extensions.
- `pi-tui`
  Terminal UI layer: interactive mode, widgets, dialogs, editor behavior, and terminal-native rendering.
- Product shells
  Pi CLI, RPC hosts, embedded apps, web UI consumers, Slack bots, and systems like OpenClaw.

## Package Choice Rules

- Choose `pi-ai` if you need provider portability without adopting Pi's agent/session model.
- Choose `pi-agent-core` if you need the loop but want to own tools, persistence, or UX yourself.
- Choose `pi-coding-agent` if you need Pi's opinions about coding-agent runtime, context, and extensibility.
- Add `pi-tui` only when terminal-native UI is part of the product or workflow.

## Runtime Modes

- Interactive mode
  Full TUI experience with editor, commands, widgets, and session navigation.
- Print/JSON mode
  Good for scripts, automation, deterministic wrappers, and structured event output.
- RPC mode
  Good for subprocess control and non-Node hosts.
- SDK mode
  Best for serious product integrations built directly on Pi sessions.

## Important Runtime Primitives

- `createAgentSession()`
  The main session factory for embedding Pi programmatically.
- `SessionManager`
  Persistence, open/continue/list behavior, and session file ownership.
- `DefaultResourceLoader`
  Discovery and reload of extensions, skills, prompts, themes, system prompt overrides, and context files.
- `ModelRegistry` and `AuthStorage`
  Model discovery and runtime auth material.
- `SettingsManager`
  Settings layering and overrides.

## Integration Rule Of Thumb

- Let Pi own model interaction, agent state, session behavior, and resource loading.
- Let the host app own user identity, business logic, policy, sandboxing, delivery semantics, and observability beyond Pi's native surface.
