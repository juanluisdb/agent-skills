# Security Review Practices

Deep-dive reference for the security expert. Loaded alongside the review checklist when security is in scope (default for the security expert; everyone else relies on the checklist's brief "Security" dimension).

Generic by design — no library, framework, or compliance-standard lock-in. Concrete examples are named as *examples* of a pattern, not as requirements.

## Trust Boundary Inventory

Untrusted data enters from many places. For each boundary in the diff, ask: is data validated at entry, and is the validated type the one used downstream?

Common boundaries:

- HTTP request body / query / headers / cookies
- File uploads
- Message queue / event bus payloads
- Third-party API responses
- Database reads of data written by untrusted sources
- Deserialized blobs from any source
- IPC / RPC channels
- Environment variables and config files
- Browser URL, hash, history state, `postMessage` events
- Client-side storage (`localStorage`, `sessionStorage`, IndexedDB) read by the same app

Anything crossing one of these is a candidate finding if the validated type doesn't replace the raw type in subsequent code.

## Input Validation & Canonicalization

- **Validate at the boundary**, not deep in business logic. Scatter validation and reviewers cannot tell whether a value is trusted at any given line
- **Allowlist over denylist** for closed sets (URL schemes, file types, sort columns, enum values, redirect targets). Denylists miss the cases the attacker found
- **Canonicalize before validate** — normalize Unicode (NFC/NFKC), URL encoding, path separators, and case *before* checks. Otherwise an equivalent representation slips past
- **Validated type replaces raw type** — if `req.body` is `unknown` and validation returns `UserInput`, downstream code accepts `UserInput`, not `any`. Otherwise validation is theatre

## Injection — Full Surface

A per-channel checklist. Untrusted data interpolated into any of these is a finding unless the channel-specific safe API is used.

- **SQL / NoSQL** — parameterized queries / prepared statements only. Flag string concatenation regardless of "internal trust" claims
- **Command / shell** — argv-form spawn; never shell concatenation. If shell is unavoidable, escape with a vetted library
- **OS paths / traversal** — resolve and verify the result is under the expected root. Reject `..`, absolute paths, and symlinks that escape the root
- **Template injection** — server-rendered templates, log format strings, and *LLM prompt templates* are all injection surfaces
- **LDAP / XPath / regex injection** — less common but real; same rule: parameterize or escape
- **Open redirect** — `Location` headers, `window.location`, and client-side router pushes taking untrusted URLs need a host/scheme allowlist
- **Header injection** — CRLF in user-controlled values reaching response headers; flag any direct interpolation

## Authentication vs Authorization

The conflation between "who" and "may they":

- **Authn** = identity verified. **Authz** = permission to act on *this specific resource*
- Route-level authz is necessary but not sufficient. Nearly every IDOR (insecure direct object reference) bug is a route-protected endpoint missing a `WHERE owner_id = current_user` (or equivalent)
- **Tenant ID from the session / token, never from the request body or URL** unless cross-checked against the session
- Permission-widening diffs (role check, scope, policy doc, middleware reordering) deserve explicit attention — these are the highest-blast-radius security changes

## Session, Tokens, and Identity Material

- **Token storage trade-offs** — cookie (`HttpOnly` + `SameSite`) vs JS-accessible storage. JS-readable tokens are XSS-exfiltratable; if the threat model allows XSS, they're game over
- **Lifetime and revocation** — short-lived access tokens + refresh, or session table for revocation. Stateless JWT with no revocation path is a finding if anything sensitive depends on it
- **No tokens in URLs** — they leak via referrer headers, logs, browser history, and shoulder-surfing
- **Constant-time comparison** for tokens, HMACs, and signature checks (`timingSafeEqual` or equivalent). `===` / `strcmp` is a timing oracle for byte-by-byte token recovery

## Secrets & Credentials

- **No hardcode, no commit** — check `.env`, `.env.sample`, CI variables drifting into the diff, and "DEV placeholder" values that look real
- **Never log** — passwords, tokens, API keys, signing keys, encryption keys, OAuth client secrets. Scrub from error reporting, request captures, exception trackers
- **Environment-specific retrieval** — no silent fallback like `process.env.SECRET ?? "dev-default"`. The fallback ships to prod the first time the env var is missing
- **Rotation story** exists for anything long-lived. If a secret has no path to rotate, the system has no path to recover from disclosure

## Cryptography Hygiene

- **Never roll your own primitive** — use the platform standard library or a vetted package. "I'll just XOR with a constant" is always a finding
- **Password storage** — KDF (argon2id / scrypt / bcrypt), not a plain hash. Parameters and salt encoded in the output. Pepper if the threat model includes DB compromise
- **Cryptographic RNG** for anything security-relevant: tokens, session IDs, password reset keys, nonces, anti-CSRF tokens. Never `Math.random()` / `random.random()` for these
- **Encryption** — authenticated modes only (AES-GCM, ChaCha20-Poly1305). Never CBC without HMAC, never ECB. Nonces must be unique per key
- **Constant-time** for any equality check that could leak secret material byte by byte
- **Versioned ciphertext** — include an algorithm/key-id byte in the stored format so key rotation doesn't require reading every record

## PII & Sensitive Data Minimization

- **Collect what's needed** — everything else is liability without value
- **Encrypt at rest and in transit** — backups, log destinations, analytics pipelines are the same surface as the primary DB
- **Redact in logs / errors / analytics / exception trackers** — flag PII fields in code (typing, naming, comments) so reviewers can grep before they hit production
- **Retention** — delete or anonymize on schedule; an audit entry precedes deletion
- **Right-to-erasure paths** exist and are exercised by tests, not just documented

## Error Handling & Information Disclosure

- **External errors are generic; internal logs are detailed** — stack traces, internal IDs, table names, query strings, file paths never reach a public response body
- **Auth failures return the same shape** for "user not found" and "wrong password" — username enumeration is the most common leak here. Same for password reset ("if this email exists, a reset is on its way")
- **500-level errors** logged with full context but produce a stable, opaque message externally — including the same response shape and timing characteristics as 4xx where feasible

## Logging Discipline

**Never log:**

- Passwords, tokens, API keys, signing keys, encryption material
- Full PII (email, phone, SSN, address, DOB) when an opaque ID will do
- Authorization headers, cookies, session IDs
- Request bodies of sensitive endpoints
- Full payment card / bank account numbers

**Always log for sensitive actions** (login, password change, permission change, data export, admin action, financial transaction):

- Actor, target, action, timestamp, source IP / UA, outcome
- Append-only destination, separate from app logs
- Retained per applicable compliance window
- Integrity protections (signed, write-once, or remote sink)

## SSRF & Outbound Request Safety

Any outbound HTTP from a URL the user controls or influences (image proxy, webhook, "import from URL", PDF generation from external content):

- **Host allowlist** or scheme allowlist — `http`/`https` only at minimum
- **Block private and loopback ranges** — `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `::1`, `fc00::/7`, `169.254.0.0/16` (link-local, includes cloud metadata endpoints like `169.254.169.254`)
- **Validate after DNS resolution**, not just the URL string — DNS rebinding returns a public IP at validation time and a private IP at fetch time
- **Constrain or disable redirects** — re-validate every hop

## Deserialization & Dynamic Execution

- **No `eval` / `Function(...)` / `setTimeout(stringArg)` / `vm.runInThisContext`** on untrusted input. Full RCE
- **`JSON.parse(x) as Type` is unsafe** — validate after parse
- **YAML loaders** — verify the safe loader is used; default `pyyaml.load`, untyped YAML parsers, etc. can construct arbitrary objects
- **Native deserialization** — Python `pickle`, Java native serialization, .NET `BinaryFormatter`, PHP `unserialize` are RCE on untrusted input
- **Dynamic `require` / `import`** with user-influenced paths is RCE in disguise

## CSRF & CORS

- **CSRF** — needed when state-changing endpoints rely on **cookie auth**. CSRF tokens, double-submit cookies, or `SameSite=Strict/Lax` cookies. Not needed for pure bearer-token APIs where the auth header is not auto-sent by browsers
- **CORS** —
  - `Access-Control-Allow-Origin: *` combined with `Allow-Credentials: true` is invalid and dangerous; flag any config that produces this
  - Reflected `Origin` without an allowlist is the most common CORS misconfig — equivalent to wildcard
  - Preflight handling errors (returning 200 with no CORS headers) leak intent more than they protect

## File Handling

- **Validate content-type AND magic bytes** — never trust the extension or the `Content-Type` header
- **Size cap at ingest**, not after the whole payload is buffered in memory
- **Store outside the webroot** and serve via a handler — never let the storage path be guessable and directly reachable
- **Serve with `Content-Disposition: attachment`** and a benign content-type for user uploads. Never serve untrusted HTML/SVG/JS inline from your origin
- **Filename sanitization** — never use user-provided path components in storage paths; generate server-side identifiers

## Multi-Tenancy Isolation

- **Every query touching tenant-scoped data has a tenant filter** — reviewers should grep changed queries and verify
- **Caches key on tenant** — in-memory, Redis, CDN — a tenant-unaware cache key is a silent data leak
- **Background jobs carry tenant context explicitly** — never "current tenant" from a global / thread-local that isn't reset between jobs
- **Tests cover two tenants** — one tenant's test passing tells you nothing about isolation; a cross-tenant assertion is what catches the bug

## Rate Limiting & Abuse Cost

- **Sensitive endpoints get stricter limits** — auth, password reset, MFA, account creation, expensive search/export
- **Per-user AND per-IP** — IP-only is bypassable; user-only doesn't help pre-auth
- **Lockout policies need a recovery path** — flag account-lockout DOS where an attacker can lock victims out at will
- **Cost-aware limits** — expensive operations (PDF generation, ML inference, full-table export) need limits proportional to cost, not request count

## Dependency & Supply Chain

For any new or upgraded dependency in the diff:

- **Known CVEs** — check current advisory state
- **Maintainer / provenance** — abandoned packages, recent ownership transfers, typosquats
- **Install scripts** — `postinstall` and equivalents on untrusted deps are an exec surface on every developer machine and CI runner
- **Transitive footprint** — a one-line import that pulls 200 transitive deps is both a risk and a cost
- **Lockfile consistency** — updates that don't update the lockfile, or lockfile churn that isn't reviewed, are common attack vectors

## Change-Pattern Triggers

A diff matching any of these patterns calls for a security pass even if "security" isn't in the description:

- New / modified auth, middleware, policy, or guard code
- New public route, public API, or exported RPC procedure
- New outbound HTTP call to a user-influenced URL
- New deserialization site or schema migration
- Touches anything in `crypto`, `auth`, `session`, `permission` paths
- Removes a guard, validation, or feature-flag check
- Widens a permission, role, scope, or CORS origin
- New PII field in a model or new logger call near a PII field
- New file upload or download path
- New `dangerouslySetInnerHTML`, `target="_blank"`, or `postMessage` (see browser-platform specifics in `frontend-review.md`)

## Cross-References

- Browser-platform security details (XSS via `dangerouslySetInnerHTML`, target=_blank, token storage at the browser level, `postMessage` origin checks): see `frontend-review.md` § Browser security
- General review dimensions and overall flow: see `review-checklist.md`