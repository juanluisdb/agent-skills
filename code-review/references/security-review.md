# Security Review

Load this reference when the change crosses trust boundaries, touches authentication or authorization, handles secrets, processes external input, or otherwise deserves a stronger security lens.

This is review guidance, not a separate full security-audit workflow.

## Key Questions

- What input is attacker-controlled, indirectly controlled, or easier to influence than the code assumes?
- Where does untrusted data cross into templates, shell commands, file paths, queries, URLs, deserializers, or privileged operations?
- Are authentication and authorization both enforced, or is the code only checking identity?
- Does the change widen permissions, expose new data, or make sensitive actions easier to trigger?
- Are secrets, tokens, cookies, credentials, or user-linked data logged, cached, or returned too broadly?
- Do external requests allow SSRF-like behavior, unsafe redirects, or overly flexible destinations?
- Are defaults secure, or does omitted configuration quietly weaken protection?

## Common Findings

- missing or misplaced authz checks
- trusting client-provided identifiers, roles, or ownership claims
- injection risks in queries, commands, templates, and path handling
- unsafe deserialization or dynamic evaluation
- overbroad CORS, cookie, session, or token behavior
- sensitive data leaking through logs, errors, analytics, or debug output
- permission or scope changes without matching tests and migration thought

## Review Style

- Focus on realistic abuse paths, not theoretical perfection.
- Treat internet-facing, multi-tenant, and admin-path changes as higher risk.
- When a security concern is plausible but incomplete, surface the uncertainty instead of overstating it.
