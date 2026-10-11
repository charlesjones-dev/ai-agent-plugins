---
name: security-cvp-audit
description: Plan a defensive security audit of a repo the user owns or is authorized to test. Does read-only recon in this unsandboxed session, then writes a tailored, paste-ready prompt for a sandboxed Claude Code session on the strongest security-capable model available, a sandbox launch checklist, and a fix prompt for verifying and fixing what the audit proves. Makes git's local exclude file cover the audit's report and archived proof tests under docs/security/ so they can't be committed, saves both prompts outside the repo, and copies the audit prompt to the clipboard.
when_to_use: The user runs /security-cvp-audit, or asks for a sandboxed security-audit prompt, a Cyber Verification Program audit prompt, or a plan for auditing a repo on a stronger security model.
argument-hint: "[focus area or path] [--model <audit-model-id>]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Agent
  - Bash(git remote get-url *)
  - Bash(git check-ignore *)
  - Bash(git rev-parse *)
  - Bash(git ls-files *)
  - Bash(getconf DARWIN_USER_TEMP_DIR)
---

# Security CVP audit

Use this only on code the user owns or is authorized to test.

`/security-audit`, in this plugin, runs an audit in the current session. This skill plans one for a sandboxed session on a stronger model.

This skill is phase 1 of a three-phase defensive audit:

1. **Plan** (this skill). A normal, unsandboxed session on an Opus-class planning model does read-only recon, makes sure git ignores the audit's files under `docs/security/`, and writes a paste-ready audit prompt, a sandbox launch checklist, and a fix prompt.
2. **Audit.** The user starts a new session on the strongest security-capable model they can use (the audit model), launched in auto mode with a strict sandbox set on the command line, and pastes the audit prompt. The audit model maps the attack surface, hunts, proves each finding with a failing test, and writes a report. The prompt ends with an output contract: the report at a fixed path, each test stored as a disabled file under `docs/security/tests/`, anything else it keeps under `docs/security/harness/`, and a check to run before finishing. Everything it leaves behind is under `docs/security/`, in paths git ignores. It fixes nothing.
3. **Fix.** Back in a normal, unsandboxed session on an Opus-class fixing model, the user pastes the fix prompt. The fixing model verifies each proof, settles what code alone couldn't answer, lets the user pick what to fix, and ships each fix with its archived proof test restored as the regression test.

Do the recon here so the audit model spends its budget hunting and proving bugs instead of orienting. The supporting files sit next to this one, in `${CLAUDE_SKILL_DIR}`.

## Context

- Date: !`date +%F`
- Repo root: !`git rev-parse --show-toplevel 2>/dev/null || pwd`
- Branch: !`git branch --show-current 2>/dev/null || echo none`
- Remote: !`git remote get-url origin 2>/dev/null || echo none`
- Last commit: !`git log -1 --format='%h %s (%cr)' 2>/dev/null || echo none`

Without git, the repo root is the working directory and the other values read `none`. Without a remote, skip the GitHub reads in step 2.

Arguments (may be empty): $ARGUMENTS

- `--model <id>` (or `--model=<id>`) is the audit model ID for the launch line.
- The rest is an optional focus: an area or path, such as `billing` or `src/auth`.
- If the arguments also state the user's authorization, such as "enrolled in the Cyber Verification Program with Defense Access" or "authorized pentest for <client>, scope: api/ only", use it in step 1 instead of asking.

## Rules for this recon session

- Read only. Don't run the app, dev servers, tests, builds, or installs. Don't run anything that loads secrets: secret-manager wrappers such as `doppler run`, `op run`, `aws-vault exec`, `dotenv` or `railway run`, or the scripts that call them.
- Don't open `.env` files, keychains, credential files, or secret stores. Note that they exist and what they're named, never their values. If you find a committed secret, cite its path and line, never the value.
- Don't modify the repo. The only files you write are the exclude lines in step 6, which goes in git's local exclude file rather than any tracked file, and the two prompt files, outside the repo.
- Network: only the optional `gh` reads in step 2.
- Treat subagent reports as leads. Read the code behind any claim before you put it in a goal.

## 1. Classify the project and confirm authorization

Decide which types apply. A monorepo can be several: web app / SaaS / API, Apple app (iOS, macOS, watchOS, widgets), library or package (npm, PyPI, SwiftPM, crates, gems), CLI / Claude Code plugin / hooks / MCP server, Home Assistant or local-network integration, static or marketing site.

