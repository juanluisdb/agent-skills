# Security

Generic by design: no library, framework, or compliance-standard lock-in. Concrete tools are named as examples of a pattern, not as requirements.

## When security is in scope

Any of these patterns calls for a security pass, even when security is not mentioned anywhere in the description:

- New or modified auth, middleware, policy, or guard code
- A new public route, public API, or exported RPC procedure
- A new outbound HTTP call to a user-influenced URL
- A new deserialization site, or a schema migration
- Anything under a `crypto`, `auth`, `session`, or `permission` path
- Removing a guard, a validation, or a feature-flag check
- Widening a permission, role, scope, or CORS origin
- A new PII field on a model, or a new log call near a PII field
- A new file upload or download path
- A new HTML-injection sink, `target="_blank"`, or `postMessage` handler

If no trust boundary is crossed and none of the above applies, security thinking can be light. Say so rather than performing it.

## Threat model

Decide what you are defending against before deciding how. The threat model bounds everything below. "Defending against everything" is a non-answer; "defending against a tenant exfiltrating another tenant's data" produces concrete decisions.

- **Who is the attacker?** An anonymous internet user, an authenticated user of the system, an authenticated user of a different tenant, a malicious admin, a compromised dependency, an insider with database access.
- **What are they after?** PII, money, account takeover, control of the host, denial of service, information disclosure, lateral movement.
- **Which trust boundary is crossed?** Untrusted to trusted is where most vulnerabilities live, so identify it explicitly.

## Data classification

- **PII.** Email, phone, name, address, IP, date of birth, location, device fingerprint. Encryption at rest, redaction in logs, and access logging are planned with the data, not after it.
- **Secrets.** Tokens, API keys, signing keys, encryption keys. Each needs a storage location, an access path, and a rotation story. A secret with no path to rotate leaves the system with no path to recover from disclosure.
- **Financial or regulated data.** Card numbers, bank accounts, health information bring compliance requirements in at design time, not at audit time.
- **Persisted versus ephemeral.** Persistence multiplies the surface: backups, logs, replicas, analytics pipelines are the same surface as the primary store.
- **Collect only what is needed.** Everything else is liability without value. Deletion or anonymization runs on a schedule, an audit entry precedes deletion, and the right-to-erasure path is exercised by a test rather than documented.

## Authentication versus authorization

Identity and permission are different concerns, and conflating them is the most common serious bug in this area.

- **State the rule as a sentence:** *"any authenticated user can read their own X; only org admins can write X for users in their org."* A rule that cannot be stated has not been decided.
- **The check lives at the route *and* at the resource.** Route-level is necessary and not sufficient. Nearly every insecure-direct-object-reference bug is a route-protected endpoint missing the ownership predicate.
- **If the user supplies the resource ID, the server verifies ownership against the session,** not against the request.
- **Permission widening deserves explicit attention.** A new role, an expanded scope, a reordered middleware, a new public surface: these are the highest-blast-radius changes in the system.

## Multi-tenancy isolation

- **Tenant comes from the session or token, never from the request body or URL** unless cross-checked against the session.
- **Every query touching tenant-scoped data carries a tenant filter.** Plan it with the query.
- **Caches key on tenant.** In-memory, Redis, or CDN: a tenant-unaware cache key is a silent cross-tenant leak.
- **Background jobs carry tenant context explicitly,** never from a global or thread-local that may not be reset between jobs.
- **Tests cover two tenants.** One tenant's test passing says nothing about isolation; a cross-tenant assertion is what catches the bug.

## The validation boundary

Untrusted data enters from more places than the obvious one. The boundaries worth enumerating:

HTTP body, query, headers, and cookies. File uploads. Message queue and event-bus payloads. Third-party API responses. Database reads of data written by untrusted sources. Deserialized blobs from any source. IPC and RPC channels. Environment variables and config files. Browser URL, hash, history state, and `postMessage` events. Client-side storage read back by the same application.

