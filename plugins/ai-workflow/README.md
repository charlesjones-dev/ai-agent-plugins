# AI-Workflow Plugin

Runs preflight code quality checks, ships a change as commit, push and PR, babysits a branch through Claude Code, Codex and Cursor Bugbot review, merge and deploy to production, sets up the Claude Code GitHub Actions on the newest Opus, generates a Development Principles section, and manages curated CLAUDE.md behavior rules.

> **Removed skills (July 2026):** `/workflow-plan-phases` and `/workflow-implement-phases` were removed because Claude Code ships **Dynamic Workflows** natively (a JavaScript runtime that orchestrates subagent fan-out with per-agent token budgets), which supersedes manual phase planning/orchestration. They're still available in git history.

---

## Available Skills

### `/workflow-principles`

Generate a context-aware Development Principles section for your CLAUDE.md, tailored to your project's structure and tech stack.

**What it does:**

- Auto-discovers project structure (monorepo vs single, workspace packages, shared modules)
- Detects tech stack (languages, frameworks, validation libs, state management, testing tools)
- Asks which principle categories to include
- Generates principles using real package names, paths, and library names from your project
- Supports monorepo-specific rules (shared package conventions, dependency direction, cross-package contracts)
- Supports frontend component architecture rules (isolation, composition, state management)
- Appends to an existing CLAUDE.md, or replaces or merges an existing principles section
- Writes to project CLAUDE.md or user-level ~/.claude/CLAUDE.md

**Usage:**

```
/workflow-principles
```

**Principle Categories Available:**

| Category | What It Covers |
|----------|---------------|
| SOLID Principles | SRP, OCP, LSP, ISP, DIP - tailored to your stack |
| DRY / Code Reuse | No duplication, shared code rules, import-first |
| KISS / Simplicity | Simplest correct solution, avoid premature abstraction |
| YAGNI / Scope Discipline | Only build what's requested, ask before extras |
| Modularity & Coupling | Package boundaries, dependency direction, loose coupling |
| Component Architecture | Component isolation, composition, prop/state rules |
| Type Safety & Contracts | Strict typing, shared types, API contracts |
| Error Handling | Error boundaries, structured errors, graceful degradation |
| Testing Philosophy | Test behavior, integration over mocking, edge cases |
| Git Workflow | Commit consent, doc review before commits, branch conventions |

### `/workflow-rules`

Add, remove, or list curated **behavior rules** in CLAUDE.md: short instructions that correct repeated Claude Code annoyances (PR padding, fabricated test plans, "Generated with Claude Code" footers, internal-deliberation narration).

> **Rules vs. Principles:** `/workflow-rules` controls **how Claude behaves** (communication style, PR/commit hygiene, scope discipline) and is cross-project, picked from a curated library. `/workflow-principles` controls **how code is written in this project** (SOLID, DRY, testing philosophy) and is generated from project discovery. Use `/workflow-rules` when you keep correcting Claude on the same thing across every project; use `/workflow-principles` when you want project-specific coding standards.

**What it does:**

- Reads the curated rule library shipped with the plugin
- Picks target file: user `~/.claude/CLAUDE.md` (default, applies everywhere) or project `./CLAUDE.md`
- Cross-platform path resolution (Windows `%USERPROFILE%\.claude\CLAUDE.md` and POSIX `~/.claude/CLAUDE.md`)
- Multi-select picker grouped by section, with already-installed rules filtered out
- Wraps each installed rule in HTML comment markers (`<!-- workflow-rules:id=... -->`) so adds are idempotent and removes are precise, even if you edit the rule's title later
- Shows a unified diff before any write and requires explicit confirmation

**Usage:**

```
/workflow-rules
```

**Modes (chosen interactively):**

- **Add**: install one or more curated rules into the chosen CLAUDE.md
- **Remove**: uninstall previously-installed rules (matched by ID, not title)
- **List**: show what's currently installed and where

**Rule library:**

| Section | Rules |
|---------|-------|
| PR and Commit Hygiene | Scope to current session, no fabricated test plans, no speculative deploy steps, short PR bodies, scoped commit messages, no "Generated with Claude Code" footers |
| Scope Discipline | No unrequested features, confirm before risky/shared-state actions |
| Communication Style | No internal-deliberation narration, match response length to task |

**Before (manual fixes every project):**

```
# Edit ~/.claude/CLAUDE.md by hand
# Copy-paste the same rules into every new project
# Forget which corrections you already wrote down
```

**After (with workflow-rules):**

```
/workflow-rules
# Pick "Add rules to CLAUDE.md"
# Pick user-level (applies everywhere) or project-level
# Multi-select the rules you want
# Review diff, confirm
```

