---
name: create-skill
description: Create a new AI-agent skill interactively. Use when the user wants to create, scaffold, or build a new skill.
---

# Create a New Skill

Guide the user through creating a new skill for an AI agent. Follow these steps:

## Step 1: Gather Requirements

Ask the user (skip anything already provided via arguments or context):

1. **Skill name** — lowercase, hyphens only (e.g. `review-pr`, `run-tests`). Use `$ARGUMENTS` if provided.
2. **What should the skill do?** — one sentence is enough.
3. **Trigger phrasing** — gather or infer 2-3 realistic ways the need would show up in user language or context. Use this to sharpen discovery and boundaries; do not include an `Example Requests` section in the final skill unless it materially clarifies a confusing trigger.
4. **Expected output** — what should the agent produce or accomplish?
5. **Edge cases or constraints** — unusual inputs, failure cases, or important rules.
6. **Scope** — where to store it:
   - **Global** (standard location: `~/.agents/skills/<name>/`) — available in all projects
   - **Project** (standard location: `.agents/skills/<name>/`) — only this project, can be committed to version control
   - If the user specifies another location, use that instead of the standard paths above.

Before asking new questions, first extract what you can from the conversation history or current context. If the user already described the workflow, tools, format, or constraints, reuse that instead of asking them to repeat it.

## Step 2: Write the Skill

Create the directory and write `SKILL.md`.

### Choose the kind of skill

Decide what kind of skill you are creating before writing it:

- **Reference skill** — adds conventions, patterns, domain knowledge, or background guidance the agent should apply while doing other work.
- **Task or workflow skill** — gives step-by-step instructions for a specific action or repeatable process, often something the user may invoke directly.

Reference skills usually need concise guidance and supporting references. Task or workflow skills usually need clearer procedures, templates, and explicit guardrails.

### Frontmatter

```yaml
---
name: <skill-name>
description: <what it does and WHEN to use it>
---
```

- **`name`** — must match the directory name. Used as the skill identifier.
- **`description`** — drives skill discovery. The agent uses it to decide when to load the skill. Write in third person. Front-load the key trigger scenario and include keywords users would naturally say. Descriptions over 250 characters get truncated.
- Include both:
  - what the skill does
  - when to use it, based on realistic user phrasing or contexts
- Also make the boundaries clear. If helpful, mention cases where the skill should **not** be used so it does not trigger for adjacent but different tasks.
- Treat realistic user phrasing as authoring input for the `description`, not as default body content. Only keep example requests in the final `SKILL.md` when they materially improve clarity for the agent.
- The body should usually **not** repeat discovery text already captured in the `description`. Avoid sections like `Use This When` when they mostly restate the frontmatter. Keep post-load content focused on execution, constraints, inputs, workflow, and output.

If the user explicitly asks to prevent automatic invocation, add `disable-model-invocation: true`.

### Deciding the level of prescriptiveness

This is the most important decision. Match the level of freedom to the task's fragility:

**High freedom** — multiple valid approaches, context-dependent decisions. Give direction, not steps.

Use for: code reviews, research, analysis, creative tasks.

```markdown
When reviewing code, check for:
1. Potential bugs or edge cases
2. Readability and maintainability
3. Adherence to project conventions
```

**Medium freedom** — a preferred pattern exists but variation is acceptable. Provide templates or pseudocode that can be adapted.

Use for: report generation, structured output, configurable workflows.

```markdown
Use this report structure, adapting sections as needed:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Low freedom** — operations are fragile, consistency is critical, a specific sequence must be followed. Provide exact instructions.

Use for: deployments, database migrations, anything with side effects where deviation breaks things.

```markdown
Run exactly this sequence:
1. `python scripts/migrate.py --verify --backup`
2. Wait for verification output
3. Only proceed if "OK" is printed
```

**The analogy**: think of an AI agent navigating a path. On a narrow bridge with cliffs, provide exact guardrails (low freedom). In an open field with no hazards, give general direction and trust the agent to find the route (high freedom).

### Writing effective content

**The agent is already smart.** Only include what the agent doesn't already know. Challenge each line: "Does the agent need this explanation, or does it already know this?" Don't explain what PDFs are, how libraries work, or general programming concepts. Do explain your specific patterns, conventions, constraints, and non-obvious rules.

**Do not duplicate the frontmatter.** If the `description` already explains what the skill does and when it should trigger, do not restate that in the body unless it adds a non-obvious execution boundary or prevents a likely mistake after the skill is loaded.

**Be concrete enough to verify.** "Use 2-space indentation" beats "format code properly." "Run `npm test` before committing" beats "test your changes." If you couldn't check whether the agent followed the instruction, it's too vague.

**Structure for scanning.** Use markdown headers and bullets. Organized sections are easier to follow than dense paragraphs. Agents read structure the same way humans do.

### Choose supporting files based on repeated pain

Only add supporting files when they remove repeated work or reduce mistakes:

- **`scripts/`** — use when the same code or command sequence would otherwise be rewritten repeatedly, or when execution should be deterministic.
- **`references/`** — use for detailed documentation, schemas, policies, or variant-specific guidance that should be loaded only when needed.
- **`assets/`** — use for templates, sample files, starter projects, images, or other resources the agent should use in its output rather than read into context.
- **`examples/`** — use when the desired style, format, or quality bar is easier to show than explain.

Add these because they solve a repeated problem, not because every skill needs every folder.

### Patterns to use when appropriate

**Templates** — when output needs a specific format. Match strictness to the task:
- Strict ("ALWAYS use this exact structure") for data contracts, API responses
- Flexible ("here is a sensible default, adapt as needed") for reports, documentation

**Examples** — when output quality depends on seeing the desired style. Input/output pairs communicate style better than descriptions. Use for commit messages, naming conventions, writing tone.

**Workflows with checklists** — when the task has multiple sequential steps. A checklist the agent can track progress against prevents skipping critical steps. Especially useful for multi-step processes with validation between steps.

**Supporting files** — when `SKILL.md` would exceed ~500 lines. Keep `SKILL.md` as an overview and table of contents. Move detailed reference material to separate files and link them. Many agents load supporting files on-demand, so large reference docs do not cost context until needed. Keep references one level deep from `SKILL.md`.

## Step 3: Confirm and Test

After creating the skill:
1. Show the user the generated `SKILL.md` content
2. Explain how to use it: direct invocation if the platform supports it (for example `/skill-name`), or describe when the skill should auto-trigger
3. Suggest a quick test invocation

## Reference: Skill Directory Structure

```text
skill-name/
├── SKILL.md           # Required — main instructions
├── references/        # Optional — detailed docs, loaded on demand
├── examples/          # Optional — example outputs
├── scripts/           # Optional — helper scripts the agent can execute
└── assets/            # Optional — templates and output resources
```

Supporting files are often loaded on demand. Reference them from `SKILL.md` so the agent knows what they contain and when to load them.