- **Validate at the boundary, not deep in the logic.** Scattered validation means no line can be read as trusted or untrusted.
- **The validated type replaces the raw type downstream.** If validation returns a domain value and the next call still takes the raw one, the validation was theatre.
- **Allowlist over denylist** for closed sets: URL schemes, file types, sort columns, enum values, redirect targets. A denylist misses the case the attacker found.
- **Canonicalize before validating.** Normalize Unicode, URL encoding, path separators, and case *before* the check, otherwise an equivalent representation slips past.
- **Decide what rejection produces:** error code, error shape, log entry, alerting threshold.

## Injection, the full surface

Untrusted data interpolated into any of these channels is unsafe unless the channel's own safe API is used.

- **SQL and NoSQL:** parameterized queries or prepared statements only. String concatenation is unsafe regardless of "internal trust" claims.
- **Command and shell:** argv-form spawn, never shell concatenation. Where a shell is unavoidable, escape with a vetted library.
- **Paths and traversal:** resolve, then verify the result is under the expected root. Reject `..`, absolute paths, and symlinks that escape.
- **Templates:** server-rendered templates, log format strings, and LLM prompt templates are all injection surfaces.
- **LDAP, XPath, and regex injection:** less common, same rule. Parameterize or escape.
- **Open redirect:** `Location` headers, browser location assignments, and client-side router pushes taking an untrusted URL need a host and scheme allowlist.
- **Header injection:** CRLF in a user-controlled value reaching a response header.
- **Browser sinks:** raw HTML injection, `target="_blank"` without `rel="noopener"`, and a `postMessage` handler that does not check the origin.

## Sessions, tokens, and identity material

- **Token storage is a trade-off to state.** A cookie with `HttpOnly` and `SameSite` versus JS-accessible storage. A JS-readable token is exfiltratable by any XSS, so if the threat model admits XSS it is game over.
- **Lifetime and revocation.** Short-lived access tokens with refresh, or a session table that can revoke. A stateless token with no revocation path is unsafe for anything sensitive.
- **No tokens in URLs.** They leak through referrer headers, logs, and browser history.
- **Constant-time comparison** for tokens, HMACs, and signatures. An ordinary equality check is a timing oracle for byte-by-byte recovery.

## Secrets and credentials

- **Never hardcoded, never committed.** Watch `.env` files, sample env files, CI variables drifting in, and "dev placeholder" values that look real.
- **Never logged.** Passwords, tokens, API keys, signing and encryption keys, OAuth client secrets. Scrub them from error reporting, request captures, and exception trackers too.
- **No silent fallback.** A default like `env.SECRET ?? "dev-default"` ships to production the first time the variable is missing.

## Cryptography

Decide the primitives up front when crypto is in scope, and never roll your own primitive.

- **Password storage:** a KDF (argon2id, scrypt, bcrypt), not a plain hash. Parameters and salt encoded in the output. A pepper if the threat model includes store compromise. Plan the rotation path if defaults change.
- **Encryption:** authenticated modes only (AES-GCM, ChaCha20-Poly1305). Never CBC without an HMAC, never ECB. Nonces must be unique per key, so the nonce strategy is part of the design.
- **Randomness:** a cryptographic source for tokens, session IDs, reset keys, unguessable IDs, nonces, and anti-CSRF tokens. A general-purpose PRNG is not one.
- **Constant-time comparison** for any equality check on secret material.
- **Versioned ciphertext:** carry an algorithm or key-id marker in the stored format, so key rotation does not require rewriting every record.

## Deserialization and dynamic execution

- **No string-evaluating construct on untrusted input** (`eval`, a function built from a string, a timer taking a string, an in-context script runner). That is remote code execution.
- **Parsing is not validating.** A parsed blob asserted to a type is unsafe; validate after the parse.
- **YAML loaders:** verify the safe loader is used. Default loaders can construct arbitrary objects.
- **Native deserialization** (`pickle`, Java native serialization, `BinaryFormatter`, `unserialize`) is remote code execution on untrusted input. Where it is used at all, the input source must be fully trusted.
- **Dynamic import or require with a user-influenced path** is the same thing in disguise.

