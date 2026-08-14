# Security Design Prompts

Design-time security prompts — questions to ask before designing a security-relevant surface.

Generic by design — no library, framework, or compliance-standard lock-in. Libraries are named as examples of patterns, not requirements.

## Threat model

Decide what you're defending against before deciding how.

- **Who's the attacker?** Anonymous internet user, authenticated user of the system, authenticated user of a different tenant, malicious admin, a compromised dependency, an insider with database access?
- **What are they after?** PII, money, account takeover, control of the host, denial of service, information disclosure, lateral movement?
- **What trust boundary does this change cross?** Untrusted-to-trusted is where most vulnerabilities live; identify it explicitly. If no boundary is crossed, security thinking can be light.

The threat model bounds the rest. "Defending against everything" is a non-answer; "defending against a tenant exfiltrating another tenant's data" produces concrete design decisions.

## Authn / authz model

Identity and permission are different concerns.

- **Who's allowed to do this action?** State as a sentence: *"any authenticated user can read their own X; only org admins can write X for users in their org."*
- **Where does the check live?** Route-level *and* resource-level. Route-level is necessary but not sufficient — nearly every IDOR bug is a route-protected endpoint missing a resource check.
- **What identifies the resource?** If the user supplies the ID, the server verifies ownership / membership against the *session*, not against the request.
- **Multi-tenant?** Tenant comes from the session, never from the request body or URL unless cross-checked. Every query touching tenant-scoped data has a tenant filter — plan this with the query, not later.
- **Permission widening?** If this change increases what someone can do (new role, expanded scope, new public surface), call it out explicitly.

## Data classification

What's sensitive in this feature?

- **PII?** Email, phone, name, address, IP, DOB, location, device fingerprint. Plan encryption at rest, redaction in logs, access logging.
- **Secrets?** Tokens, API keys, signing keys, encryption keys — plan rotation strategy, storage location, access path.
- **Financial / regulated data?** Card numbers, bank accounts, health info — bring in compliance requirements (PCI / HIPAA / equivalent) at design time.
- **What's persisted vs ephemeral?** Persistence multiplies surface area (backups, logs, replicas, analytics pipelines).
- **What's logged?** Decide redaction strategy at design time. If a PII field exists in the data, every logger near it is a leak risk unless explicitly redacted.

## Validation boundary

Where does untrusted data become trusted?

- **Identify every boundary.** Every API request, every external response, every deserialized blob, every storage read of user-influenced data, every `postMessage`, every env var.
- **What's the schema?** Decide the validation strategy per boundary (schema library, hand-rolled, types-only-and-accept-the-lie).
- **Allowlist over denylist** for closed sets (URL schemes, file types, sort columns, redirect targets). Denylists miss the case the attacker found.
- **Canonicalize before validate** — normalize Unicode, URL encoding, path separators, case *before* checks; otherwise an equivalent representation slips past.
- **What happens on rejection?** Error code, error shape, log entry, alerting threshold.

## Failure-mode design

Information disclosure happens at error time. Design the error path explicitly.

- **External errors generic** — "Invalid request" / "Not found" — stable shape, no internal IDs, no stack traces, no table names, no file paths.
- **Internal logs detailed** — full context for debugging, but redact PII and secrets.
- **Auth failures uniform** — "User not found" and "wrong password" return the same response and (where feasible) the same timing. Same for password reset — "if this email exists, a reset is on its way."
- **No enumeration leaks** in signup, password reset, or any path that confirms whether an identifier exists.

## Cryptography choices (when crypto is in scope)

If this feature involves any cryptographic operation, decide primitives at design time.

- **Password storage** — KDF (argon2id / scrypt / bcrypt), not a plain hash. Plan parameters, plan rotation if defaults change.
- **Authenticated encryption** — AES-GCM / ChaCha20-Poly1305. Never CBC without HMAC, never ECB. Plan nonce strategy (counter, random — must be unique per key).
- **RNG** — cryptographic source (`crypto.randomBytes`, `crypto.randomUUID`, or platform equivalent) for tokens, IDs that must be unguessable, nonces, anti-CSRF tokens. Not `Math.random()`.
- **Constant-time comparison** for tokens, HMACs, signatures (`timingSafeEqual` or equivalent). `===` is a timing oracle.
- **Versioned ciphertext** — include an algorithm/key-id byte in stored format so key rotation doesn't require touching every record.

Never roll your own primitive.

## Audit-event design (when sensitive actions are in scope)

If this feature includes login, permission changes, exports, admin actions, financial moves, or any other action that needs traceability:

- **What gets logged?** Actor, target, action, timestamp, source IP / user agent, outcome.
- **Where?** Separate destination from app logs — append-only, integrity-protected.
- **Retention?** Per applicable compliance window.
- **Who can read the audit log?** Plan access controls. "Auditors and the system itself" is usually the right answer; engineers typically read via a redacted view.

## Outbound request safety (when calling external URLs)

If this feature makes outbound HTTP from user-influenced URLs (image proxy, webhook delivery, "import from URL", PDF generation from external content):

- **Host / scheme allowlist** — `http` / `https` only at minimum; named host allowlist for known consumers.
- **Block private and loopback ranges and metadata endpoints** — `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, link-local (includes `169.254.169.254` cloud metadata).
- **DNS-rebinding safe** — validate after DNS resolution, not just the URL string.
- **Redirects** — disable or constrain; revalidate every hop.

## Rate limiting & abuse cost (when DoS or abuse is in scope)

For any endpoint that's expensive, auth-related, or otherwise abuse-attractive:

- **Per-user AND per-IP** — IP-only is bypassable; user-only doesn't help pre-auth.
- **Cost-aware** — expensive operations (PDF generation, ML inference, full-table export) need limits proportional to cost, not request count.
- **Lockout policies have a recovery path** — flag designs that let an attacker lock victims out indefinitely.
- **Sensitive endpoints get stricter limits** — auth, password reset, MFA, account creation.

## Deserialization & dynamic execution

If this feature parses external data formats or constructs callables from input:

- **No `eval` / `Function(string)` / `setTimeout(string)` / `vm.runInThisContext`** on untrusted input — RCE.
- **`JSON.parse(x) as Type` is unsafe** — validate after parse.
- **YAML loaders** — verify the safe loader (`pyyaml.safe_load`, equivalent). Default loaders construct arbitrary objects.
- **Native deserialization** — `pickle`, Java native serialization, `BinaryFormatter`, `unserialize` are RCE on untrusted input. If used at all, the input source must be fully trusted.

## What good looks like

A security-relevant feature designed well at planning time produces:

- An explicit threat model — attacker, asset, boundary crossed
- Authn/authz stated as sentences, with checks at both route and resource level
- PII / secrets identified and redaction/encryption planned with the data
- Validation boundary identified per input, with strategy and rejection handling
- Error paths designed to disclose nothing
- Crypto primitives chosen up front when crypto is in scope
- Audit-event plan when sensitive actions are in scope