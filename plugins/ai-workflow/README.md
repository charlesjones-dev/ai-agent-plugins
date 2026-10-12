# AI-Workflow Plugin

**Release and PR workflows for Claude Code.** Take a branch to production through Claude Code, Codex and Cursor Bugbot review, merge and a watched deploy, and keep Claude's PR descriptions and commit messages short and accurate with a few CLAUDE.md rules.

The plugin runs in Claude Code only.

---

## Available Skills

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
- With `--to staging`, it stops once the change is merged into staging and the staging deploy has finished, for example when staging builds go to an internal TestFlight group for testing first. It leaves staging services running and the release for later: run `/workflow-babysit` from the staging branch to promote
- Watches the production deploy until every affected service is live, then runs a health check
- Reports what merged, which reviewers ran, what was deferred and how the deploy went, then does whatever you asked for once the change is live

**When it stops:** a blocking finding still open after 3 rounds, a teammate requesting changes, CI it can't fix, a merge GitHub refuses, or a failed deploy or health check. It never force pushes, never merges with `--admin`, never deploys or changes anything on your host itself, and never reverts on its own. Run it again after a stop and it picks up the open PR, or the release step when run from staging.

**Usage:**

```
/workflow-babysit                              # The current branch
/workflow-babysit 142                          # PR #142
/workflow-babysit --to staging                 # Stop once it's on staging, promote later
/workflow-babysit then close issue #87         # Something to do once it's live
```

**Requirements:**

- A GitHub repository and an authenticated `gh` CLI
- At least one PR reviewer: the Claude Code GitHub Action (set up with Claude Code's built-in `/install-github-app`), Codex Code Review with automatic reviews on, or Cursor Bugbot. Without the Claude Code action, it can run `/code-review` locally instead
- To walk away, permission for `gh`, `git`, `curl` and your host's CLI, or auto mode. Otherwise the first permission prompt pauses the run until you're back

**Deploy targets:** your host deploys on merge, and the skill only watches. It finds the deploy through GitHub deployments (Vercel, Railway and other hosts that report back to GitHub), a GitHub Actions deploy workflow, Xcode Cloud's check runs for app builds, or a host CLI linked to the repo. For Railway it uses the CLI for per-service status, logs and domains. If it finds no deploy target, it stops after the merge and says so.

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

### `/workflow-rules`

Adds, removes or lists **behavior rules** in CLAUDE.md that keep Claude's PR descriptions and commit messages short and limited to what was actually done.

**What it does:**

- Reads the rule library shipped with the skill
- Picks the target file: user `~/.claude/CLAUDE.md` (default, applies everywhere) or project `./CLAUDE.md`, resolving the home directory on Windows and POSIX
- Offers a multi-select picker with already-installed rules left out
- Wraps each installed rule in HTML comment markers (`<!-- workflow-rules:id=... -->`) so adds are idempotent and removes are precise, even if you edit the rule's title later
- Shows a unified diff before any write and asks you to confirm

**Usage:**

```
/workflow-rules
```

**Modes (chosen interactively):**

- **Add**: install one or more rules into the chosen CLAUDE.md
- **Remove**: uninstall installed rules, matched by ID, not title
- **List**: show what's installed and where

**Rule library (PR and Commit Hygiene):**

| Rule | What it says |
|------|--------------|
| `pr-scope-current-session` | Describe only the commits from the current session |
| `no-fabricated-test-plans` | Don't list testing that wasn't done |
| `no-speculative-deploy-steps` | Don't add deploy or rollout steps unless asked |
| `short-pr-bodies` | Keep PR bodies to a short summary of the diff |
| `scoped-commit-messages` | Describe what the diff does, not surrounding context |

**Retired rules (October 2026):** five rules left the library because Claude Code now covers them. If you installed them earlier, the List and Remove modes still find them and say what replaces each one:

| Rule | Replaced by |
|------|-------------|
| `no-generated-by-footers` | Claude Code's `attribution` setting. `"attribution": false` in `~/.claude/settings.json` hides the commit trailer and PR line |
| `no-internal-narration`, `match-response-to-task` | The built-in Concise output style (`/output-style concise`) |
| `no-unrequested-features`, `confirm-risky-actions` | Nothing. Claude Code's built-in instructions cover them |

---

## Removed Skills

| Skill | Status |
|-------|--------|
| `/workflow-ship` | Moved to ai-git (October 2026). Run `/git-commit-push-pr --preflight` |
| `/workflow-preflight` | Moved to ai-git as `/git-preflight` (October 2026) |
| `/workflow-claude-actions` | Removed (October 2026). Use Claude Code's built-in `/install-github-app`, which installs the Claude GitHub App, saves the auth secret, and opens a PR with `claude.yml` and, optionally, `claude-code-review.yml`. Since Claude Code v2.1.229, the review workflow posts inline comments, or one summary comment when it finds nothing. Without `--model`, the action uses Claude Code's default model, Opus 5.5 on Pro, Max, Team, Enterprise and the API. To update an older workflow, run `/install-github-app` again and pick "Update workflow file with latest version" |
| `/workflow-principles` | Removed (October 2026). The built-in `/init` writes CLAUDE.md |
| `/workflow-plan-phases`, `/workflow-implement-phases` | Removed (July 2026). Claude Code's native Dynamic Workflows orchestrate subagent fan-out with per-agent token budgets |

ai-git is a separate plugin. To keep using the moved skills, install it once with `/plugin install ai-git@ai-agent-plugins`. Removed skills are still in git history.

---

## Quick Start

### Installation

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-workflow@ai-agent-plugins
```

---

## Plugin Details

- **Name:** AI-Workflow Plugin
- **Type:** AI Instruction Plugin (Skills)
- **Version:** 3.0.1
- **Skills:** `/workflow-babysit`, `/workflow-rules`
- **License:** MIT
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