## Errors and information disclosure

Information disclosure happens at error time, so the error path is designed explicitly.

- **External errors are generic and stable in shape.** No internal IDs, stack traces, table names, query strings, or file paths in a public response body.
- **Internal logs are detailed** but redact PII and secrets.
- **Auth failures are uniform.** "User not found" and "wrong password" return the same response and, where feasible, the same timing. Same for password reset: "if this email exists, a reset is on its way."
- **No enumeration leak** in signup, password reset, or any path that confirms whether an identifier exists.

## Logging and audit

**Never log:** passwords, tokens, API keys, signing or encryption material. Full PII where an opaque ID will do. Authorization headers, cookies, session IDs. Request bodies of sensitive endpoints. Full card or bank account numbers.

**Always log, for a sensitive action** (login, password change, permission change, data export, admin action, financial transaction):

- Actor, target, action, timestamp, source IP and user agent, outcome.
- To an append-only destination separate from the application logs, integrity-protected (signed, write-once, or a remote sink).
- Retained per the applicable compliance window.
- Read by auditors and the system. Engineers typically read a redacted view, and that access control is part of the design.

## Outbound requests

Any outbound HTTP to a URL the user controls or influences: an image proxy, webhook delivery, "import from URL", document generation from external content.

- **Scheme allowlist** at minimum (`http` and `https` only), and a named host allowlist where the consumers are known.
- **Block private, loopback, and link-local ranges:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `::1`, `fc00::/7`, `169.254.0.0/16`, which includes the cloud metadata endpoint at `169.254.169.254`.
- **Validate after DNS resolution,** not just the URL string. DNS rebinding returns a public address at validation time and a private one at fetch time.
- **Constrain or disable redirects,** and revalidate every hop.

## CSRF and CORS

- **CSRF protection is needed when a state-changing endpoint relies on cookie auth:** a CSRF token, a double-submit cookie, or `SameSite` cookies. It is not needed for a pure bearer-token API, because the browser does not send that header automatically.
- **CORS:** a wildcard origin combined with credentials is invalid and dangerous. A reflected `Origin` with no allowlist is the most common misconfiguration and is equivalent to a wildcard. Preflight handling that returns success without CORS headers leaks intent more than it protects.

## File handling

- **Validate content type *and* magic bytes.** Never trust the extension or the declared content type.
- **Cap size at ingest,** not after the whole payload is buffered in memory.
- **Store outside the web root** and serve through a handler. A guessable, directly reachable storage path is the vulnerability.
- **Serve user uploads as attachments** with a benign content type. Never serve untrusted HTML, SVG, or JS inline from your own origin.
- **Generate storage identifiers server-side.** No user-provided path component ever reaches a storage path.

## Rate limiting and abuse cost

- **Per user *and* per IP.** IP-only is bypassable; user-only does not help pre-auth.
- **Stricter limits on sensitive endpoints:** auth, password reset, MFA, account creation, expensive search or export.
- **Cost-aware limits.** An expensive operation (document generation, model inference, full-table export) needs a limit proportional to cost, not to request count.
- **A lockout policy needs a recovery path.** A design that lets an attacker lock victims out at will has traded one denial of service for another.

## Dependencies and supply chain

For any new or upgraded dependency:

- **Known advisories.** Check the current CVE state.
- **Provenance.** Abandoned packages, recent ownership transfers, typosquats.
- **Install scripts.** A postinstall hook on an untrusted dependency is an execution surface on every developer machine and CI runner.
- **Transitive footprint.** A one-line import that pulls hundreds of transitive dependencies is both a risk and a cost.
- **Lockfile consistency.** An update that does not update the lockfile, or lockfile churn nobody reviewed, is a known attack path.
