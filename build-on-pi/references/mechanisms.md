# Mechanisms

Use this reference when deciding whether a change belongs in a skill, extension, tool, prompt, or host application.

## Use A Skill When

- The agent needs procedural knowledge, domain guidance, or instructions for using existing tools well.
- The capability is mostly knowledge, conventions, playbooks, or decision rules.
- You want progressive disclosure: the skill should be advertised briefly, then read in full only when needed.

## Use An Extension When

- You need runtime hooks, session interaction, custom tools, slash commands, shortcuts, or TUI/UI behavior.
- The agent or operator needs new capabilities inside the Pi runtime itself.
- You need to register a provider, inject context dynamically, or react to lifecycle events.

Important extension surface from current docs includes:
- `registerTool`
- `registerCommand`
- event subscriptions via `on(...)`
- `exec(...)`
- UI helpers like dialogs and widgets
- actions such as sending messages or switching models/tools

## Use A Tool When

- The LLM should call a structured capability during the loop.
- The action has clear machine-readable parameters and a meaningful result shape.
- The capability benefits from schema validation, output truncation, and UI rendering hooks.

Prefer structured tools over free-form shell where possible.

## Use A Prompt Template When

- You want a reusable operator-facing macro or prompt expansion.
- The capability is not a durable part of runtime behavior.

## Use The Host App When

- The concern is business logic, product identity, tenancy, policy, delivery, sandboxing, or orchestration outside the Pi runtime.
- The concern spans channels, users, or workflows that should not be encoded as Pi session-local behavior.

## Lightweight-First Rule

Prefer this order unless there is a strong reason not to:
1. `AGENTS.md` or config files
2. skill
3. prompt template
4. extension
5. host-level integration
6. core package change
