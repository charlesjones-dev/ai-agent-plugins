# AI-Workflow Plugin

**Release and PR workflows for Claude Code.** Take a branch to production through Claude Code, Codex and Cursor Bugbot review, merge and a watched deploy, or stop when the PR is ready to merge. Get a review loop with models from several providers, finish other people's PRs, refresh stale ones, and keep Claude's PR descriptions and commit messages short and accurate with a few CLAUDE.md rules.

Several skills and parts of `/workflow-babysit` are adapted from Theo Browne's [tstack](https://github.com/t3dotgg/tstack). See [Credits](#credits).

The plugin runs in Claude Code only.

---

## Available Skills

### `/workflow-babysit`

Takes the current branch to production in one unattended run. Run `/workflow-babysit` or say "babysit this to prod", then walk away. Invoking it approves the merge and any test method needed to prove the change, even where a project file says to ask first. With `--to ready`, or "full stop", it does everything except merge. "Full send" merges the PR into its own base and watches that deploy, so in a repo with a staging branch it stops on staging. The skill starts only on a clear request to ship, not on those words in passing.

**What it does:**

- Finishes the change first when your request includes work that isn't done yet, such as "fix the login redirect and full send"
- Proves every change before it's pushed: it reproduces the failure and watches the fix pass, runs the checks your CI runs, adds one focused test when the behavior has none, and runs the app for UI changes. The PR's test plan lists that proof. If it can't prove a change, it stops and asks
- Opens the PR if there isn't one. It commits uncommitted changes in the style of your recent commits, creates a branch when you're on the default or staging branch, pushes, and targets staging when the repo uses a staging branch
- Asks its only questions at the start: which uncommitted files to leave out if some look unrelated, what to do when the Claude Code review action isn't set up, and whether to promote other people's unreleased commits that are already on staging. It also warns when a branch rule needs a human approval. After that it stops only for the cases under **When it stops**
- Opens the PR with a title that says what the change does for the user, and a description that starts with the problem rather than a list of edits
- Waits for CI and for the Claude Code GitHub Action, Codex Code Review and Cursor Bugbot to finish on the head commit, including a clean Codex pass that shows up only as a 👍 reaction. It also waits for Greptile and Macroscope when the repo uses them
- Waits with one watcher per PR instead of a polling loop. In T3 Code it uses T3's own PR watch. Elsewhere it runs the bundled `pr-wait` script under Claude Code's Monitor tool, which wakes Claude once per event: a failed check, a new comment or thread, a reviewer finishing, or base commits that touch the PR's files
- Fixes correctness, data-loss, security and regression findings in code the PR changed, opens issues for the rest or replies "by design", and replies to and resolves every thread
- Each reply starts with a note that names the model and says it's responding on your behalf. It keeps the PR the size the goal needs, and lists the rest as follow-ups. Claude Code and Bugbot re-review by themselves after each push, and Codex gets one scoped re-review request per round, for up to 3 rounds of fixes. A finding Claude Code raises again after it was answered gets a link to the earlier reply
- Works alongside Bugbot Autofix: it waits for Autofix to finish, pulls the commits Autofix pushed, only fixes what Autofix didn't, and never merges an Autofix branch of its own
- Runs Claude Code's built-in `/code-review` locally in place of the GitHub Action when the action isn't set up, if you choose that
- Merges with the repo's merge method, and only the commit that was reviewed, after a merge gate: proof covers the whole diff, checks are green, every finding is answered, no one is requesting changes, and the branch is up to date with its base
- With `--to ready`, it turns off auto-merge, takes the PR out of a merge queue, and ends with one verdict: ready to merge, waiting for a required approval, or blocked. The PR stays open for you to merge
- With `--council`, it runs `/workflow-council` unattended on the change before the PR opens, checks at the start of the run, before any waiting, that every member is reachable, proves the council's fixes, and puts the council's scores in the PR description
- When the PR conflicts with its base, it merges the base in and resolves the conflicts, so it never needs a force push
- With a staging branch, it watches the staging deploy, opens or reuses a `Release:` PR into the default branch, reviews it the same way, and merges it
- With `--to staging`, it stops once the change is merged into staging and the staging deploy has finished, for example when staging builds go to an internal TestFlight group for testing first. It leaves staging services running and the release for later: run `/workflow-babysit` from the staging branch to promote
- Watches the production deploy until every affected service is live, then runs a health check
- Reports what merged, which reviewers ran, what was deferred and how the deploy went, then does whatever you asked for once the change is live

