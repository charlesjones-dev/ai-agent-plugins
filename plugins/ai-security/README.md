# AI-Security

Security tools for reviewing your code, planning a sandboxed audit on a stronger model, checking a live website, and protecting your development setup.

## Quick start

Install from this marketplace:

```text
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-security@ai-agent-plugins
```

Then open the repository you want to review and run:

```text
/ai-security:security-audit
```

To review a smaller part of the project, describe the scope:

```text
/ai-security:security-audit ./server — exclude generated files
```

## Choose a command

| Command | Use it to… |
| --- | --- |
| `/ai-security:security-audit` | Review source code and save a report explaining possible problems, supporting evidence, and suggested fixes. |
| `/ai-security:security-cvp-audit` | Plan an audit for a sandboxed session on a stronger model that proves each finding with a failing test, plus a prompt for verifying and fixing what it proves. Takes an optional focus and `--model <audit-model-id>`. |
| `/ai-security:security-scan-dependencies` | Check a live website for visible outdated libraries, known vulnerabilities, and browser protection settings. Pass the URL and scope, or it asks for them. |
| `/ai-security:security-init` | Set up Claude Code file-access rules for sensitive files such as credentials and environment files. |
| `/ai-security:security-supply-chain` | Configure a pnpm project to delay installing newly published packages and keep automated builds aligned with its lockfile. |

Some hosts also expose shorter aliases such as `/security-audit`.

The two setup commands show proposed configuration changes for approval. After using `security-init`, restart Claude Code for its settings to take effect; this step is optional and is not required to run an audit. The supply-chain command checks pnpm compatibility before making changes.

## What to expect from an audit

By default, the audit reviews the current repository, including application code, background jobs, configuration, and dependencies. It checks suspected problems against the code and uses small local tests where practical. Live infrastructure, vendor dashboards, and setting up a full test environment are not required unless you request that scope.

Reports are saved inside your repository:

```text
docs/security/YYYY-MM-DD-HHMMSS-security-audit.md
docs/security/YYYY-MM-DD-HHMMSS-security-audit.json
```