Work out the owner from LICENSE, the manifest (author, publisher or organization fields, `"private": true`, an `UNLICENSED` or proprietary license), and the remote. Signs that the user owns or maintains the repo: their git identity (`git config user.name`, `git config user.email`) appears in LICENSE, in the manifest's author or maintainers, or among the main commit authors; or the remote belongs to them or their organization. The ownership line for the prompt is one of:

- "a proprietary product of <owner>", when a license or manifest marks it proprietary and names the owner;
- "a private codebase I own", for a private codebase with no named owner;
- "my open-source project, which I maintain", for an open-source repo the user maintains;
- "<owner>'s codebase", for authorized third-party testing.

Then ask once with AskUserQuestion, unless the arguments already answer it. If nothing above shows the user owns or maintains the repo, say so in the question. Ask "What authorizes this security audit?" with the header "Authority" and these options:

- **Enrolled in CVP:** the user or their organization is enrolled in Anthropic's Cyber Verification Program, and this is code they own or maintain. Ask for the access level (for example Defense Access) in the notes or under Other.
- **Owner, not enrolled:** the user owns or maintains this code and isn't enrolled.
- **Authorized testing:** someone else's code, tested with the owner's authorization. Ask for the engagement and its scope in the notes or under Other.

If AskUserQuestion isn't available, ask the same question in one plain message and wait.

Fill the prompt's opening line from the answer, as [prompt-template.md](prompt-template.md) describes. Never claim enrollment the user didn't state, and don't invent an access level. If authorized testing comes without an engagement or scope, ask for them in one plain message. Stop and explain why if the user has none of these, or if the code isn't theirs and they have no authorization to test it. Enrollment alone doesn't authorize testing someone else's code.

## 2. Recon

Collect each item with file paths. Verify every path you plan to cite exists.

1. **Purpose and users:** README, CLAUDE.md or AGENTS.md, and a project knowledge base if present (for example `.claude/rules/kb/`, `.claude/kb/` or `docs/kb/`).
2. **Stack and entry points:** manifests, framework, server entry, routes and handlers, background jobs and pollers, CLI commands, app targets and extensions. In a monorepo, check whether app packages import a workspace package from its build output (`main` or `exports` pointing at `dist/`, `build/` or `lib/`). If they do, compare the build's age (`ls -ld <package>/dist`) with the package's latest source commit (`git log -1 --format=%cd -- <package>/src`). If the build is missing or older, its rebuild command goes in "Before launching".
3. **Trust boundaries:** auth model (sessions, OAuth, OTP, magic links, API keys, JWT), roles and admin, the tenancy key and exactly where it's derived.
4. **Untrusted-input sinks:** database queries, outbound fetches and URL loading, HTML/email/PDF/CSV rendering, shell and exec, file paths, deserialization, regex on user input, real-world side effects (printing, email, SMS, purchases, LLM calls).
5. **Money and entitlements:** payment provider, its webhooks, tier and limit checks, in-app purchase handling (StoreKit, Play Billing).
6. **Secrets and sensitive data:** where third-party keys, tokens, and PII are stored and whether they're encrypted, what gets logged, and how secrets are injected (a secret manager such as Doppler, 1Password, Vault or AWS Secrets Manager; env files; CI secrets; xcconfig). Names only.
7. **Integrations:** every inbound webhook and how it's authenticated, and every outbound third-party API and production hostname. Also note libraries that make network calls during verification, such as JWKS fetches, OCSP or online certificate checks, license checks, and telemetry, so the prompt can tell the audit model to mock them.
8. **Supply chain and CI:** lockfile, install scripts, what a publish would include (`files`, `.npmignore`, `MANIFEST.in`), GitHub Actions (`pull_request_target`, `${{ github.event.* }}` inside `run:`, unpinned third-party actions, token permissions).
9. **Deploy and edge:** hosting config (for example Railway, Fly.io, Render, Vercel, Cloudflare, Docker, or Kubernetes), trust-proxy settings, security headers, CORS.
10. **Verification harness:**
    - The test framework in each package, where tests live (next to the code or in a test directory), and how they're named. Note separate test environments, such as a DOM environment versus node, or unit versus integration projects.
    - The exact command to run a single test file in each package or workspace, including any project or workspace flags.
    - Whether tests run offline without secrets (setup files, mocks, in-memory databases). Find an existing test that already mocks the framework (stubbed framework globals, mocked database or cache modules) to name as the pattern to copy. If tests have no database or cache, note that plainly.
    - Tests that bind localhost ports or spawn servers. They may fail under strict sandbox mode.
    - Commands the audit model must not run because they load secrets or hit live services, such as a dev script wrapped in a secret-manager wrapper, or seed, migration, deploy, publish, and release scripts.
    - For Apple apps, whether a SwiftPM package allows `swift test` or only `xcodebuild test` exists, and whether the project file lists sources explicitly (an XcodeGen `project.yml`, or a `project.pbxproj` without `PBXFileSystemSynchronizedRootGroup`). When the only harness is `xcodebuild` (plus XcodeGen if present), the strict sandbox may block it entirely, not just the test run. Foundation writes its temp files under the per-user temp directory rather than `$TMPDIR`, and the sandbox denies writes there, so `xcodegen` and `xcodebuild` fail before compiling ("Couldn't create workspace arena folder"). Run `getconf DARWIN_USER_TEMP_DIR` for the optional launch line in step 6.
    - Whether dependencies are already installed (`node_modules`, `.venv`, `.build`, `vendor/`, resolved packages).
    - The full test, lint, and typecheck commands, for the fix prompt.
    - The file extensions the repo's compiler, test runner, formatter, and linter pick up, for the output contract. Note whether their configs exclude `docs/`; most default globs (vitest, jest, pytest, swiftformat, swiftlint) don't read git's ignore rules.