**When it stops:** it can't prove a change, a teammate requests changes or asks a question, a blocking finding is still open after 3 rounds, CI fails in a way it can't fix, a conflict it can't resolve, another PR makes this one obsolete, a step that would delete data, change production directly or close a PR, a merge GitHub refuses, or a failed deploy or health check. It never force pushes, never merges with `--admin`, never deploys or changes anything on your host itself, and never reverts on its own. Run it again after a stop and it picks up the open PR, or the release step when run from staging.

**Usage:**

```
/workflow-babysit                              # The current branch
/workflow-babysit 142                          # PR #142
/workflow-babysit --to staging                 # Stop once it's on staging, promote later
/workflow-babysit --to ready                   # Stop when the PR is ready to merge ("full stop")
/workflow-babysit full send                    # Merge into its own base, no promotion to production
/workflow-babysit --council                    # Cross-model review before the PR opens
/workflow-babysit then close issue #87         # Something to do once it's live
```

**Requirements:**

- A GitHub repository and an authenticated `gh` CLI
- At least one PR reviewer: the Claude Code GitHub Action (set up with Claude Code's built-in `/install-github-app`), Codex Code Review with automatic reviews on, or Cursor Bugbot. Without the Claude Code action, it can run `/code-review` locally instead
- To walk away, permission for `gh`, `git`, `curl`, `python3` and your host's CLI, or auto mode. Otherwise the first permission prompt pauses the run until you're back
- `python3` for the `pr-wait` watcher outside T3 Code. Without it, the skill polls every 30 seconds instead
- With `--council` outside T3 Code, the CLI for each provider on the council, installed and signed in, and permission to run it

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

### `/workflow-council`

Reviews a change in a loop with models from several providers, until they approve or the round budget runs out. Say "council" for three members, or "sol loop" or "second opinion" for one.

**What it does:**

- Asks on its first run which models sit on your council. It lists only the models this machine can reach (T3 Code's providers, or the CLIs it finds), recommends Claude, GPT and Grok, and saves your answer to `~/.claude/workflow-council.json`. A repo can have its own council in `.claude/workflow-council.json`
- Saves model families such as "GPT Sol", so the council moves to each new release by itself. An exact model ID in the file pins that model
- Takes the members from the command first, then the repo's saved council, then yours. It never puts another model in place of one it can't reach
- Reaches each member through T3 Code's `delegate_task` in T3 Code. In plain Claude Code, it uses a subagent for Claude, and each provider's own CLI for the rest: the Codex CLI for OpenAI, the Grok CLI for xAI, and the Cursor CLI for any model Cursor offers. Every member reviews read-only, and the skill stops if one changes a file
- Sends every member the same brief: the intent, what's out of scope, the checks run, and the diff. Each one replies with a verdict, a score out of 10 and findings ranked blocker, should or nit
- Checks each finding itself, fixes what's right with the smallest change, pushes back with evidence on the rest, and declines nits as follow-ups. It keeps a ledger of every finding
- Runs 3 rounds by default, and up to 5 for security, auth, data-loss or concurrency changes while a blocker or should finding stays open. It stops early when a round returns only nits
- Puts a "Council review" table of scores per round in the PR description, and never pushes during the loop unless you asked it to
- With `--unattended`, which `/workflow-babysit --council` uses, it asks nothing: it leaves out members it can't reach, and declines findings still disputed at the end, with both sides written down

**Usage:**

```
/workflow-council                     # Three members on the current change
/workflow-council gpt                 # One member: a second-opinion loop
/workflow-council gpt,grok 142        # Two members on PR #142
/workflow-council --rounds 5          # A longer budget
/workflow-council --setup             # Choose your council again
/workflow-council --setup repo        # Save a council for this repo only
```

**Requirements:** in T3 Code, nothing more. In plain Claude Code, the CLI for each provider on the council, installed and signed in. Each round costs a call to every member.

### `/workflow-takeover`

Finishes a PR, branch or agent thread that someone else started, and keeps their credit. Say "take over PR 142".

**What it does:**

- Reads the source, its review findings and later corrections, and finds the current head commit and any uncommitted work. It treats claims in the handoff, such as "tests pass", as unchecked until it runs them
- Continues on a new branch from the original commits by default, so their authors stay, or in place when you ask for that
- Runs `/workflow-refresh` to bring the work up to date, finishes the original goal without adding features, and verifies it independently
- Credits the original contributors in the PR description, and in `Co-authored-by:` trailers with verified identities when the PR will be squash-merged
- Runs `/workflow-babysit --to ready` on the result, unless you asked it to merge. It never merges or closes the original PR without your say-so

**Usage:**

```
/workflow-takeover 142
/workflow-takeover feature/old-branch and merge it
```

### `/workflow-refresh`

Brings an old PR up to date and decides whether it should still exist. Say "refresh PR 142" or "is this PR still worth it?".

**What it does:**

- States the PR's goal from its title, body, linked issues, commits and review threads
- Reads what changed on the base branch since the PR diverged, and searches for PRs that replaced or compete with it
- Recommends REFRESH, REWORK or CLOSE, with evidence. A PR isn't current just because Git reports no conflicts
- For REFRESH, rebases onto the latest base, compares the commits before and after with `git range-diff`, runs the checks for the touched area, and pushes with a lease tied to the head it recorded
- Pushes only when you asked it to refresh or rebase the PR. A question such as "is this PR still worth it?" gets an answer and no push. It asks before it rewrites a branch that belongs to someone else
- Never merges, closes the PR or changes its base

**Usage:**

```
/workflow-refresh 142
```

### `workflow-pr-comments` (automatic)

Claude uses this skill by itself whenever it posts a GitHub comment for you. Each comment starts with a note callout that names the model and says it's responding on your behalf, followed by a short reply that leads with the conclusion and cites a commit, check or file. Commands to bots, such as `@codex review` and `bugbot run`, stay bare so the bots still read them.

```markdown
> [!NOTE]
> 🤖 **Claude Opus 5.5 responding on behalf of your-login**

Fixed in 3f2a1c9: the retry now stops after the third attempt.
```

### `/workflow-rules`

Adds, removes or lists **behavior rules** in CLAUDE.md that keep Claude's PR descriptions and commit messages short and limited to what was done.

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
| `short-pr-bodies` | Keep PR bodies short: the problem, then how the change fixes it |
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
- **Version:** 3.2.0
- **Skills:** `/workflow-babysit`, `/workflow-council`, `/workflow-takeover`, `/workflow-refresh`, `/workflow-rules`, and `workflow-pr-comments`, which Claude runs by itself
- **License:** MIT
- **Author:** Charles Jones

---

## Credits

`/workflow-council`, `/workflow-takeover`, `/workflow-refresh`, `workflow-pr-comments`, and the proof, merge gate, `--to ready`, PR-watching, reviewer and PR-description parts of `/workflow-babysit` are adapted from [tstack](https://github.com/t3dotgg/tstack) by Theo Browne: agent skills for Claude Code and Codex, some of which use [T3 Code](https://github.com/pingdotgg/t3code) features. The bundled `pr-wait` script is his, extended to know the Claude Code review action, Codex and Cursor Bugbot. tstack is MIT licensed. [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) has its license and lists each adapted file.

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