Git treats them like any other new file, so committing them is up to you. They describe weaknesses in your code, so think before committing them to a public repository. In a clone where `/security-cvp-audit` added `/docs/security/` to `.git/info/exclude`, git ignores them; see [What it writes](#what-it-writes).

Start with the Markdown summary and table of contents, then jump to the findings you need. The matching JSON keeps the full evidence and commands for deeper review or automation. Reports explain:

- **What was reviewed** and which areas still need attention.
- **Confirmed problems**, their likely impact, and recommended next steps.
- **Uncertain concerns** separately from confirmed problems and optional improvements.
- **Changes since a previous audit**, when a previous report is selected or supplied.

The audit uses at most two reviewers at a time by default and closes its workers when they finish. If the host cannot manage workers reliably, the main assistant does the review itself. Reviewers contribute evidence to one final report, not separate reports for you to sort through.

You can ask the audit to compare against a specific report:

```text
/ai-security:security-audit compare against docs/security/<previous-report>.md
```

**Complete** means the agreed review work is finished. It can still say **follow-up remains** when a concern needs a production setting or vendor fact that the code cannot answer. Those concerns stay visible with next steps. **Partial** means actual review work is unfinished, such as unread routes or required tests that were skipped. Saving a report is not a reason to stop while useful, authorized checks remain.

A finding disappearing from a report does not mean it was fixed; the comparison should explain what happened to it. Suggested fixes still need review and testing.

Python 3.9+ is needed for automatic report checking and formatting. If it is unavailable, the assistant can produce a partial report and explain which checks were skipped.

## Planning a sandboxed audit

`/security-cvp-audit` plans a security audit for a separate, sandboxed session, so the strongest model you can use spends its time finding and proving bugs instead of learning the repo. Use it only on code you own or are authorized to test.

It reads the repo, makes sure git ignores the audit's files under `docs/security/`, and writes two prompts and a checklist:

- **An audit prompt** to paste into a new, sandboxed Claude Code session. It names this repo's attacker goals, files, banned commands, secret paths, production hosts and test commands.
- **A launch checklist** for that session: dependencies, a clean working tree, a one-line launch that turns on auto mode and a strict sandbox, and a probe that confirms the sandbox is on.
- **A fix prompt** for phase 3, which verifies each finding and fixes the ones you pick.

CVP refers to [Anthropic's Cyber Verification Program](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet), which gives qualifying security teams, open-source maintainers and researchers advanced cyber capabilities with fewer blocked requests. You don't need to be enrolled. The skill asks what authorizes the audit and writes only that into the prompt.

### Which audit to use

- `/security-audit` runs the audit in the current session and keeps Markdown and JSON reports that track findings across runs.
- `/security-cvp-audit` plans an audit for a sandboxed session on a stronger model, which proves each finding with a failing test, and a separate session that fixes the findings you pick.
- Claude Code's built-in `/security-review` checks the pending changes on your branch.

### The three phases

| Phase | Where it runs | Model tier | Sandboxed? | Network? | Output |
|---|---|---|---|---|---|
| 1. Plan (`/security-cvp-audit`) | A normal Claude Code session in the repo | Planning model: Opus-class | No | Only optional `gh` reads of GitHub alerts | Audit prompt, launch checklist and fix prompt, saved to `~/.claude/cvp-audit-prompts/`, plus a local ignore rule for the audit's files |
| 2. Audit | A new session in the repo, launched in auto mode with a strict sandbox | Audit model: the strongest security-capable model you can use | Yes, strict | None. Third-party services are mocked | A report in `docs/security/`, one failing proof test per finding, archived as a `.disabled` file under `docs/security/tests/`, and any alternative-harness scripts and logs in `docs/security/harness/`. Nothing is fixed or committed |
| 3. Fix | A normal session in the repo | Fixing model: Opus-class | No | Yes, for GitHub, CI and deploys, plus read-only provider checks you approve | Verified findings, a fix per change you pick with its proof test restored as the regression test, and an updated report |

Opus-class means the current Opus model or one at least as capable (as of October 2026, Claude Opus 5.5). The audit model can be any model your account offers; some with stronger security capabilities require enrollment in the Cyber Verification Program.

### How the plan works

1. Classifies the project (web app or API, Apple app, library, CLI or Claude Code plugin, Home Assistant integration, static site) and works out the owner from LICENSE, the manifest and the remote
2. Asks what authorizes the audit: enrollment in the Cyber Verification Program, ownership or maintenance of the code, or an authorized third-party engagement. It never claims enrollment you didn't state
3. Does read-only recon: entry points, auth and tenancy, untrusted-input sinks, billing, secrets (names only), integrations, CI and supply chain, deploy config, the test harness, earlier audits and project MCP servers. Earlier audits include the newest `/security-audit` report, whose findings it sorts into a retest list, open findings not to re-report, and items to settle. With `gh` signed in, it also reads open Dependabot and code-scanning alerts. On a large repo, a read-only Explore subagent does the breadth sweep while the skill reads the auth, tenancy, webhook and encryption code itself
4. Picks 5 to 9 attacker goals from [`attack-catalog.md`](skills/security-cvp-audit/attack-catalog.md) and rewrites each in the repo's own actors, assets and files
5. Fills in [`prompt-template.md`](skills/security-cvp-audit/prompt-template.md): the rules for this repo, up to 8 files to read first, the goals, a retest section for earlier findings, open alerts, and how to prove each finding. That means the test framework, a file name with a `cvp` marker placed by the repo's convention, an existing test whose mocking to copy, the libraries to mock, the single-file run command for each package, and an output contract: where the report, each test and any harness files end up, plus a check the audit runs before it finishes. It checks that every path it cites exists
6. Fills in [`fix-prompt-template.md`](skills/security-cvp-audit/fix-prompt-template.md) for phase 3
7. Adds the ignore rule to `.git/info/exclude` unless git already ignores the audit's files, saves both prompts outside the repo, copies the audit prompt to the clipboard, and replies with the path to each prompt, a checklist for the audit session and one for the fix session, and any warnings, such as a stale workspace build or tests that bind localhost ports. It doesn't print the prompts; open the files to read or edit them

```text
/ai-security:security-cvp-audit
/ai-security:security-cvp-audit billing
/ai-security:security-cvp-audit src/auth --model <audit-model-id>
```

The focus is optional: an area or a path. Most goals then land there, with enough of the surrounding map to find paths in. `--model` fills in the launch line. Without it, the checklist says `claude --model <audit-model>`, and you pick the strongest model your account offers for security work (`/model` lists them).

### Phase 2: run the audit

Follow the printed checklist. In short:

1. Outside the sandbox, install dependencies and check that `git status` is clean
2. Start the audit session in the repo with the checklist's launch line:
   ```bash
   claude --model <audit-model-id> --permission-mode auto --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false,"failIfUnavailable":true}}'
   ```
3. Check that the status bar shows `⏵⏵ auto mode on`, and that `/status` lists `Command line arguments` under setting sources
4. Ask Claude to run `touch ~/sandbox-probe`. It should fail with `Operation not permitted` on macOS, or `Read-only file system` on Linux and WSL2
5. Paste the prompt, and deny any network access you can't explain
6. When it finishes, check that `git status` lists nothing and that the checklist's `find` check prints nothing

The launch line replaces the `/sandbox` panel. Its settings last for that session only and write no file:

- `enabled` turns on the sandbox.
- `autoAllowBashIfSandboxed` runs sandboxed commands without prompts (auto-allow).
- `allowUnsandboxedCommands: false` turns on strict sandbox mode, so Claude can't retry a blocked command outside the sandbox. Set this way, it also makes the sandbox admin-required (Claude Code v2.1.285 or later): Claude Code ignores the repo's own `.claude/settings.json` and `.claude/settings.local.json` entries that would loosen it, such as `excludedCommands`, `allowWrite` and `allowedDomains`.
- `failIfUnavailable` makes Claude Code exit at startup if the sandbox can't start, instead of running commands unsandboxed.

For an Apple app whose only harness is `xcodebuild`, the checklist also offers an optional launch line that adds the per-user temp folder (`getconf DARWIN_USER_TEMP_DIR`) to `sandbox.filesystem.allowWrite`. Foundation writes its temp files there rather than in `$TMPDIR`, so without it `xcodegen` and `xcodebuild` fail before compiling. With it, `xcodegen` and `xcodebuild build-for-testing` work, given DerivedData under `$TMPDIR` and `-disable-sandbox` for the compiler's macro plugins. `xcodebuild test` still doesn't, because the simulator and `testmanagerd` are out of reach. The extra folder is shared by every app you run, which is why the line is optional.

`/sandbox` won't open in that session, because command-line settings outrank the file it saves to. If you use [ai-statusline](../ai-statusline/), turn on its sandbox indicator to see when your settings turn the sandbox on.

The audit model maps the attack surface, hunts each goal, proves each finding with a failing test, and writes a report. It doesn't fix anything or commit. The prompt ends with an output contract that describes the end state rather than steps, so it holds however the runs went:

- the report at the exact path the prompt names;
- each test, helper and fixture at `docs/security/tests/<path it runs from>.disabled`, whether or not it ever sat in the source tree;
- anything else it keeps, such as alternative-harness scripts and run logs, in `docs/security/harness/`, with no extension the repo's compiler, test runner, formatter or linter picks up;
- build staging in a temp folder outside the repo.

Before it finishes, the audit model runs a `find` check against that layout and `git status`. The check skips `/security-audit` and `/security-scan-dependencies` reports, so running either while the audit is under way doesn't trip it. If the sandbox blocks the repo's own test command, the audit model may build an alternative harness, but a result counts as Confirmed only if the test would also compile and run unchanged in the real project, and the report gives the command that runs it there.

### Phase 3: verify and fix

Once the report is written, quit the audit session, start a normal, unsandboxed session on an Opus-class model (`claude --model opus`), and paste the fix prompt (`<repo>-<date>-fix.md`). The reply's fix checklist gives the command that copies it to the clipboard. The fix session:

- checks the audit's files against the output contract first, moves anything misplaced (a misnamed report, live test files, harness files with source extensions) into the expected layout, and tells you what moved;
- re-runs each Confirmed proof test outside the sandbox and downgrades any that don't fail for the reason the report gives;
- runs the tests the sandbox kept from running through the real project, checks that each one actually ran, and tries to settle Unconfirmed findings with local tests, never real servers;
- proposes exact checks for what code alone couldn't settle (dashboards, CLIs, provider settings), and runs read-only ones only with your OK;
- shows a triage table (ID, severity, verified, effort, proposed grouping) and asks which to fix;
- fixes each pick on a branch from your integration branch, moves its archived proof test back into place (dropping `.disabled`) as the regression test, and runs the full test suite, lint and typecheck;
- never commits anything under `docs/security/`, and updates the report with each finding's status, date, commits or PR, and how it was verified.

Commits, pushes and PRs wait for your consent. When the fixes have merged, run `/security-cvp-audit` again. Its recon finds the updated report and adds a retest section for the fixed IDs.

### Why plan outside the sandbox

- **The audit model's budget goes to finding and proving bugs.** Orientation runs here, on a cheaper model plus a read-only subagent.
- **The guardrails are written before an unattended run starts.** Banned commands, secret paths and production hosts are set for this repo before the auto-mode session begins. You can read and edit them first, and the audit model doesn't set its own limits.
- **Steps that need network or credentials stay outside.** GitHub alert reads happen in phase 1, so the sandboxed session never needs your tokens.
- **Earlier audits arrive sorted.** Fixed findings become a retest list, open ones aren't re-reported, and needs-investigation items get settled, so the audit doesn't rediscover known findings.
- **The prompt is a saved file.** You can review it, edit it, rerun it and compare it across audits.
- **Finding and fixing happen in separate sessions.** The fixing session re-checks each finding before changing code, and only an unsandboxed session can push branches, open PRs and watch CI and deploys.

### Trade-offs

- The chosen goals can anchor the audit model on what recon noticed. The prompt's method still requires a full attack-surface map before hunting, which offsets this.
- The prompt goes stale as the code changes. If the code has moved since you generated it, run the skill again.
- If budget doesn't matter, a short prompt with only the rules may find more bugs off the map.

### Requirements

- **Claude Code v2.1.285 or later, with the sandbox and auto mode.** Earlier versions let the audited repo's own settings loosen a sandbox set on the command line. The sandbox runs on macOS, Linux and WSL2. Linux and WSL2 also need `bubblewrap` and `socat`. On native Windows, Claude Code runs commands unsandboxed, so run the audit in WSL2. Auto mode needs a supported model, and an organization admin can turn it off. If your audit model doesn't offer auto mode, launch with `--permission-mode acceptEdits` instead; auto-allow still runs sandboxed commands without prompts. Managed settings outrank `--settings`, so if your organization sets the sandbox keys, theirs apply.
- **Access to a strong audit model.** Some require enrollment, such as models offered through the Cyber Verification Program.
- **`gh`, optionally,** signed in, to include open Dependabot and code-scanning alerts.
- **Dependencies installed before launch,** so the sandboxed session doesn't need the network.

### What it writes

| File | Written in | Contents |
|---|---|---|
| `~/.claude/cvp-audit-prompts/<repo>-<date>.md` | Phase 1 | The audit prompt. Repos with more than about three independent deployables get one prompt per surface, with a suffix |
| `~/.claude/cvp-audit-prompts/<repo>-<date>-fix.md` | Phase 1 | The fix prompt for phase 3 |
| `.git/info/exclude` | Phase 1 | The ignore rule described below, unless git already ignores the audit's files |
| `docs/security/<date>-security-cvp-audit.md` | Phase 2 | The audit report |
| `docs/security/tests/<path>.disabled` | Phase 2 | One proof test per finding, stored under the repo-relative path it runs from, with `cvp` in its file name |
| `docs/security/harness/` | Phase 2 | Only if the audit needed an alternative harness: its scripts and run logs |

Phase 1 doesn't change any file git tracks. Claude Code protects `~/.claude/`, so expect an approval prompt for the prompt files (in auto mode, the classifier reviews them instead).

These files are sensitive. They map your attack surface: entry points, weak spots to try, where secrets live and which hosts are production. Don't commit them, and don't post them in issues, chats or gists.

Git ignores the audit's files, so the report and tests stay local, even in an open-source repo. The rule goes in `.git/info/exclude` rather than `.gitignore`, so it's never committed and nothing in the repo hints at the files. It applies to this clone and all its worktrees. If you copy the files into another clone, add the rule there too. The rule depends on whether your repo already commits files in `docs/security/`:

- **Git tracks nothing there:** the rule is one `/docs/security/` line. It also keeps other new files in that folder out of commits from this clone, including `/security-audit` and `/security-scan-dependencies` reports, and the reply says so. To commit one of those anyway, use `git add -f`, or replace the line with the three below.
- **Git tracks files there:** the repo commits that folder, so the rule covers only the audit's own paths: `/docs/security/*cvp*audit*`, `/docs/security/tests/` and `/docs/security/harness/`. Your other reports stay committable. If an earlier run already added `/docs/security/`, the warnings say to replace it with these.

Files git already tracks at the audit's paths stay tracked, and the skill lists them in its warnings.

Proof tests fail by design, so the audit doesn't leave one in the source tree, where a commit would turn CI red. The `.disabled` suffix keeps the usual test, type-check and lint patterns from matching the archived copies. Most of those tools don't read git's ignore rules, so a live source file anywhere under `docs/security/` could still be compiled, formatted or linted, and the contract allows none. Each one keeps its original path, so the fix session restores it with a single `mv` once its fix is in.

### Authorization and safety

- Use this only on code you own or are authorized to test. The skill asks what authorizes the audit and writes only that into the prompt. It doesn't claim Cyber Verification Program enrollment unless you say you're enrolled, and it stops if you have no authorization.
- The audit prompt limits scope to this repository, bans network requests to production and third parties, requires every third-party service to be mocked, and forbids changing application code, committing and switching branches.
- Recon in phase 1 is read-only. It doesn't run the app, tests, builds, installs or anything that loads secrets, and it cites a committed secret by path and line, never by value. Phase 1 changes no file git tracks. Its one write inside the repo is the ignore rule in `.git/info/exclude`.
- MCP servers run outside the sandbox. Recon flags project MCP servers that start without a prompt, the checklist says to turn them off with `/mcp` before pasting the prompt, and the audit prompt tells the audit model not to call MCP tools.
- Strict sandbox mode stops Claude from retrying a blocked command outside the sandbox. The sandbox covers shell commands only: Claude's Read, Edit and Write tools follow your permission rules instead, and sandboxed commands can read most of your machine by default. Add deny rules for secret files before launching (`/security-init` in this plugin writes them), and see `sandbox.credentials` in the [sandboxing docs](https://code.claude.com/docs/en/sandboxing).

## Scanning a website

Pass the URL and a scope after the command:

```text
/ai-security:security-scan-dependencies https://example.com all
/ai-security:security-scan-dependencies example.com frontend,headers
```

The scope is one or more of `frontend`, `cms`, `headers` and `all`. The command asks for whatever you leave out. With both supplied it asks nothing, so scheduled or headless runs should pass both; an unattended run given only a URL scans everything. The report is saved to `docs/security/YYYY-MM-DD-HHMMSS-dependency-scan.md`.

## Limits

Results depend on the available code, tools, and review time. Audits can miss problems or make mistakes, and they do not certify compliance or guarantee an identical result on every run. Use them alongside your existing tests, dependency scanners, and security reviews.

A website scan sees what the site exposes publicly; it cannot establish the security of private server code or infrastructure.

## Updating and automation

Source edits do not update an installed plugin. Once a new version is available through your configured marketplace, refresh the marketplace, update the plugin, and reload plugins or start a new session as your host requires.

**Coming from ai-cvp:** ai-cvp's `/cvp-defense-audit` is now `/security-cvp-audit` in this plugin, and the ai-cvp plugin is removed. Claude Code users who only had ai-cvp run `/plugin install ai-security@ai-agent-plugins` once. New reports are named `<date>-security-cvp-audit.md`, and recon still reads earlier `<date>-cvp-security-audit.md` reports. Saved prompts stay in `~/.claude/cvp-audit-prompts/`.

**Upgrading from 1.x:** Version 2.0 changes the audit report format. New reports use JSON schema 1.1; existing schema 1.0 reports keep their original completion rules. See the [report format guide](skills/security-audit/references/artifacts.md). Automations that previously launched the `security-auditor` helper directly should invoke `/ai-security:security-audit` for a complete audit.

## Detailed guidance

- [Audit workflow](skills/security-audit/SKILL.md) and [review methodology](skills/security-audit/references/methodology.md)
- [Report format and tools](skills/security-audit/references/artifacts.md)
- [Sandboxed audit planning](skills/security-cvp-audit/SKILL.md), its [attack catalog](skills/security-cvp-audit/attack-catalog.md), and the [audit](skills/security-cvp-audit/prompt-template.md) and [fix](skills/security-cvp-audit/fix-prompt-template.md) prompt templates
- [Website scanning](skills/security-scan-dependencies/SKILL.md)
- [Claude Code file-access setup](skills/security-init/SKILL.md)
- [pnpm supply-chain setup](skills/security-supply-chain/SKILL.md)

**Version:** 3.0.0 · **Author:** Charles Jones · **License:** [MIT](../../LICENSE)