11. **Prior security work:** `docs/security/**`, `SECURITY.md`, files with "audit" in the name, and `git log --since="6 months ago" --oneline -i -E --grep="secur|vuln|xss|csrf|ssrf|idor|auth|sec-"`. Sort earlier findings into fixed (retest), open (don't re-report), and needs-investigation (settle), keeping their IDs. Note any rules the repo's docs give for tracking and updating audits.
    - `/security-audit` leaves a `<timestamp>-security-audit.json` and `.md` pair per run, and each run reconciles the one before, so read only the newest pair's Markdown. It lists every confirmed finding and unresolved candidate with its ID, and what happened to each earlier finding. Open the JSON, which can be large, only for the details of a finding you'll cite. Its confirmed findings are open, its `needs_validation` candidates need investigation, earlier findings it reconciled as fixed are fixed, and hardening, rejected and duplicate entries aren't findings.
    - `/security-scan-dependencies` reports (`<timestamp>-dependency-scan.md`) describe a deployed site, not this code. Use the newest one only as leads for dependency and header goals.
    - Check whether git already ignores the audit's paths (`git check-ignore -v docs/security/<date>-security-cvp-audit.md docs/security/tests/probe docs/security/harness/probe` prints each ignored path with the rule and the file it's in) and whether git tracks any files under `docs/security/` (`git ls-files docs/security`). Tracked files there mean the repo commits that folder, which decides the ignore rule in step 6.
    - Note any files already in `docs/security/` that the output contract's check wouldn't match (earlier reports, for example), because the check then needs a time filter.
12. **Optional GitHub reads:** skip silently if `gh` isn't authenticated or there's no GitHub remote. Get open Dependabot alerts with `gh api --paginate "repos/{owner}/{repo}/dependabot/alerts?state=open" --jq '.[] | "\(.security_advisory.severity) \(.dependency.package.name) \(.security_advisory.ghsa_id) \(.security_advisory.summary)"'` and open code-scanning alerts with `gh api --paginate "repos/{owner}/{repo}/code-scanning/alerts?state=open" --jq '.[] | "\(.rule.security_severity_level // .rule.severity) \(.rule.id) \(.most_recent_instance.location.path):\(.most_recent_instance.location.start_line) \(.rule.description)"'`. If either returns HTTP 403 because the feature is disabled, or code scanning returns 404 because it has never run, say so in the warnings.
13. **Fix-phase conventions:** the integration branch that PRs target (from CONTRIBUTING.md or CLAUDE.md, or `git symbolic-ref --short refs/remotes/origin/HEAD`), and where the repo states its commit, PR, and review rules.
14. **Project MCP servers:** servers in `.mcp.json`, and whether `.claude/settings.json` or `.claude/settings.local.json` turns them on without a prompt (`enableAllProjectMcpServers`, `enabledMcpjsonServers`). MCP servers run outside the sandbox, so their tools can build, run, write files, or reach the network for the audit model. An Xcode MCP server, for example, can build and run the app.

