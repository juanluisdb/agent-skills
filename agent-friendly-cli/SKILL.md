---
name: agent-friendly-cli
description: "Guide for designing CLI tools that AI agents can use effectively. Use when creating a new CLI, adding commands to an existing one, or retrofitting a human-centric CLI for agent consumption — covers command shape, structured output, non-interactive modes, exit codes, and composability."
---

# Agent-Friendly CLI Design

Patterns for building CLIs that AI agents can drive effectively through shell access. The goal: turn any service, API, or system into composable shell commands an agent can discover and run without human intervention.

## Core Principles

1. **Composable primitives over monolithic workflows** — small focused commands (discover, read, resolve, download, inspect) that compose well beat one command that tries to do everything. Let the agent orchestrate.

2. **Structured output everywhere** — support `--json` on every command. Agents need to parse results, not read prose.

3. **Non-interactive by default** — no prompts, no confirmation dialogs, no spinners. If interactive mode exists for humans, provide flags to bypass it entirely.

4. **Semantic exit codes** — exit 0 means success (including empty results). Distinct non-zero codes for distinct failure categories. Agents decide what to do based on the code, not by parsing error text.

5. **Self-documenting** — `--help` is the API surface. Write it for a caller that only has the binary and a vague task. List subcommands, describe every flag, use literal names from the product domain.

6. **Predictable formats** — same input always produces same output structure. Schema changes are additive only. Never change or remove fields in minor versions.

7. **Actionable errors** — errors include a machine-readable type and a suggestion for what to do next. "Authentication expired — re-run `tool auth login`" beats "error: 401".

## Command Shape

### Noun-verb pattern

Use product nouns, then verbs. Consistency matters more than any specific convention — pick one style and hold it:

```bash
tool accounts list --json
tool accounts get <id> --json
tool channels resolve --name general --json
tool messages search "query" --limit 10 --json
tool logs download <build-url> --out ./logs --json
tool drafts create --body-file draft.json --json
```

### Discover, resolve, read, context

Design commands in this progression:

1. **Discover** — list broad containers (workspaces, accounts, projects, channels, queues)
2. **Resolve** — turn human input into stable IDs (names, URLs, slugs, permalinks → IDs)
3. **Read** — fetch a single object by stable ID
4. **Context** — retrieve surrounding data when useful (nearby messages, parent thread, audit log, surrounding log lines)

Don't force repeated searches when the agent already holds a stable ID.

### Raw escape hatch

Provide a `request` or `raw` command for API endpoints not yet covered by high-level commands. It should still use configured auth, base URL, JSON output, and error handling:

```bash
tool request get /v2/me --json
tool request post /v2/items --data '{"name": "test"}' --json
```

This is a repair hatch, not the primary interface.

## Output Design

### Stdout vs stderr

- **stdout**: data only — JSON objects, file paths, IDs
- **stderr**: progress, diagnostics, spinners, informational messages

This lets agents pipe and parse stdout cleanly.

### JSON output

```bash
# Human-friendly by default
tool pods get my-pod

# Structured when requested
tool pods get my-pod --json

# Field selection when the data model is wide
tool issues list --json number,title,url,state
```

JSON rules:
- Consistent envelope shape: `{"success": true, "data": {...}}` or equivalent
- Document both success and error shapes
- Redact tokens, cookies, secrets — agents echo output into context windows
- For file operations, return: path written, byte count, source identifier

### Quiet mode

```bash
tool run --quiet --json
```

Suppress all informational output — progress bars, tips, banners. When agent-facing flags like `--non-interactive` are set, reduce chattiness automatically.

### Pagination

Start shallow. Add explicit controls for breadth:

```bash
tool items list --limit 10 --json
tool items list --limit 50 --offset 40 --json
tool items list --cursor <token> --max-pages 3 --json
```

Always include pagination metadata in JSON output (`next_cursor`, `total_count`, `has_more`).

## Non-Interactive Execution

### The problem

Interactive prompts, confirmation dialogs, and guided wizards block agents. They wait for input that will never come.

### The fix

Add flags that bypass all interaction:

```bash
# Human mode — prompts, confirms, guides
tool quickstart

# Agent mode — all required values as flags, no prompts
tool quickstart --non-interactive \
  --source openapi.yaml \
  --target typescript \
  --name MySDK \
  --output ./out
```

Rules:
- Every value an interactive prompt would ask for must be passable as a flag
- When a required value is missing and can't be prompted for, **fail fast** with a clear error listing exactly what's needed
- Provide sensible defaults where possible
- Never hang waiting for stdin

### Doctor command

Provide a `doctor` or `status` command that reports environment health — auth state, configuration, connectivity, version. It must work even when auth is broken (report the problem, don't crash):

```bash
tool doctor --json
```

## Checklist

When designing or reviewing a CLI for agent use:

- [ ] Every command supports `--json` or equivalent structured output
- [ ] No command blocks on interactive prompts without a bypass flag
- [ ] Exit codes are semantic and documented
- [ ] `--help` is complete — lists subcommands, describes all flags
- [ ] Errors include machine-readable types and recovery suggestions
- [ ] Pagination has explicit `--limit` and cursor/offset support
- [ ] Data goes to stdout, noise goes to stderr
- [ ] A raw/request escape hatch exists for uncovered API endpoints
- [ ] Output structure is stable — changes are additive only
- [ ] A `doctor` or `status` command reports environment health
