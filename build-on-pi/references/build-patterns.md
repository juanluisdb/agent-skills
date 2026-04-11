# Build Patterns

Use this reference when the task is not just "understand Pi" but "ship something on top of Pi."

## Embedded Pi Service

Use when:
- the product already has its own identity, routing, channels, or permissions
- you need Pi as the runtime kernel inside a larger system

Typical shape:
- create sessions with `createAgentSession()`
- wire `SessionManager`, `ModelRegistry`, `AuthStorage`, `SettingsManager`
- use a resource loader for extensions, skills, prompts, and system prompt overrides
- keep policy and delivery in the host app

## Repo-Local Pi Customization

Use when:
- the goal is to make Pi effective inside one codebase or one team workflow

Typical shape:
- `AGENTS.md`
- project `.pi/` config
- a few focused skills
- small local extensions when the runtime needs extra behavior

## Extension-First Feature

Use when:
- you need new tools, commands, widgets, dialogs, or dynamic context
- you want to preserve Pi's native workflows instead of wrapping around them

Typical shape:
- add an extension
- register tools or commands
- use event hooks and UI helpers
- persist extension state through session entries if needed

## Thin Wrapper Or Automation

Use when:
- the host just needs structured control or output
- deep embedding is overkill

Typical shape:
- print/JSON mode for scripts and automation
- RPC mode for structured host control

## OpenClaw-Style Integration

Useful mental model:
- Pi provides the agent runtime, session machinery, and extensibility substrate.
- The host provides identity, channel semantics, prompt shaping, policy, auth rotation, sandbox boundaries, and higher-level orchestration.

## Anti-Pattern Checks

- If the host is just parsing CLI text, ask whether SDK embedding or RPC would be cleaner.
- If a workflow could live in a skill or extension, avoid forking Pi too early.
- If every operation is going through `bash`, ask whether you are bypassing Pi's stronger primitives.