For a large repo, hand the breadth sweep (items 2, 4, 7, 8, and the harness search in 10) to an Explore subagent with a precise list of what to return. Read the critical files yourself: auth middleware, tenancy guard, webhook handlers, encryption.

## 3. Choose attacker goals

Use [attack-catalog.md](attack-catalog.md). Pick the 5 to 9 goals that fit this repo and rewrite each in this repo's terms, naming:

- the real actors (stranger, free user, paying tenant, another household, a malicious package consumer),
- the real assets (which API keys, which PII, which printers or devices),
- the real features and files.

Drop catalog items that don't apply, order by risk, and add anything specific to this repo that the catalog lacks. Fold open code-scanning alerts into the goal they belong to, as leads to prove or dismiss. If a focus was given, put most goals inside that area, but keep enough of the surrounding map to find paths into it.

## 4. Write the audit prompt

Fill in [prompt-template.md](prompt-template.md).

- Write the opening line from step 1.
- Keep the scope and rules section, adapting the forbidden commands, secret files, production hosts, and third-party list to this repo. For third-party testing, limit the scope to the engagement's scope.
- The read-first list should hold at most 8 docs, all relevant to security.
- Name the exact test framework, where new tests go, the test to copy, what to mock, and the run command:
  - Place new tests by the repo's convention (next to the code or in its test directory), so imports and the runner's config work, with a `cvp` marker in the file name so they're easy to find: `*.cvp.test.ts`, `test_cvp_*.py`, `*_cvp_test.go`, `CVP*Tests.swift`, and so on. Name a separate location for each test environment, such as DOM versus node.
  - Proof tests fail by design, so none may stay in the source tree, where a commit would turn CI red. The output contract at the end of the prompt says where everything goes, as an end state rather than a step, so it holds even when no test ever runs in the source tree: each test, helper, and fixture at `docs/security/tests/<the repo-relative path it would run from>.disabled`, for example `docs/security/tests/src/auth/session.cvp.test.ts.disabled`. The suffix keeps test runners, type checkers and linters from picking it up, and restoring it is a single `mv`. Give one example path from this repo.
  - Fill the contract's `{TOOLED_EXTENSIONS}` from recon item 10, and its `{CONTRACT_CHECK}` with the real report path, as [prompt-template.md](prompt-template.md) describes. Don't restate the contract elsewhere in the prompt.
  - Name the existing test whose mocking to copy. Say plainly when tests have no database or cache.
  - Tell the audit model to mock the libraries from recon item 7 that call the network during verification.
  - Give the exact single-file run command for each package or workspace, including project or workspace flags.
  - If there's no harness, tell the audit model to use the language's built-in runner (`node --test`, `python -m unittest`, `go test`, `cargo test`, `swift test`) in a `security-tests/` directory without adding dependencies. The contract covers those tests too.
  - When the project file lists sources explicitly, say how to add and remove a test file, as the `{TEST_SETUP}` note describes.
  - If tests bind localhost ports or spawn servers, say they may fail in the sandbox and to call handlers in-process where it can.
  - For an Apple app whose only harness is `xcodebuild`, prepare the audit model in `{TEST_SETUP}` for the method's alternative-harness fallback, so it works whichever launch line the user picks. With the optional Apple launch line from step 6, `xcodegen generate` and `xcodebuild build-for-testing -derivedDataPath "$TMPDIR/cvp-derived-data" 'OTHER_SWIFT_FLAGS=$(inherited) -disable-sandbox'` work in the sandbox, which shows a test compiles in the real project. That flag turns off only the compiler's own sandbox for macro plugins, which fails when nested inside this one. Without that line, both fail with permission errors. Either way, no `xcodebuild test` run works in the sandbox, because the simulator and `testmanagerd` are out of reach, so tests run through an alternative harness such as `swiftc` plus `xcrun xctest` on macOS. Give the `xcodebuild test` command for the real project too; the report repeats it for each proof, and the fix session runs it.
