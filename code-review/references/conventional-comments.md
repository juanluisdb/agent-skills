# Conventional Comments

Load this reference only when turning agreed findings into review comments for GitHub, GitLab, or another review surface.

## Labels

- `issue:` for concrete problems
- `suggestion:` for specific improvements
- `question:` for clarification
- `thought:` for non-blocking design commentary
- `nitpick:` for trivial style preferences
- `note:` for neutral context

Optional decorations can make intent clearer:

- `(blocking)`
- `(non-blocking)`
- `(security)`
- `(test)`
- `(if-minor)`

## Comment Pattern

Keep comments short and actionable:

1. label the concern
2. state the issue clearly
3. explain why it matters if the reason is not obvious
4. offer a concrete fix or alternative

## Mapping

- `CRITICAL` or `HIGH` usually maps to `issue (blocking):`
- `MEDIUM` often maps to `issue:` or `suggestion:`
- `LOW` often maps to `suggestion (non-blocking):` or `nitpick:`
- `SMELL` often maps to `issue (non-blocking):`
- `SUGGESTION` often maps to `thought:` or `suggestion (non-blocking):`