### `/workflow-preflight`

Run code quality checks before commits, PRs, or deployments.

**What it does:**

- Auto-detects configured quality tools across ecosystems
- Runs checks in this order: typecheck -> lint -> format check -> security -> tests
- Detects security tools: pnpm/npm/yarn audit, eslint-plugin-security, Semgrep
- Finds Semgrep through package.json scripts, config files, CI workflows, or README docs, with a Docker fallback
- Reports each check as pass, warning, or fail
- Offers interactive fix mode (or use `--fix` for automatic)
- Respects existing project scripts (uses `npm run lint` over raw `eslint`)

**Usage:**

```
/workflow-preflight                  # Interactive mode (default)
/workflow-preflight --fix            # Auto-fix all fixable issues
/workflow-preflight --check-only     # Report only, no fixes
/workflow-preflight --verbose        # Show detailed output
```

**Supported Ecosystems:**

| Ecosystem | Type Check | Lint | Format | Security | Test |
|-----------|------------|------|--------|----------|------|
| **Node.js/TypeScript** | tsc | ESLint, Biome | Prettier | pnpm/npm/yarn audit, eslint-plugin-security, Semgrep | Jest, Vitest |
| **Python** | MyPy | Ruff | Black, Ruff | pip-audit, safety, Semgrep | Pytest |
| **.NET** | dotnet build | Analyzers | dotnet format | Semgrep | dotnet test |
| **Go** | go build | golangci-lint | gofmt | Semgrep | go test |
| **Rust** | cargo check | Clippy | cargo fmt | cargo audit, Semgrep | cargo test |

### `/workflow-ship`

Run preflight checks, then commit, push, and open a PR.

**What it does:**

- Runs `/workflow-preflight --fix` first. If checks fail, it applies auto-fixes and re-runs them. If it applied fixes, it stops so you can review them before running `/workflow-ship` again. If issues can't be fixed automatically, it stops and reports them
- Asks whether to commit to the current branch or a new one (on main or master, it requires a new branch)
- Stages specific files and writes a commit message in the style of your recent commits, with no Claude attribution
- Pushes, setting upstream if needed, and never force pushes
- Asks for the PR target (staging first if it exists on origin, otherwise main), opens the PR with a summary, test plan, and Claude Code attribution footer, and returns the URL

**Usage:**

```
/workflow-ship
```

To go further, `/workflow-babysit` does the same commit, push and PR steps without asking, then takes the PR through review, merge and deploy.

### `/workflow-babysit`

Takes the current branch to production in one unattended run. Run `/workflow-babysit` or say "babysit this to prod", then walk away. Invoking it is the approval to merge.

**What it does:**

- Opens the PR if there isn't one. It commits uncommitted changes in the style of your recent commits, creates a branch when you're on the default or staging branch, pushes, and targets staging when the repo uses a staging branch
- Asks its only questions at the start: which uncommitted files to leave out if some look unrelated, what to do when the Claude Code review action isn't set up, and whether to promote other people's unreleased commits that are already on staging. It also warns when a branch rule needs a human approval. After that it runs without stopping
- Waits for CI and for the Claude Code GitHub Action, Codex Code Review and Cursor Bugbot to finish on the head commit, including a clean Codex pass that shows up only as a 👍 reaction
- Fixes correctness, data-loss, security and regression findings in code the PR changed, opens issues for the rest or replies "by design", and replies to and resolves every thread. Claude Code and Bugbot re-review by themselves after each push, and Codex gets one scoped re-review request per round, for up to 3 rounds of fixes. A finding Claude Code raises again after it was answered gets a link to the earlier reply
- Works alongside Bugbot Autofix: it waits for Autofix to finish, pulls the commits Autofix pushed, only fixes what Autofix didn't, and never merges an Autofix branch of its own
- Runs Claude Code's built-in `/code-review` locally in place of the GitHub Action when the action isn't set up, if you choose that
- Merges with the repo's merge method, and only the commit that was reviewed
- With a staging branch, it watches the staging deploy, opens or reuses a `Release:` PR into the default branch, reviews it the same way, and merges it
- Watches the production deploy until every affected service is live, then runs a health check
- Reports what merged, which reviewers ran, what was deferred and how the deploy went, then does whatever you asked for once the change is live

**When it stops:** a blocking finding still open after 3 rounds, a teammate requesting changes, CI it can't fix, a merge GitHub refuses, or a failed deploy or health check. It never force pushes, never merges with `--admin`, never deploys or changes anything on your host itself, and never reverts on its own. Run it again after a stop and it picks up the open PR, or the release step when run from staging.

**Usage:**

