# Audit prompt template

Fill every `{PLACEHOLDER}`. Delete sections marked "optional" when they don't apply, and delete each `{IF_...}` line whose condition is false. Keep the wording of the rules, method, and report sections unless this repo needs a change. That wording was tuned against real runs. Keep the output contract as written apart from its placeholders, and don't restate it elsewhere: the checklist and the fix prompt check against it.

## Opening line

`{OWNERSHIP}` is the ownership line from step 1 of SKILL.md. `{AUTHORIZATION}` comes from the user's answer, and states nothing beyond it:

| Answer | `{AUTHORIZATION}` |
|---|---|
| Enrolled in the Cyber Verification Program | `I'm in Anthropic's Cyber Verification Program with {ACCESS_LEVEL}, and this session is sandboxed.` Without an access level: `I'm in Anthropic's Cyber Verification Program, and this session is sandboxed.` |
| Owner or maintainer, not enrolled | `This session is sandboxed.` |
| Authorized third-party testing | `I'm authorized to test it under {ENGAGEMENT}, limited to {SCOPE}, and this session is sandboxed.` |

## Placeholder notes

- `{SCOPE_LIMIT}`: empty, or `, limited to {SCOPE}` for third-party testing.
- `{FORBIDDEN_COMMANDS}`: the exact dev, start, seed, migration, deploy, publish, and release scripts, secret-manager wrappers and the scripts that call them, and installs or builds that need the network.
- `{SECRET_FILES}`: only the ones that exist or apply, such as `.env*` (except `.env.example`), credential files, registry credentials (`~/.npmrc`, `~/.pypirc`), and the config directories of the secret manager, cloud CLIs, and `gh`.
- `{PROD_HOSTS}` and `{THIRD_PARTIES}`: from recon items 7 and 9. If the repo has neither (many libraries and CLIs), replace that bullet with "Make no network requests. If something truly needs network access, stop and ask me first."
- `{IF_PROJECT_MCP}`: keep it when recon item 14 found project MCP servers that start without a prompt, naming them: `, including the {SERVERS} server(s) this repo configures`.
- `{CODE_KIND}`: application, library, or app.
- `{TEST_PLACEMENT}`: where new tests go and how they're named, by the repo's convention, with the `cvp` marker. For example "named `*.cvp.test.ts` next to the code it targets" or "named `test_cvp_*.py` under tests/security/". When test environments differ, name the location for each.
- `{TEST_SETUP}`: one to four sentences, or delete it. An Apple app whose only harness is `xcodebuild` needs a few more, as step 4 of SKILL.md describes. The existing test to copy and how it mocks the framework, database, or cache. "There's no database or cache in tests," when true. The libraries to mock because they call the network during verification (JWKS fetches, OCSP, license checks, telemetry). "No new dependencies." When tests bind ports or spawn servers: "Tests that bind localhost ports or start servers may fail in this sandbox; call handlers in-process where you can." When the project file lists sources explicitly: "Run `xcodegen generate` after adding or removing a test file" for XcodeGen, or "Add each test file to the {TEST_TARGET} target, and remove it again when the test leaves" for an Xcode project without synchronized folders.
- `{TEST_COMMAND}`: the exact single-file command. In a monorepo, give one per package or workspace with its project or workspace flags.
- `{REPORT_PATH}`: `docs/security/<date>-security-cvp-audit.md`, from step 4 of SKILL.md.
- `{ARCHIVE_EXAMPLE}`: one archived test path from this repo: `docs/security/tests/`, then the path the test runs from, relative to the repo root, then `.disabled`. For example `docs/security/tests/src/auth/session.cvp.test.ts.disabled`.
- `{TOOLED_EXTENSIONS}`: the extensions this repo's compiler, test runner, formatter, and linter pick up, such as `.swift`, or `.ts`, `.js`, `.vue`, and `.json`.
- `{CONTRACT_CHECK}`: `find docs/security -type f ! -path '{REPORT_PATH}' ! -path 'docs/security/tests/*.disabled' ! -path 'docs/security/harness/*' ! -name '*-security-audit.*' ! -name '*-dependency-scan.md'`, with the real report path. The two `-name` tests skip the reports `/security-audit` and `/security-scan-dependencies` write to the same folder, including any run while the audit is under way. If docs/security/ already holds files these patterns don't cover, such as earlier reports, insert `-newermt '<YYYY-MM-DD HH:MM>'` after `-type f`, set to the time you fill the prompt, so the check lists only what the audit adds. Keep the `{IF_PRIOR_FILES}` line whenever docs/security/ already holds files. The checklist and the fix prompt use the same command.
- `{INFRA}`: the hosting, provider, and store dashboards to check. For a library, the package registry and repository settings.

## Example

An invented Express + Vue multi-tenant invoicing SaaS that stores each tenant's payment-processor and SMS API keys, to show the level of specificity expected:

