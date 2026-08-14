# Conventional Comments Reference

Format for MR review comments. Load this when drafting comments for posting.

## Labels

| Label | When to use |
|---|---|
| `suggestion:` | Propose a specific improvement |
| `issue:` | Highlight a concrete problem |
| `question:` | Seek clarification or context |
| `thought:` | Non-blocking idea for consideration |
| `nitpick:` | Trivial preference, style-only |
| `todo:` | Small necessary change |
| `chore:` | Process or housekeeping task |
| `note:` | FYI, always non-blocking |

## Decorations (optional, in parentheses after label)

| Decoration | Meaning |
|---|---|
| `(non-blocking)` | Should not prevent merge |
| `(blocking)` | Must resolve before merge |
| `(if-minor)` | Resolve only if the fix is trivial |
| `(security)` | Security-related concern |
| `(test)` | Test-related concern |

## Priority to Label Mapping

| Finding priority | Conventional Comment label |
|---|---|
| CRITICAL | `issue (blocking):` |
| HIGH | `issue (blocking):` |
| MEDIUM | `issue:` or `suggestion:` |
| LOW | `nitpick:` or `suggestion (non-blocking):` |
| SMELL | `issue (non-blocking):` — note that full context may be needed |

A finding without a "Proposed fix" maps to `issue:` or `question:` (no `suggestion:` partner needed). Don't invent a fix to fill the form.

## Comment Structure

Each comment should:

1. Start with the label and optional decoration
2. State the concern clearly in 1-2 sentences
3. Include a brief "why" when the reason isn't obvious from the code
4. Include a **concrete suggestion** *only when the right fix is clear*. When it isn't, a flag-only comment (`issue:` or `question:` with reasoning) is valid and often better than guessing.

**Example — fix is clear, propose it:**

```
suggestion (non-blocking): Consider using `StrEnum` instead of `Literal["active", "inactive"]` here.
This centralizes the valid states, makes them greppable, and avoids silent drift
if new states are added in only some of the places that reference this type.
```

**Example — concrete bug, fix is clear:**

```
issue (blocking): This `except Exception` swallows `KeyError` from the config lookup,
which would silently return `None` instead of surfacing a missing config key.
Catch `requests.RequestException` specifically, and let config errors propagate.
```

**Example — flag-only, no proposed fix:**

```
issue: The retry loop here can re-issue the same write after a partial DB failure,
but the calling path doesn't appear to be idempotent. I couldn't tell from the diff
whether the upstream caller dedupes — worth confirming before this lands.
```