- Include the retest section only if earlier findings exist, and the dependency section only if there are open alerts.
- Report path: `docs/security/<date>-security-cvp-audit.md`, with `-2`, `-3`, and so on if that file exists. The name doesn't end in `-security-audit`, so `/security-audit` doesn't take it for one of its own reports.
- Aim for 60 to 110 lines. Include only what the audit model needs, with no commentary about this recon. Go longer only when surfaces share auth or sessions and must be audited together (for example an app and an admin dashboard that share a session cookie), and say why in the warnings.
- If the repo has several large, independent surfaces (more than about three deployable apps), write one prompt per surface instead of one giant prompt.
- Before saving, check that every path the prompt cites exists.

## 5. Write the fix prompt

Fill in [fix-prompt-template.md](fix-prompt-template.md) with the report path, the contract check, the tooled extensions, the ignore lines step 6 chooses, the test naming and run commands from step 4, and, from recon, the integration branch, the full check commands, whether the project file lists sources explicitly, and the repo's commit, PR, review, and security-tracking rules. For several surfaces, write one fix prompt that covers every report.

## 6. Deliver

1. Make sure git ignores the audit's files, so the report and archived tests can't be committed. Unless recon's `git check-ignore` showed rules already cover all three paths, append to the file `git rev-parse --git-path info/exclude` prints, creating it if needed:
   - If git tracks no files under `docs/security/`, add `/docs/security/` on its own line. It also keeps other new files there, such as `/security-audit` and `/security-scan-dependencies` reports, out of commits from this clone, and the reply says so.
   - If git tracks files there, the repo commits that folder, so ignore only the audit's own paths, each on its own line: `/docs/security/*cvp*audit*`, `/docs/security/tests/` and `/docs/security/harness/`. Skip any a rule already covers.

   Use that command rather than `.git/info/exclude`, because in a linked worktree `.git` is a file. The exclude file is never committed and applies to every worktree of the clone, so nothing in the repo hints at the audit's files. Don't edit `.gitignore`. Expect an approval prompt for the write. Without git, write nothing; the checklist covers it.
2. Save the audit prompt to `~/.claude/cvp-audit-prompts/<repo-name>-<date>.md` and the fix prompt to `~/.claude/cvp-audit-prompts/<repo-name>-<date>-fix.md`, creating the directory if needed. For several surfaces, add a surface suffix to each audit prompt. Don't overwrite an earlier file; add `-2`, `-3`, and so on. Claude Code protects `~/.claude/`, so expect an approval prompt for these writes (in auto mode, the classifier reviews them).
3. Copy the audit prompt to the clipboard with the first of these that exists: `pbcopy`, `wl-copy`, `xclip -selection clipboard`, `clip.exe` (for example `pbcopy < <file>`). Note which one worked, because the fix checklist uses it too. If none exists or the copy fails, skip it, and the audit checklist tells the user to open the file instead.
4. Reply in the format below and nothing else. Don't print either prompt: the files hold them, and the user opens or edits them there. Fill in every `<...>` and drop the lines that don't apply.

````markdown
**Audit prompt:** `~/.claude/cvp-audit-prompts/<repo-name>-<date>.md` (<copied to the clipboard | not copied: no clipboard tool>)
**Ignore rule:** <added `/docs/security/` to `.git/info/exclude`, which also keeps other new files there, such as `/security-audit` reports, out of commits from this clone | added the audit's own paths to `.git/info/exclude`, because git tracks files in `docs/security/` | already ignored by <file:line from git check-ignore -v> | no git yet, see the checklist>

### Audit checklist

**Before launching**, outside the sandbox:
- `<install command>`, so the sandboxed session doesn't need the network <only if dependencies are missing>
- `<rebuild command>` <only if recon found a stale workspace build>
- `git status` → clean. Commit any other work first, so that afterwards `git status` shows only what the audit changed

**Launch**
```bash
cd <repo_root>
claude --model <audit-model-id> --permission-mode auto --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false,"failIfUnavailable":true}}'
```
These settings last this session only, and the repo's own `.claude/` settings can't loosen them.

<only for an Apple app whose only harness is xcodebuild:> Optional: to let `xcodegen` and `xcodebuild` builds work in the sandbox, launch with this line instead. It adds one writable folder, the per-user temp folder that every app you run shares. Test runs stay blocked either way.
```bash
claude --model <audit-model-id> --permission-mode auto --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false,"failIfUnavailable":true,"filesystem":{"allowWrite":["<getconf DARWIN_USER_TEMP_DIR output>"]}}}'
```