- Actors: "an admin or member of a paying tenant, a user on a free trial, an invoice recipient holding a public payment link, or an unauthenticated stranger"
- Goal: "Get another tenant's payment-processor or SMS API key in plaintext, or weaken the per-tenant encryption that protects them (key derivation, nonce reuse, plaintext fallbacks, the key-rotation script in server/scripts/rotate-keys.ts)."
- Forbidden: "Do NOT run `npm run dev` or `npm run db:seed` (both wrap `op run`), `docker compose up`, or anything that loads real secrets."
- Test setup: "Follow server/routes/invoices.test.ts, which stubs `req.tenant` and mocks server/db.ts. There's no database in tests. Mock the payment SDK and the JWKS fetch in server/auth/verify.ts. Component tests that need jsdom go in client/tests/. Run with `npx vitest run --project server <file>`, or `--project client` for client tests."
- Archive example: "docs/security/tests/server/routes/tenant-keys.cvp.test.ts.disabled"
- Tooled extensions: "`.ts`, `.js`, `.vue`, or `.json`"

---

```text
This is {NAME}: {ONE_LINE_PURPOSE}. It's {OWNERSHIP}. {AUTHORIZATION} I want a
deep security review of this codebase that finds real, exploitable bugs and
proves each one.
{OPTIONAL_FOCUS_LINE: "Focus on {AREA}; cover the rest only as far as it leads into {AREA}."}

## Scope and rules
- In scope: this repository only{SCOPE_LIMIT}, exercised through {HARNESS} and
  local code.
- Do NOT run {FORBIDDEN_COMMANDS}, or anything that loads real secrets. Don't
  read {SECRET_FILES}.
- Make no network requests to production ({PROD_HOSTS}) or to {THIRD_PARTIES}.
  Mock every third-party service. If something truly needs network access, stop
  and ask me first.
- MCP tools run outside this sandbox, so don't call any{IF_PROJECT_MCP}.
- Don't change {CODE_KIND} code. Leave files only where the output contract
  at the end allows.
- No git commits, pushes, or branch changes.

## Read first
{READ_FIRST: bullet list, at most 8 paths, security-relevant only}
{IF_PRIOR_AUDIT: "- {PRIOR_AUDIT_PATH}. Don't re-report its open findings unless you find a worse variant or new impact."}

## Attacker goals to pursue
Think like {ACTORS} trying to:
1. {GOAL, in repo terms, naming real assets, features, and files}
2. ...
(5 to 9 goals, riskiest first)

## Retest the previous audit (optional)
- Try to bypass the fixes for {FIXED_IDS}.
- Settle the needs-investigation items {NEEDS_INVESTIGATION_IDS} as far as the
  code allows. For anything that depends on live {INFRA} setup, tell me exactly
  what to check and how.

## Open dependency alerts (optional)
{ALERT_LIST: severity, package, advisory ID, one-line summary}
For each one, decide whether the vulnerable code is reachable from this
codebase. Prove it's reachable with a test, or show the call path that makes it
unreachable.

## Method
1. Map the attack surface: every {SURFACE_UNIT: route / entry point / public
   API / command / URL handler}, what protects it, {TENANCY_LINE: "where
   tenantId comes from,"} and every place untrusted input reaches {SINKS}. Show
   me the map, then keep going.
2. Hunt each attacker goal against that map. Prefer depth on the riskiest paths
   over a broad checklist.
3. For every candidate, write a {FRAMEWORK} test {TEST_PLACEMENT} that fails on
   the current code and demonstrates the bug, with external services mocked.
   {TEST_SETUP}
   Run it with `{TEST_COMMAND}`. A finding counts as Confirmed only if its test
   fails for the right reason. Otherwise mark it Unconfirmed and say what
   evidence is missing. Store every test as the output contract says.
4. If the sandbox blocks `{TEST_COMMAND}` itself, an alternative harness, such
   as calling the compiler and test runner directly, beats no proof. Keep its
   files within the output contract. Its result counts as Confirmed only if the
   same test would also compile and run unchanged in the real project.
5. Before reporting, try to disprove each Confirmed finding: look for upstream
   checks, {ORDERING: middleware ordering / call-site validation}, or deploy
   config that blocks it.

## Report
Write the report with:
- A summary table: ID (CVP-01, ...), severity, Confirmed or Unconfirmed,
  one-line problem, file:line, and the archived test's path.
- For each finding: attacker and access needed, step-by-step exploit path,
  impact, the test that proves it and how you ran it, and a specific fix. For a
  test run through an alternative harness, also give the exact command that
  runs it through the real project.
{IF_RETEST: "- Retest results for the previous audit's items."}
{IF_ALERTS: "- A reachable or unreachable verdict for each dependency alert."}
- What you couldn't determine from code, and what I should check in {INFRA}.
Don't fix anything yet. I'll choose what to fix after reading the report.

## Output contract
However your runs went, leave this layout under docs/security/, in paths git
ignores:
- The report at exactly {REPORT_PATH}, even if today's date differs, with the
  IDs and summary table above.
- Every proof test, helper, and fixture at docs/security/tests/<the
  repo-relative path it would run from>.disabled, for example
  {ARCHIVE_EXAMPLE}, whether or not it ever sat in the source tree. Proof tests
  fail by design, so one sits at its source path only while it runs.
- Anything else you keep, such as alternative-harness scripts and run logs, in
  docs/security/harness/, with no file ending in {TOOLED_EXTENSIONS}.
- Build staging, such as copies with `.disabled` stripped, in a `mktemp -d`
  directory outside the repo, deleted after each run.
{IF_PRIOR_FILES: "- Leave the files that were already in docs/security/ alone."}
Before you finish, check that `{CONTRACT_CHECK}`
prints nothing, that the summary table cites each test by its archived path, and
that `git status --porcelain` lists nothing. If a check fails, move your files
into place, undo any other change, and check again.
```
