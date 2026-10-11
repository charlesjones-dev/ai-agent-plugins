# Attack catalog

Raw material for step 3. Pick the items that apply, then rewrite each in the repo's own terms. Don't paste the list verbatim.

## Every project

- **Secrets:** keys committed to the repo or its history, keys shipped in client bundles or app binaries, tokens or keys written to logs.
- **Dependencies:** whether open advisories are reachable from this code.
- **CI/CD:** `${{ github.event.* }}` interpolated into `run:`, `pull_request_target` checking out PR code, unpinned third-party actions, broad `GITHUB_TOKEN` permissions, secrets reachable from fork PRs, publish workflows without provenance or OIDC.

## Web app, SaaS, API

1. **Cross-tenant access (IDOR):** read or change another tenant's records; check where the tenant ID is derived, plus bulk, export, and search endpoints, and background jobs that batch tenants together.
2. **Account takeover:** OAuth state and PKCE, linking accounts by email, OTP and magic links (brute force, reuse, races), password reset, session signing, fixation, and revocation, cookie flags, CSRF on state-changing routes.
3. **Privilege escalation:** becoming admin, mass-assignable role or tier fields, admin routes, IP allowlists that trust forwarded headers.
4. **Billing and entitlements:** paid features without paying, payment webhook forgery, replay, or out-of-order delivery, limits enforced only in the client, self-assigned tiers.
5. **Webhook trust:** signature checks (raw body, timing-safe compare, timestamp tolerance), idempotency races, payloads not bound to the right tenant.
6. **SSRF:** the server fetching attacker-influenced URLs (logos, images, link previews, scanners, headless browsers), redirects, DNS rebinding, IPv6 and numeric-IP forms, cloud metadata, private networks such as a host's private service network (`*.internal` names).
7. **Injection:** NoSQL operators, SQL, shell commands, HTML in emails and PDFs, CSV formulas, headers, path traversal in uploads and file serving, prototype pollution, ReDoS.
8. **Secrets at rest:** encryption of third-party keys and PII (key derivation, nonce reuse, plaintext fallbacks, repair or migration paths), APIs that echo stored keys back.
9. **Abuse and cost:** rate limits keyed on spoofable IPs, unauthenticated endpoints that trigger email, SMS, printing, or LLM calls, exhausting a tenant's third-party quota.
10. **Client side:** XSS (`v-html`, `innerHTML`, `dangerouslySetInnerHTML`, markdown rendering), open redirects, CSP gaps, tokens in `localStorage`.

## Apple apps (iOS, macOS, watchOS, widgets)

1. **Credential storage:** OAuth tokens and keys in the Keychain with a sensible accessibility class, versus `UserDefaults`, plists, SwiftData, or app-group containers; secrets syncing through iCloud.
2. **Data leakage:** logs (`print`, `os_log` privacy levels), crash reports, widget and app-group containers, backups, pasteboard, app-switcher snapshots, Spotlight and Handoff indexing.
3. **Inbound entry points:** URL schemes, universal links, App Intents and Shortcuts, share extensions, notification payloads. Can a crafted link trigger an action or leak data?
4. **Web content:** `WKWebView` loading remote or user content, `WKScriptMessageHandler` bridges, file URL access, navigation policy.
5. **Hostile servers:** ATS exceptions, custom trust evaluation, HTTP fallbacks. For apps that query arbitrary hosts, check handling of oversized responses, redirect loops, malformed certificates or DNS, and parser crashes.
6. **Purchases:** StoreKit 2 `VerificationResult` handling, entitlement state stored locally where it can be edited, refunds and revocations.
7. **OAuth:** PKCE, state checks, redirect handling, refresh and revocation, scopes requested versus needed.
8. **Build config:** secrets in committed xcconfig files or the compiled binary.

Verification note: `swift test` on a SwiftPM package is the friendliest option inside the sandbox. `xcodebuild test` doesn't run there, and without the optional Apple launch line, neither do `xcodegen` and `xcodebuild` builds. The audit model may then use an alternative harness, such as `swiftc` plus `xcrun xctest` on macOS, under the prompt's output contract: each test stays at `docs/security/tests/<path>.disabled`, staged `.swift` copies go in a `mktemp -d` directory and are deleted after each run, and build scripts and run logs go in `docs/security/harness/` with no `.swift` file there. A result counts as Confirmed only if the test would also compile and run unchanged in the real project. For each proof, the report gives the `xcodebuild test` command that runs it through the real project, and the fix session runs it.

## Libraries and packages (npm, PyPI, SwiftPM, crates, gems)

1. **Hostile input to the public API:** ReDoS, prototype pollution, deep recursion, path traversal, unsafe defaults.
2. **Code execution:** `child_process` with interpolated input, `shell: true`, `eval` or `Function`, dynamic `require` or `import`, unsafe deserialization (`pickle`, `yaml.load`).
3. **Network:** fetching caller-supplied URLs (SSRF once embedded in a server), headless browsers loading untrusted pages (sandbox flags, `file://` access, reaching the local network), disabled TLS verification.
4. **Package contents:** what a publish would ship (files listed by `npm pack --dry-run` or the built sdist and wheel, source maps, stray `.env` files), install scripts.
5. **Downstream impact:** for each finding, which consumer configurations are exposed.

## CLI tools, Claude Code plugins, hooks, MCP servers

1. **Command injection** through file names, branch names, environment variables, or tool input passed to a shell.
2. **Untrusted repo content:** hooks or scripts that act on it, prompt-injection-driven execution, reading files outside the project.
3. **Filesystem:** path traversal and symlink following when reading or writing.
4. **Secrets:** tokens read from env or files leaking into output, logs, or model context.
5. **Unsafe defaults:** auto-approving dangerous actions, broad permissions in shipped settings.
6. **Install and update paths:** `curl | sh`, unsigned or unpinned downloads.

## Home Assistant and local-network integrations

1. **Credentials:** stored in config entries, redacted in diagnostics, kept out of logs.
2. **Remote responses:** trusted without checks, letting injected entity names or attributes reach the frontend.
3. **Transport:** TLS verification, timeouts, unbounded responses.
4. **Config flow input:** user-entered URLs causing SSRF from the HA host.

## Static and marketing sites (Nuxt, Next.js, Astro, Vite and similar)

1. **Server routes:** contact forms (email header injection, spam relay, rate-limit bypass).
2. **Client bundle:** secrets in public runtime config (`runtimeConfig.public`, `NEXT_PUBLIC_*`, `VITE_*`) or the bundle, third-party scripts, open redirects.
3. **Headers:** CSP and other security headers actually served in production versus configured.
4. **Prerender:** draft or private data leaking into prerendered output.