**In the session**
1. The status bar shows `⏵⏵ auto mode on`. If it doesn't, this model may not offer auto mode: quit and relaunch with `--permission-mode acceptEdits`
2. `/status` → "Setting sources" includes "Command line arguments". Skip `/sandbox`: the launch line already turned on the sandbox, auto-allow and strict mode
3. Ask Claude to run `touch ~/sandbox-probe`. Expect `Operation not permitted` (macOS) or `Read-only file system` (Linux, WSL2). If it succeeds, delete the file and quit: a settings file is widening the sandbox, so check `sandbox` in `~/.claude/settings.json`
4. Run `/mcp` and disable <servers>. MCP tools run outside the sandbox <only if recon item 14 found project MCP servers that start without a prompt>
5. Paste the audit prompt from the clipboard <if it wasn't copied: "Open the audit prompt file, copy all of it, and paste it">
6. Network: deny anything you can't explain. Allow package registries only if an install is unavoidable. In auto mode a command names the hosts it needs instead of prompting, so stop the session if one names a host you can't explain
7. When it finishes, `git status` should list nothing, and `<the contract check>` should print nothing. If either prints anything, the fix prompt's first step normalizes it

**Fix prompt:** `~/.claude/cvp-audit-prompts/<repo-name>-<date>-fix.md`

### Fix checklist

Once the audit session has finished (its report should be at `docs/security/<date>-security-cvp-audit.md`):
1. Quit the audit session
2. Start a normal, unsandboxed session on an Opus-class model, so it can run the full checks, `gh` and CI:
   ```bash
   cd <repo_root>
   claude --model opus
   ```
3. Run `<clipboard tool> < ~/.claude/cvp-audit-prompts/<repo-name>-<date>-fix.md` and paste the fix prompt <if there's no clipboard tool: "Open the fix prompt file, copy all of it, and paste it">
4. It re-runs each proof test, shows a triage table and asks which findings to fix. Commits, pushes and PRs wait for your OK

### Warnings
- <each warning from recon>
- These files map the repo's attack surface: both prompts now, and later the report and archived tests in `docs/security/`. Don't commit them or post them publicly.
````

- Keep the launch line on one line, exactly as above apart from the model ID. The optional Apple line differs only by its `filesystem.allowWrite` entry, which holds the path `getconf DARWIN_USER_TEMP_DIR` printed during recon. Without `--model`, write `<audit-model>` in place of the ID, and add after the code block: "Pick the strongest model your account offers for security work (`/model` lists them)."
- Without git, replace the `git status` item with: run `git init`, add `/docs/security/` to `.git/info/exclude`, and make a baseline commit, so the audit's files can't be committed, `git status` can show what the audit changed, and the fix prompt's branch steps work.
- For several surfaces, give each audit prompt its own **Audit prompt** line, naming its surface. Each one gets its own audit session with the same checklist. The clipboard holds the first prompt, and step 5 says to copy each of the others with `<clipboard tool> < <file>` before pasting it.
- Always end the warnings with the attack-surface warning. Recon warnings come first, for example:
  - tests need a database or cache, which the prompt tells the audit model to mock;
  - only `xcodebuild` is available (plus XcodeGen, if present): the strict sandbox blocks it entirely unless the optional Apple launch line is used, and blocks every `xcodebuild` test run even then. The prompt lets the audit model fall back to an alternative harness, and the fix session reruns those proofs through the real project;
  - project MCP servers start without a prompt (name them): disable them with `/mcp` before pasting the prompt, because their tools run outside the sandbox;
  - a committed secret, by path and line;
  - Dependabot or code scanning is disabled (HTTP 403);
  - a workspace build is stale and must be rebuilt before launch;
  - tests bind localhost ports or spawn servers and may fail under strict sandbox mode;
  - the prompt runs past 110 lines because surfaces share auth or sessions;
  - git already tracks files at the audit's own paths (list them): the ignore rule covers only new files, and `git rm --cached <path>` stops tracking each one on the next commit while keeping the local copy;
  - git tracks files under `docs/security/`, but an earlier run's `/docs/security/` line already ignores the whole folder (give its file:line): new files there, such as `/security-audit` reports, can't be committed from this clone. Replace that line with `/docs/security/*cvp*audit*`, `/docs/security/tests/` and `/docs/security/harness/`;
  - local secret files such as `.env` exist: the sandbox covers shell commands only, and Claude's Read tool follows permission rules, so add deny rules for those files before launching.