```
/workflow-babysit                              # The current branch
/workflow-babysit 142                          # PR #142
/workflow-babysit then close issue #87         # Something to do once it's live
```

**Requirements:**

- A GitHub repository and an authenticated `gh` CLI
- At least one PR reviewer: the Claude Code GitHub Action (set up with `/workflow-claude-actions` or the built-in `/install-github-app`), Codex Code Review with automatic reviews on, or Cursor Bugbot. Without the Claude Code action, it can run `/code-review` locally instead
- To walk away, permission for `gh`, `git`, `curl` and your host's CLI, or auto mode. Otherwise the first permission prompt pauses the run until you're back

**Deploy targets:** your host deploys on merge, and the skill only watches. It finds the deploy through GitHub deployments (Vercel, Railway and other hosts that report back to GitHub), a GitHub Actions deploy workflow, or a host CLI linked to the repo. For Railway it uses the CLI for per-service status, logs and domains. If it finds no deploy target, it stops after the merge and says so.

**Per-repo settings:** the skill reads your project and user CLAUDE.md, and anything there about reviews, merges or deploys overrides its defaults. For example:

```markdown
## Review triage

Also fix before merging: anything that touches billing or auth.
If Claude Code review is off, use the local /code-review.

## Deploy

Production health check: https://example.com/api/health
Staging health check: https://staging.example.com/api/health
Before merging into staging, make sure the staging database and Redis services are running.
```

### `/workflow-claude-actions`

Sets up or updates the Claude Code GitHub Actions so PR reviews post inline comments and both workflows run on the newest Opus. It builds on the built-in `/install-github-app`, which installs the Claude GitHub App and adds the workflows, and adds:

- `--model opus` on both workflows. The alias follows the newest Opus that the action's bundled Claude Code knows about, and the action's floating `@v1` tag picks up new releases without edits
- Inline comments from the review workflow. Workflows from older versions of `/install-github-app` run `/code-review` with no way to post, so their findings never reach the PR
- In-place edits: it changes only the model, `--comment` and the inline-comment tool, and keeps your triggers, filters, permissions and auth. It copies the bundled workflows only when one is missing
- A bundled review workflow that skips fork PRs and bot PRs such as Dependabot's, which would otherwise fail. On public repos it offers to add the same guard to an existing review workflow
- A PR into your staging branch when that's where work lands, and notes on what to expect afterwards

**What it does:**

- Finds the Claude workflows on the base branch by content, not filename, and notes pinned or pre-v1 actions, the auth they use, and whether they're disabled
- Asks its questions at once: whether the Claude GitHub App is installed (skipped when `claude[bot]` has commented in the repo recently), whether to use a subscription token or an API key for new workflows, and what to do about a different model, a pinned action or a pre-v1 action
- Checks for the `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` secret on the repo or the organization. If it's missing, it gives you the commands to set it in your own terminal and never asks for the token in chat
- Checks every edited file parses as YAML, shows you the diff, and commits, pushes and opens one PR only after you approve it. It never merges, and never changes repo settings or files outside `.github/workflows/`
- Tells you what to expect: the PR's own review check passes without reviewing (the action only runs a workflow that matches the default branch, so in staging repos reviews pause on staging PRs until this is promoted), bot reviewers may wrongly flag `pull-requests: read`, and how to confirm the model from the run log

**Usage:**

```
/workflow-claude-actions
```

**Requirements:**

- An authenticated `gh` CLI, a clean working tree, and admin access if a secret needs setting
- The Claude GitHub App on the repo (https://github.com/apps/claude)
- A Claude subscription token from `claude setup-token`, or an Anthropic API key. With an API key, each Opus review bills to your API account

---

## Quick Start

### Installation

```
/plugin install ai-workflow@claude-code-plugins-dev
```

---

## How It Works

### Preflight Check Flow

```
Discovery Phase
      |
      v
Detect Project Type(s)
      |
      v
Find Configured Tools (including security scanners)
      |
      v
Run Checks (type -> lint -> format -> security -> test)
      |
      v
Present Results
      |
      v
Fix Prompt (if issues found)
      |
      v
Verify Fixes
```

---

## Best Practices

### Preflight Integration

- Run `/workflow-preflight` before you commit
- Use `--fix` locally and `--check-only` in CI.
- Align local checks with CI configuration

---

## Plugin Details

- **Name:** AI-Workflow
- **Version:** 2.1.0
- **Type:** Development Workflow Automation
- **Skills:** `/workflow-preflight`, `/workflow-ship`, `/workflow-babysit`, `/workflow-claude-actions`, `/workflow-principles`, `/workflow-rules`
- **License:** [MIT](LICENSE)
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
