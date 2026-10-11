# Changelog

All notable changes to AI Agent Plugins (formerly Claude Code Plugins for Developers) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2026-10-11

The repository and marketplace are renamed from `claude-code-plugins-dev` to `ai-agent-plugins`, and 8 plugins are now packaged for Codex and Cursor as well as Claude Code. Four plugins merge into others (ai-aeo and ai-geo into ai-seo, ai-cvp into ai-security, ai-writing into ai-slop), which leaves 13. Skills that repeated another skill are merged, skills that Claude Code now covers are removed, ai-knowledge moves to Claude Code's path-scoped rules, and five wrapper subagents that couldn't load their skills are removed. The marketplace goes from 64 skills to 41.

### Removed

- **ai-aeo and ai-geo** — merged into ai-seo (see Changed). `/aeo-audit` and `/geo-audit` are now `/seo-audit aeo` and `/seo-audit geo`, `/aeo-fix` and `/geo-fix` are folded into `/seo-fix`, and `/aeo-faq`, `/aeo-questions` and `/geo-llms-txt` are now `/seo-faq`, `/seo-questions` and `/seo-llms-txt`. The Claude Code catalog's new `renames` map points both names at ai-seo, so Claude Code switches an existing install's setting over to ai-seo. Users then run `/plugin install ai-seo@ai-agent-plugins` once to install it.
- **ai-cvp** — merged into ai-security. `/cvp-defense-audit` is now `/security-cvp-audit` (see Added). `renames` points ai-cvp at ai-security, and users who only had ai-cvp run `/plugin install ai-security@ai-agent-plugins` once.
- **ai-writing** — merged into ai-slop. `/writing-humanize` is now `/slop-rewrite` (see Added), and its pattern catalog is merged into ai-slop's `signals.md`, so the audit and the rewrite share one list. `renames` points ai-writing at ai-slop, and users run `/plugin install ai-slop@ai-agent-plugins` once.
- **ai-git `/git-commit-push` and `/git-pr-codex-loop`** — `/git-commit-push` is now `/git-commit-push-pr --no-pr`. The Codex review loop is removed: Claude Code's `/code-review --fix` and `/autofix-pr` loop on review comments and CI failures, and `/workflow-babysit` still triages Codex Code Review findings. Major version bump: ai-git 1.3.2 → 2.0.0.
- **ai-workflow `/workflow-ship`, `/workflow-preflight`, `/workflow-claude-actions` and `/workflow-principles`** — `/workflow-ship` is now `/git-commit-push-pr --preflight` and `/workflow-preflight` is now `/git-preflight`, both in ai-git. Claude Code's `/install-github-app` replaces `/workflow-claude-actions`: its review workflow posts inline comments since v2.1.229, and without `--model` the workflows use Claude Code's default model, Opus 5.5. `/init` replaces `/workflow-principles`. Major version bump: ai-workflow 2.1.0 → 3.0.0.
- **Five `/workflow-rules` rules** — `no-generated-by-footers` (Claude Code's `attribution` setting does this), `no-internal-narration` and `match-response-to-task` (the built-in concise output style, `/output-style concise`), and `no-unrequested-features` and `confirm-risky-actions` (covered by Claude Code's built-in instructions). The list and remove modes still find copies already installed in CLAUDE.md and say what replaces each one.
- **ai-ado `/ado-create-feature`, `/ado-create-story`, `/ado-create-task` and `/ado-work-items`** — replaced by `/ado-create` (see Added). The `/ado-work-items` guidelines are now `/ado-create`'s `references/work-items.md`. Major version bump: ai-ado 1.3.3 → 2.0.0.
- **ai-modernize `/modernize-scan`** — use `/modernize-audit <path> --defaults` (see Changed).
- **ai-knowledge Obsidian support** — the vault instructions, `[[wiki-link]]` syntax and the `related` and `sources` frontmatter. Cross-references are plain paths in an optional Related section, the only place Claude sees them, since Claude Code strips frontmatter.
- **ai-knowledge `/kb-auto`, `/kb-load`, `/kb-ingest`, `/kb-import`, `/kb-harvest`, `/kb-absorb`, `/kb-search`, `/kb-list`, `/kb-organize`, `/kb-remove` and `/kb-upgrade`** — 17 skills become 7. Auto-capture replaces `/kb-auto` (see Added), and an @-mention replaces `/kb-load`. `/kb-add` takes over ingest, import, harvest and absorb, `/kb-query` takes over search and list, `/kb-prune` takes over organize and remove, and `/kb-migrate` takes over upgrade. The plugin README maps each one. Major version bump: ai-knowledge 1.5.2 → 2.0.0.
- **Wrapper subagents** — `accessibility-auditor`, `modernize-auditor`, `performance-auditor`, `security-dependency-scanner` and `swift-release-auditor`. Each one's instructions were to load its plugin's skill, which Claude Code refuses because those skills set `disable-model-invocation: true`, so a skill that handed off to one reached a subagent without the methodology or report template. `/accessibility-audit`, `/modernize-audit`, `/performance-audit` and `/security-scan-dependencies` now run their audits themselves. For unattended runs, pass the settings as arguments (see Changed); `/swift-preflight --check-only` replaces `swift-release-auditor`. `security-auditor` stays: it's a separate reviewer role with its own instructions that `/security-audit` runs in parallel. Major version bumps: ai-accessibility 1.4.2 → 2.0.0, ai-modernize 1.1.1 → 2.0.0, ai-performance 1.2.2 → 2.0.0, ai-security 2.0.1 → 3.0.0, ai-swift 1.0.2 → 2.0.0.

### Changed

- **Repository and marketplace renamed** — `charlesjones-dev/claude-code-plugins-dev` is now `charlesjones-dev/ai-agent-plugins`, and the marketplace `name` in `.claude-plugin/marketplace.json` changed to match. Install IDs change from `<plugin>@claude-code-plugins-dev` to `<plugin>@ai-agent-plugins`. GitHub redirects the old URLs, so existing installs and links keep working, but Claude Code keeps those installs under the old marketplace name. To switch, remove the old marketplace, add `charlesjones-dev/ai-agent-plugins` and reinstall. Removing the old marketplace uninstalls its plugins. The README has the commands, and a table of renamed commands.
- **ai-seo covers SEO, AEO and GEO** — six skills, all ai-aeo and ai-geo checks and fixes carried over. Major version bump: ai-seo 1.0.1 → 2.0.0.
  - `/seo-audit [seo|aeo|geo|all]` audits one lens or all three (the default, asked first when missing) and takes every setting as an argument, with defaults for unattended runs. It writes one report to `docs/seo-audit/` with a section and a score per lens and no combined score. Findings carry lens-prefixed IDs (`SEO-1`, `AEO-1`, `GEO-1`). The report index gets a column per lens, rows from 1.x are converted, and trends compare against reports in the old `docs/aeo-audit/` and `docs/geo-audit/` folders.
  - `/seo-fix` applies the newest report for every lens it covers, keeps every fix type, confirmation rule and `--dry-run` from the three fix skills, applies fixes two lenses share once, and acts as `--dry-run` in an unattended run. It takes an optional report path, so an older AEO or GEO report can still be applied.
  - `/seo-schema` owns all JSON-LD generation and validation, including FAQPage/QAPage and Organization/Person with `sameAs`. `/seo-schema`, `/seo-fix` and `/seo-faq` share one `json-ld.md` rule set.
  - `/seo-faq`, `/seo-questions` and `/seo-llms-txt` take their setup as arguments and have unattended defaults. With no arguments they behave as before. `/seo-questions` can also start from an earlier question map, including one in the old folder.
- **Audit skills take their settings as arguments** — each asks only for what the arguments leave out, and asks nothing when they cover everything, so the audits can run unattended.
  - `/accessibility-audit [WCAG version] [level] [path or URL]`, such as `/accessibility-audit 2.2 AA src/`. With a URL from the arguments, it uses Playwright visual testing when the Playwright MCP server responds and otherwise audits the HTML and notes that visual testing was skipped. The Playwright setup step now covers Claude Code (`.mcp.json`), Cursor (`.cursor/mcp.json`) and Codex (`codex mcp add`).
  - `/modernize-audit [path] [ai=…] [era=…] [stack=…|auto] [categories=all|…] [severity=all|medium|high] [--defaults]`. `--defaults` asks nothing and uses the defaults for any setting the arguments leave out, which replaces `/modernize-scan`. The same defaults apply when no one can answer, and the report marks each one "(default)". The audit also takes a single file as its scope, and skips categories that can't apply to it. Its category checklist moved to `skills/modernize-audit/references/categories.md`.
  - `/performance-audit [path]` limits the audit to one directory.
  - `/security-scan-dependencies [URL] [frontend|cms|headers|all]`. With only a URL in an unattended run, the scope is `all`. The skill also gained build-tool detection (Webpack, Vite, Turbopack, Parcel), including a warning when a Vite dev server is exposed.
  - Their report paths are repository-relative (`docs/accessibility/`, `docs/modernize/`, `docs/performance/`, `docs/security/`) rather than written with a leading slash.
- **ai-git `/git-commit-push-pr`** — takes `--preflight`, which runs `/git-preflight --fix` first and stops if it applied fixes or problems remain, and `--no-pr`, which stops after the push. It used to ignore all arguments. It reads the default branch from `gh` instead of assuming `main`, returns the URL of a PR that's already open, stops when a push is rejected or `gh` is missing, and writes a test plan with only what was actually run. In Codex and Cursor it runs preflight by loading the `git-preflight` skill.
- **ai-git `/git-preflight`** — moved from ai-workflow, so it now runs in Codex and Cursor too. It no longer depends on Claude Code for platform detection or questions.
- **ai-workflow `/workflow-babysit`** — points to `/install-github-app` instead of `/workflow-claude-actions` when Claude Code review is off, including its "Update workflow file with latest version" option, and treats the summary comment a v2.1.229 or later review workflow posts as a clean pass.
- **ai-security `/security-cvp-audit`** — its ignore rule no longer hides `/security-audit` reports. When git already tracks files in `docs/security/`, it ignores only the audit's own paths (`/docs/security/*cvp*audit*`, `/docs/security/tests/`, `/docs/security/harness/`); otherwise it still adds `/docs/security/` and says that also covers `/security-audit` reports. It no longer suggests `git rm -r --cached docs/security`. Its reports are now named `<date>-security-cvp-audit.md`, so they no longer end in `-security-audit` like `/security-audit`'s. Recon reads only the newest `/security-audit` report pair, and treats `/security-scan-dependencies` reports as leads only.
- **ai-swift** — `/swift-preflight` can't run `/swift-ci-scaffold` or `/swift-verify`, which are command-only, so its fix step now prints which command to run for which findings, with the path and flags filled in, plus a guided list for the edits no command makes. `--fix` prints that list without asking. `/swift-diagnose` and `/swift-ci-scaffold` also name the command to run instead of handing off, and all five skills read arguments in Codex and Cursor too.
- **ai-knowledge stores the knowledge base as Claude Code rules** — instead of a CLAUDE.md table that asked Claude to read each article at the right moment. Scoped articles live in `.claude/rules/kb/` with `paths` frontmatter and load when Claude reads, writes or edits a matching file, and pinned ones load every session. Articles with only keywords live in `.claude/kb/` and are read on demand. The always-loaded `.claude/rules/kb/_index.md` lists every scoped and on-demand article with its keywords, so a 1.x row's keywords still bring in a scoped article by topic, and Claude names each scoped or on-demand article it loads in one line (`📖 Loaded KB: conventions/api.md`). CLAUDE.md gets nothing. In frontmatter, `scope` becomes `paths` and an article's folder replaces `pinned`; the `related` and `sources` fields and `[[wiki-links]]` give way to plain paths in an optional Related section. Teammates get the knowledge base without installing the plugin. `/kb-add [note | path, glob or URL ... | --absorb]`, `/kb-query <question> | search <terms> | tag:<tag> | list`, `/kb-prune [remove <article> | organize]` and `/kb-learn [focus]` take arguments.
- **ai-knowledge `/kb-learn`** — Claude can now run it itself (`auto <learning>`), but only under auto-capture or when you ask it to save something; a user stating a rule isn't enough. Typed as `/kb-learn`, it still reviews the whole conversation and asks before saving.
- **Codex catalog** — Codex now reads `.agents/plugins/marketplace.json` instead of the Claude Code catalog, so it lists only the 8 plugins that run there. Codex users who installed a Claude Code-only plugin from the old catalog no longer get updates for it.
- Every plugin's `repository` field, the README install lines, and the report footers in `/seo-audit`, `/seo-questions` and `/compliance-notice-generate` point at the new URL. The `/seo-audit` reports no longer call the plugin a Claude Code plugin.
- README rewritten with a "Runs in" column, install steps for Claude Code, Codex and Cursor, and a section on moving from `claude-code-plugins-dev` that maps each renamed command. The portable plugins' READMEs add Codex and Cursor install steps and note what works only in Claude Code, such as `claude mcp add`. CONTRIBUTING, SECURITY and CLAUDE.md describe the new files, and CLAUDE.md now says not to write agents that only load a skill, or skills that tell the agent to run a command-only skill.
- Marketplace descriptions: "Plugins for git and project workflows, code audits and release checks. All 13 run in Claude Code, and 8 also run in Codex and Cursor." for Claude Code, and "Plugins for code audits, release checks, git workflows and writing cleanup in Claude Code, Codex and Cursor." for Cursor.

### Added

- **Codex and Cursor support** — ai-accessibility, ai-compliance, ai-git, ai-modernize, ai-performance, ai-seo, ai-slop and ai-swift are listed in two new catalogs, `.agents/plugins/marketplace.json` (Codex) and `.cursor-plugin/marketplace.json` (Cursor). Each has a root `plugin.json` in the [Agent Plugins](https://agent-plugins.org/) 1.0 format next to its `.claude-plugin/plugin.json`. Codex and Cursor read the root manifest first, and Claude Code ignores it. Minor version bumps: ai-compliance 1.0.1 → 1.1.0, ai-slop 1.0.0 → 1.1.0. The other six get major bumps under Removed and Changed.
- **ai-slop `/slop-rewrite`** — rewrites a file, a glob, or a block of text pasted right after the command, so it reads as a person wrote it. Leading `type=` (`docs`, `readme`, `blog`, `pr`) and `level=` (`light`, `standard`, `heavy`) settings skip the matching questions. Pasted text comes back as one block to copy, and files change only after you approve the edits. It reads the project's writing rules first, works from the same `signals.md` as `/slop-audit`, and lists any line that needs a fact it doesn't have as a question instead of inventing one. `signals.md` gains the humanize patterns it lacked: copula avoidance, wordy filler phrases, hedging, unnecessary prefixes, trailing -ing analysis, vague attributions, false ranges, upbeat endings, conclusion signposts, chatbot leftovers, formatting habits and developer-text padding.
- **ai-security `/security-cvp-audit [focus area or path] [--model <audit-model-id>]`** — ai-cvp's sandboxed audit planner. It does read-only recon, then writes a paste-ready audit prompt for a sandboxed session on a stronger model, a launch checklist and a fix prompt. `/security-audit` and `/security-cvp-audit` each name the other.
- **ai-ado `/ado-create [feature|story|task] [parent ID] [title]`** — one command for Features, User Stories and Tasks. It keeps every question, field and rule from the three old skills and asks only for what the arguments leave out. It looks up the parent first and warns when a story's parent isn't a Feature or a task's parent isn't a User Story.
- **ai-knowledge `/kb-migrate [--dry-run] [auto=off] [agents=off]`** — moves a 1.x knowledge base to the new layout. It maps each table row and article to pinned, scoped or on-demand and asks before changing anything, moves files with `git mv` so history follows, rewrites `*.ext` globs as `**/*.ext`, drops scopes that pointed at `docs/kb/` itself (in 2.x they'd load the article with every knowledge base read), keeps every row's keywords in `tags`, turns links into plain paths, and removes the CLAUDE.md Knowledge Base section, the `/kb-auto` block and `docs/kb/.obsidian/`. It's safe to re-run, and on a migrated knowledge base it checks and repairs the format. The other commands stop and point to it while a 1.x knowledge base exists. It also finds notes that still point at renamed or removed marketplace commands, plugins and report folders, such as `/writing-humanize`, `/geo-audit` or `docs/geo-audit/`, in the knowledge base, CLAUDE.md, CLAUDE.local.md, AGENTS.md, other `.claude/rules/` files, `.gitignore` and `docs/`. It works from `command-map.md`, a map of every rename and removal since 1.0. Simple renames are applied with the migration and other changes are proposed as sentence rewrites; files outside the knowledge base change only after a separate yes, and dated notes, logs and changelogs are left alone. Its format check runs the same scan, so running `/kb-migrate` again after a marketplace update catches newly stale references.
- **ai-knowledge auto-capture** — saves team knowledge as it comes up, the way Claude Code's auto memory saves personal notes, so you don't have to run `/kb-learn`. It's set per developer: `/kb-init` and `/kb-migrate` turn it on unless you pass `auto=off`, and it stays off for anyone who hasn't run either. A SessionStart hook in the plugin adds the instruction when the setting is on and the project has a 2.x knowledge base. Claude then saves corrections, stated rules, settled decisions and gotchas, updates an existing article instead of adding a duplicate, skips personal preferences, and picks the load mode. It reports each save in one line, and "undo" reverses it. It works with auto memory off. Running `/kb-init` again keeps an earlier choice, and `/kb-init auto=on|off` switches it. The setting lives in `git config --local ai-knowledge.autoCapture`, or in `.claude/settings.local.json` outside git.
- **ai-knowledge `AGENTS.md` section** — Codex and Cursor read `AGENTS.md`, not `.claude/rules/`, so `/kb-init` and `/kb-migrate` add a short section between `<!-- ai-knowledge:start -->` and `<!-- ai-knowledge:end -->` markers, creating the file if needed. It tells those agents to read `_index.md` and the pinned articles at the start of a task, the scoped articles whose `paths` match a file before touching it, and an on-demand article when a task matches its index line. Running `/kb-init` again refreshes it, `/kb-migrate`'s format check repairs it, and `agents=off` skips or removes it. It changes nothing in Claude Code.
- **`scripts/check-manifests.py`** — checks that the three catalogs, both manifest formats and the Codex policy files agree, that each skill's `name` matches its folder, that reference files copied between skills are identical (ai-slop's `signals.md`, ai-seo's `json-ld.md` and report index template, and ai-knowledge's `kb-format.md`), and that every plugin command in ai-knowledge's command map exists. Standard library only.
- Install lines in the ai-modernize and ai-knowledge READMEs, which had none.

### Fixed

- **Codex could start command-only skills unprompted** — Codex ignores Claude Code's `disable-model-invocation: true`, so when a prompt matched, it could run any skill that's meant to run only when called, such as `/git-commit-push-pr`. Each of those skills (37 after this release) now has `agents/openai.yaml` with `allow_implicit_invocation: false`, which keeps it out of the skill list Codex gives the model until you pick it. Cursor and Claude Code already honored the frontmatter field. ai-statusline gets only this fix and the new URL: 1.5.0 → 1.5.1. Codex doesn't list the Claude Code-only plugins, but they get the file too, so the check script applies one rule to every command-only skill.
- **ai-ado `/ado-init`** — it told users, and wrote into CLAUDE.md, that the `ado-work-items` skill loads automatically with the Azure DevOps MCP tools. It couldn't: the skill was command-only. The CLAUDE.md section now has four short work item rules (State "New" and unassigned, the parent hierarchy, HTML fields, Story Points and hours) and points to `/ado-create`. Running `/ado-init` on a project whose section mentions `ado-work-items` replaces that paragraph and leaves the settings alone.
- **ai-ado config reading** — `/ado-init` has written a line-per-value format since 1.1, but the create skills and `/ado-log-story-work` read only the 1.0 format, and `/ado-timesheet-report` read only the newer one. `/ado-create`, `/ado-log-story-work` and `/ado-timesheet-report` now accept either.
- **ai-git `/git-commit-push-pr`** — the PR footer now names the agent that ran the skill instead of always crediting Claude Code. Commits carry no AI attribution in any agent.
- **ai-git `/git-preflight`** — no longer pauses at "Ready to run checks?", no longer offers tool setup with `--fix` or `--check-only`, and its two check-order lists now agree.
- **ai-knowledge 1.x links** — 1.x wrote `related: [[a]], [[b]]`, which isn't valid YAML, and Claude Code doesn't load a rule whose frontmatter won't parse. `/kb-migrate` drops the `related` and `sources` fields and turns their links, and any `[[name]]` links in article bodies, into plain paths.
- **ai-security `/security-cvp-audit`** — the output contract check skips `/security-audit` and `/security-scan-dependencies` reports, and the fix prompt moves only a report file the check printed and checks staged files instead of `git status` before committing.
- **ai-seo** — the SEO lens no longer suggests HowTo or FAQ markup for rich results, and `/seo-llms-txt` no longer saves validation output next to `llms.txt` in the public folder, where the site would publish it.
- **ai-swift `/swift-verify`** pointed at ai-workflow's `/workflow-preflight`. It now points at ai-git's `/git-preflight`.
- Marketplace metadata version bumped `2.12.0` → `3.0.0`. The major bump is for the changed install IDs, the merged plugins and the removed skills and subagents.

## [2.12.0] - 2026-10-10

### Added

#### AI-Workflow Plugin (v2.0.1 → v2.1.0)

- **`/workflow-babysit`** — takes the current branch to production in one unattended run. Runs from `/workflow-babysit` or when you say "babysit this to prod", and invoking it is the approval to merge.
  - Opens the PR itself when there isn't one: commits uncommitted changes in the repo's style, branches off the default or staging branch, pushes, and targets staging when the repo has a staging flow. It doesn't need `/workflow-ship` first.
  - Asks every question at the start (which uncommitted files to leave out if some look unrelated, what to do when the Claude Code review action isn't set up, and whether to promote other people's unreleased commits already on staging, read from GitHub logins), and warns when a branch rule needs a human approval. Then it runs without stopping. It stops only for a blocking finding still open after 3 rounds, a teammate requesting changes, CI it can't fix, a merge GitHub refuses, or a failed deploy or health check. Every wait has a deadline. Running it again after a stop picks up the open PR, or the release step when run from staging.
  - Waits for CI, the Claude Code GitHub Action, Codex Code Review and Cursor Bugbot on the head commit. Claude Code counts as on only when a workflow running `anthropics/claude-code-action` on pull requests is on the default branch and enabled, has its secret set, and posts its findings to the PR. A workflow that runs `/code-review` without `--comment` or another way to comment would otherwise pass as a clean review. A run whose log says `Skipping action due to workflow validation` counts as no review. A clean Codex pass that posts only a 👍 reaction counts as done. Each reviewer has a time limit.
  - Fixes correctness, data-loss, security and regression findings in code the PR changed, opens issues for the rest or replies "by design", and resolves every bot thread. Claude Code re-reviews by itself after each push and Codex gets one scoped `@codex review` per round, with 3 rounds of fixes at most. A finding Claude Code raises again after it was answered gets a link to the earlier reply instead of a second round. When the review workflow doesn't run on pushes, the local `/code-review` covers the new commits. It never resolves a person's thread or merges over a requested change. A repo's CLAUDE.md can set its own triage rules.
  - **Cursor Bugbot** — detected by its `Cursor Bugbot` check run. A pass is done when a `<!-- BUGBOT_REVIEW -->` review names the head commit, and reviews marked `BUGBOT_REVIEW_STALE` are ignored. Only `cursor[bot]` comments with a `BUGBOT_BUG_ID` count as findings, so Cursor Automations approvals and Autofix results aren't triaged. Findings are handled High Severity first, and every location listed under "Additional Locations" is checked. Bugbot re-reviews by itself on pushes; when it doesn't run on the new commit within 5 minutes, the skill posts one `bugbot run`. It also posts one after resolving findings when a required Bugbot check failed on unresolved issues. It never writes `@cursor`, because a mention starts a Cursor agent that can push to the branch.
  - **Bugbot Autofix** — when Autofix commits to the PR branch, the skill waits for the `Cursor Bugbot Autofix` check, pulls its commits, fixes only what it left, and runs `git pull --rebase` before every push. When Autofix makes a separate branch, the skill fixes the finding in the PR and doesn't merge that branch.
  - When the Claude Code action isn't set up, it can run the built-in `/code-review` locally on each PR in its place and post the findings and what happened to them as a PR comment.
  - Merges only the commit that passed the review gate (`--match-head-commit`), never with `--admin`, and uses a merge commit for release PRs so staging and the default branch don't diverge. Each PR's own base decides whether it goes on to the release step. If GitHub's automatic branch deletion removes staging when the release PR merges, it recreates staging at the same commit.
  - With a staging flow, it watches the staging deploy before promoting, opens or reuses a `Release:` PR, and reviews it the same way.
  - Watches the production deploy without deploying anything itself: GitHub deployments first (Vercel, Railway and other hosts that report to GitHub), then GitHub Actions deploy runs, then a linked host CLI. Railway gets per-service status, logs and domains through its CLI, since Railway reports one GitHub deployment per environment. The health check skips `environment_url` values that point at a host dashboard, and treats a 401 or 403 from a protected URL as inconclusive.
  - Follows deploy rules from CLAUDE.md, such as starting staging services before a staging deploy.
- **`/workflow-claude-actions`** — sets up or updates the Claude Code GitHub Actions so PR reviews post inline comments and both workflows run on the newest Opus. Builds on the built-in `/install-github-app`.
  - Passes `--model opus` on the review and `@claude` mention workflows. The alias follows the newest Opus the action's bundled Claude Code knows about, and the floating `@v1` tag picks up new releases without edits. It asks before moving a pinned action to `@v1` or replacing a different model.
  - Edits existing workflows in place: adds the model, `--comment` on the `code-review` prompt and the inline-comment tool, and keeps triggers, filters, permissions and auth. Workflows from older versions of `/install-github-app` ran `/code-review` with no way to post, so their findings never reached the PR. For pre-v1 workflows it recommends regenerating them with `/install-github-app` first.
  - Copies the bundled workflows when one is missing, with a subscription token (`CLAUDE_CODE_OAUTH_TOKEN`) or an Anthropic API key (`ANTHROPIC_API_KEY`). For a missing workflow next to one on Bedrock, Vertex, Foundry or workload identity federation, it copies that workflow's whole auth setup. The bundled review workflow skips fork PRs and bot PRs, which get no OIDC token or are refused by the action. On public repos the skill offers to add that guard to an existing review workflow.
  - Checks for the secret on the repo and the organization, and gives you the commands to set a missing one in your own terminal. It never asks for, prints or passes a token.
  - Checks `ANTHROPIC_MODEL`, which overrides `--model`, and edits every action step in a workflow. It adds the inline-comment tool without quotes so a double-quoted `claude_args` stays valid, and parses every edited file as YAML before showing the diff.
  - Skips asking about the Claude GitHub App when `claude[bot]` has commented in the repo recently. It commits, pushes and opens one PR only after you approve the diff, targets staging when work lands there, switches back to your branch whenever it stops, and never merges or changes repo settings.
  - Explains why the PR's own review check passes without reviewing (and, in staging repos, why reviews pause on staging PRs until promotion), why `pull-requests: read` findings from bot reviewers are false positives, and how to confirm the model from the run log.
- `/workflow-babysit` points to `/workflow-claude-actions` when Claude Code review is off or its review workflow can't post to the PR.

### Fixed

#### AI-Workflow Plugin (v2.0.1 → v2.1.0)

- **`/workflow-ship` preflight step** — `/workflow-preflight` had `disable-model-invocation: true`, so Claude Code refused the Skill tool call that `/workflow-ship` makes in its first step and told Claude not to run the checks another way. `/workflow-preflight` can now be invoked by Claude, and `/workflow-ship` passes `--fix` so preflight applies auto-fixes without stopping at its numbered menu. Claude can also run preflight when you ask to check code before committing.
- Marketplace metadata version bumped `2.11.3` → `2.12.0`.

## [2.11.3] - 2026-10-09

### Fixed

#### AI-CVP Plugin (v1.0.2 → v1.0.3)

- **Audit prompt output contract** — an audit whose sandbox blocked the repo's own test harness invented its own layout: a misnamed report, different finding IDs, no test-path column, and live source files outside `docs/security/tests/`. The final `git status` check passed because git ignores `docs/security/`, and the fix prompt pointed at files that didn't exist. The archive rule was a step ("once it has run, move it"), so it never fired when no test ran in the source tree. The prompt now ends with one output contract that describes the end state:
  - the report at exactly the prompt's path, even if the audit runs on a later date, with `CVP-NN` IDs and each test's archived path in the summary table;
  - every proof test, helper and fixture at `docs/security/tests/<path it would run from>.disabled`, whether or not it ever sat in the source tree;
  - alternative-harness scripts and run logs in `docs/security/harness/`, with no extension the repo's compiler, test runner, formatter or linter picks up, since most of those tools don't read git's ignore rules;
  - build staging in a `mktemp -d` folder outside the repo.
- **Contract check** — before finishing, the audit model runs `find docs/security -type f ! -path '<report>' ! -path 'docs/security/tests/*.disabled' ! -path 'docs/security/harness/*'`, which should print nothing, and `git status --porcelain`. When `docs/security/` already holds earlier reports, the check adds `-newermt` with the planning time so it lists only the audit's files, and the contract says to leave earlier files alone.
- **Alternative harness** — when the sandbox blocks the repo's test command, the audit model may build its own harness under the contract. A result counts as Confirmed only if the test would also compile and run unchanged in the real project, and the report gives the command that runs each such test there.
- **Fix prompt** — step 1 no longer assumes the contract held. It runs the same check, moves the newest `.md` directly under `docs/security/` to the expected report path if the report isn't there, moves misplaced tests into `docs/security/tests/<path>.disabled` (including tests stored relative to a test target's folder), disables source-extension files in `docs/security/harness/`, tells you what moved, reruns the check, and then uses the report's own IDs. Step 2 runs every test the sandbox kept from running through the real project, checks that each one actually ran, and tries to settle Unconfirmed findings with local tests, never real servers. When the project file lists sources explicitly (XcodeGen, or an Xcode project without synchronized folders), it regenerates or updates the project whenever a test moves in or out.
- **Apple apps** — recon now warns that the strict sandbox can block `xcodegen` and `xcodebuild` entirely, not just the test run: Foundation writes temp files under `getconf DARWIN_USER_TEMP_DIR` rather than `$TMPDIR`, and the sandbox denies writes there. For apps whose only harness is `xcodebuild`, the checklist offers an optional launch line that adds that folder to `sandbox.filesystem.allowWrite`. Tested on an XcodeGen iOS app under Claude Code 2.1.295 and Xcode 27: with the line, `xcodegen generate` and `xcodebuild build-for-testing` (DerivedData under `$TMPDIR`, `-disable-sandbox` for macro plugins) succeed in the sandbox. `xcodebuild test` still fails on iOS and macOS, because the simulator and `testmanagerd` are out of reach, so tests run through an alternative harness and the fix session reruns them.
- **Project MCP servers** — recon checks `.mcp.json` and `.claude/settings*.json` for servers that start without a prompt (`enableAllProjectMcpServers`, `enabledMcpjsonServers`). MCP tools run outside the sandbox, so the reply warns about them, the checklist says to disable them with `/mcp` before pasting the prompt, and the audit prompt tells the audit model not to call MCP tools.
- **Launch checklist** — the final step runs the contract check as well as `git status`; anything either prints is normalized by the fix prompt's first step.
- Marketplace metadata version bumped `2.11.2` → `2.11.3`.

## [2.11.2] - 2026-10-07

### Added

#### AI-Statusline Plugin (v1.4.1 → v1.5.0)

- **Sandbox indicator** — the Bash script template can show `Sandbox` in orange right after the effort level while Claude Code's Bash sandbox is on for the session, and hides it while the sandbox is off. New `SHOW_SANDBOX` toggle (default **off**). Existing status lines don't change; to add it, re-run `/statusline-wizard` and select it.
  - The status line payload has no sandbox field, so the script resolves `sandbox.enabled` the way Claude Code does, taking the first layer that sets it: managed settings (`managed-settings.json` and `managed-settings.d/`), `--settings` on the `claude` command line (inline JSON or a file path, read from the process found through `$CLAUDE_PID` or by walking up the process tree), `.claude/settings.local.json` at the repository root (the main checkout's root in a worktree) and then in the starting directory, `.claude/settings.json`, and the user's `settings.json` (respecting `CLAUDE_CONFIG_DIR`). A `/sandbox` change shows up on the next refresh.
  - On Linux and WSL2 the indicator stays hidden when `bwrap` or `socat` is missing, since the sandbox can't start without them. It can't read MDM profiles or server-managed settings, and the docs say to confirm with the `touch ~/sandbox-probe` check when it matters.
  - Native Windows has no sandbox, so the PowerShell template has no indicator, and both wizards leave the option out on Windows.
- `/statusline-wizard` and `/statusline-edit` — "Sandbox indicator" is a new option in the Project Display question. `/statusline-edit` leaves it out for scripts generated before 1.5.0 and points to `/statusline-wizard`.

### Changed

#### AI-CVP Plugin (v1.0.1 → v1.0.2)

- **Launch checklist** — the audit session now starts with one command instead of the `/sandbox` panel and Shift+Tab: `claude --model <audit-model-id> --permission-mode auto --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false,"failIfUnavailable":true}}'`.
  - The settings last one session and write nothing to `.claude/settings.local.json`.
  - Strict mode set through `--settings` makes the sandbox admin-required, so on Claude Code v2.1.285 or later the audited repo's own `.claude/settings.json` and `.claude/settings.local.json` can't loosen it (their `excludedCommands`, `allowWrite` and `allowedDomains` entries are ignored). The README's requirements now list v2.1.285.
  - `failIfUnavailable` makes Claude Code exit at startup instead of running commands unsandboxed when the sandbox can't start.
  - The checklist checks `/status` for `Command line arguments` instead of opening `/sandbox`, which can't change settings that come from the command line.
- **Shorter reply** — `/cvp-defense-audit` no longer prints the audit prompt in the conversation. The reply gives the path to each prompt, whether the audit prompt is on the clipboard, whether the ignore rule was added, an audit checklist, a fix checklist and the warnings. The fix checklist covers phase 3: quit the audit session, start `claude --model opus` unsandboxed, copy the fix prompt with the same clipboard tool, and paste it. Without a clipboard tool, both checklists say to open the file and copy it, replacing the `/copy` fallback, which needed the prompt in the conversation.
- Marketplace metadata version bumped `2.11.1` → `2.11.2`.

## [2.11.1] - 2026-10-07

### Fixed

#### AI-CVP Plugin (v1.0.0 → v1.0.1)

- **`/cvp-defense-audit` audit prompt** — the audit session no longer leaves failing proof tests across the source tree, where a commit would turn CI red. It still writes each test where the repo keeps its tests and runs it, then moves it to `docs/security/tests/` under the same repo-relative path with `.disabled` appended (for example `docs/security/tests/src/auth/session.cvp.test.ts.disabled`). Before finishing, it checks `git status` for strays. The report now always goes to `docs/security/<date>-cvp-security-audit.md`, and the summary table lists each finding's archived test.
- **`/cvp-defense-audit` ignore rule** — the planning session now adds `/docs/security/` to `.git/info/exclude` unless git already ignores it, so the report and archived tests stay out of commits in open-source repos and repos with confidential findings. The exclude file is never committed, so the repo carries no hint of the folder, and it applies to every worktree of the clone. The warnings list any files git already tracks under `docs/security/`. The rule also covers ai-security's reports in the same folder.
- **Launch checklist** — drops the `security/cvp-audit-<date>` branch, which would now hold nothing. Instead it asks for a clean `git status` before launch and adds a final `git status` check that should come back empty.
- **Fix prompt** — checks that `docs/security/` is ignored (adding the exclude line if it isn't) and archives any stray proof tests. It runs each proof from a temporary copy, and restores the proof test with `mv` (dropping `.disabled`, which removes the archived copy) on the fix branch. It never commits anything under `docs/security/`.
- Marketplace metadata version bumped `2.11.0` → `2.11.1`.

## [2.11.0] - 2026-10-07

### Added

#### AI-CVP Plugin (new — v1.0.0)

New plugin for planning a defensive security audit of code you own or are authorized to test. The audit itself runs in a strict sandbox on the strongest security-capable model you can use.

- `/cvp-defense-audit` — phase 1 of a three-phase audit. The planning session does read-only recon and writes a paste-ready audit prompt, a sandbox launch checklist and a fix prompt. The audit session (auto mode, `/sandbox` in strict mode) maps the attack surface, writes one failing test per finding as proof, and writes a report without fixing anything. The fixing session verifies each proof and ships each fix with its proof test as the regression test.
  - Asks what authorizes the audit (Cyber Verification Program enrollment, ownership or maintenance, or authorized third-party testing) and writes only that into the prompt. It never claims enrollment by default, and stops if there's no authorization.
  - Recon covers entry points, auth and tenancy, untrusted-input sinks, billing, secrets (names only), integrations, CI and supply chain, deploy config, the test harness and earlier audits. With `gh` signed in, it adds open Dependabot and code-scanning alerts and notes when either feature is disabled.
  - Picks 5 to 9 attacker goals from `attack-catalog.md` (web apps and APIs, Apple apps, libraries, CLIs and Claude Code plugins, Home Assistant integrations, static sites) and rewrites each in the repo's own actors, assets and files.
  - The prompt names the test framework, a file name with a `cvp` marker (`*.cvp.test.ts`, `test_cvp_*.py`) placed by the repo's convention, an existing test whose mocking to copy, libraries to mock because they call the network during verification, the single-file run command for each package, and a report path that matches the repo's audit naming. Recon also flags stale workspace builds and tests that bind localhost ports.
  - `fix-prompt-template.md` drives phase 3: re-run each proof outside the sandbox, propose checks for what code couldn't settle, triage, fix only what you pick on branches from the integration branch, never merge the audit branch, and update the report's status for each finding.
  - Saves both prompts to `~/.claude/cvp-audit-prompts/`, copies the audit prompt to the clipboard (`pbcopy`, `wl-copy`, `xclip` or `clip.exe`), and warns that the files map the attack surface and shouldn't be committed or posted.
  - Model-agnostic: `--model <audit-model-id>` fills in the launch line, and the skill refers to the planning, audit and fixing models by tier rather than by name.
- Marketplace metadata version bumped `2.10.0` → `2.11.0` (new plugin).

### Changed

- **CONTRIBUTING.md** — test a fix by loading the plugin from your clone with `claude --plugin-dir`, instead of adding the clone as a local marketplace. The flag needs no install, and for that session it replaces an installed copy of the same plugin.

## [2.10.0] - 2026-10-06

AEO and GEO are now separate plugins. AEO (Answer Engine Optimization) is about being *the* direct answer in a featured snippet, voice reply or answer box. GEO (Generative Engine Optimization) is about being cited and mentioned inside AI answers that draw on many sources. ai-geo's direct-answer checks moved to the new ai-aeo plugin, and both plugins were checked against vendor documentation current as of October 2026.

### Added

#### AI-AEO Plugin (new — v1.0.0)

- `/aeo-audit` — scores how ready answer pages are to be lifted as the direct answer, across nine weighted categories: answer-first formatting, question headings, concise definitions, real lists and tables, snippet eligibility controls, FAQ sections and structured data, voice and assistant readiness, answer trust signals, and technical accessibility. Writes timestamped reports to `docs/aeo-audit/` with a `README.md` index (trend indicators 📈 📉 ➡️), `latest.md` and an optional `.gitignore` entry, the same way `/geo-audit` does.
  - Searches every source of `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet` and Bing `nocache` / `noarchive`: meta tags, framework metadata APIs, header config, middleware and robots.txt. Lists the Search Console "Search generative AI" setting as a manual check.
  - Flags accordions that render answers only after a click (`{open && …}`, `v-if`, `{#if}`), main answers collapsed by default, and lists or tables drawn with divs.
  - Optional live URL check: fetches up to ten deployed pages to confirm answers are in the served HTML and to read the robots directives actually sent.
- `/aeo-fix` — applies fixes from the latest audit: safe fixes as one batch, a keep/remove/narrow question for every snippet control, answer-first rewrites and question headings drawn only from the page's own text, and refactors for click-to-load accordions and CSS-grid tables. Supports `--dry-run`.
- `/aeo-questions` — builds a question map from the site's own headings plus typed questions, a Search Console or Bing Webmaster Tools export, or web search suggestions (each linked to its source). Merges duplicates, assigns one owner page per question, and marks each answered first, buried, partial, missing or competing. `/aeo-audit` scores question coverage against the latest map.
- `/aeo-faq` — builds, updates or validates visible FAQ sections, with optional FAQPage or QAPage JSON-LD rendered from the same data. Drafts answers only from site content or the user, and keeps the main answers open.
- Marketplace metadata version bumped `2.9.0` → `2.10.0` (new plugin).

### Changed

#### AI-GEO Plugin (v1.1.1 → v1.2.0)

- **`/geo-audit` categories rebuilt around GEO** — AI Crawler Access, Technical AI Accessibility, Topical Authority (new), Original Research & Evidence (new), Expert Perspectives & Authorship, External Validation (new), Entity Clarity, Extractable Passages, Content Freshness, and llms.txt & Markdown Access. FAQPage, speakable, question headings, definitional openings and conversational heading checks moved to `/aeo-audit`. Scores aren't comparable with earlier audits; the index marks the first 1.2.0 run with 🔄 instead of a trend.
- **Three bot groups instead of two** — training crawlers, AI search indexers and user-triggered fetchers, plus Googlebot, Bingbot and Applebot. Adds AI search indexers from more vendors (Meta-WebIndexer, Amzn-SearchBot, MistralAI-Index, DuckAssistBot) and more user fetchers (meta-externalfetcher, Amzn-User, MistralAI-User, Google-Agent), and notes which fetchers say robots.txt may not apply to them.
- **Optional live URL check and web search** — `/geo-audit` can compare the deployed robots.txt with the repo (CDNs such as Cloudflare can add rules), confirm content is in the served HTML, and test responses to AI user agents. With web search it adds a dated off-site snapshot of brand mentions and reviews, which isn't scored.
- **Measuring citations** section in the report: Bing Webmaster Tools AI Performance, Search Console's Generative AI performance report, server logs and a fixed question panel.
- `/geo-fix` asks three separate robots.txt questions, offers to swap retired bot names for current ones, hands snippet controls to `/aeo-fix`, asks for sources behind unsourced statistics, scaffolds author pages and topic hubs, and prints off-site work as manual steps.
- `/geo-llms-txt` and the README now state that Google Search ignores `llms.txt`, that some coding tools read it, and that Lighthouse's agentic browsing audit checks for it. Markdown companion routes are optional and recommended only for developer docs.

### Fixed

- **ai-geo** — `/geo-audit` listed Google-Extended in its citation crawler table. It's a robots.txt token, not a crawler, and covers Gemini training and grounding in Gemini Apps and Vertex AI only. It doesn't affect Google Search, so it can't remove a site from AI Overviews or AI Mode; those follow `nosnippet`, `max-snippet`, `data-nosnippet`, `noindex` and the Search Console "Search generative AI" setting.
- **ai-geo** — a missing `llms.txt` could be rated Critical and the category carried 15% of the score. It's now Low (Medium for developer docs) at 5%, since Google says Google Search ignores the file and no AI search provider has said it uses it.
- **ai-geo** — removed claims that FAQPage and HowTo "are disproportionately cited by AI engines", that AI engines "prefer markdown", and that Markdown companions are "the single biggest citation-quality improvement". None has a primary source. Google stopped showing HowTo rich results in 2023 and FAQ rich results in May 2026.
- **ai-geo** — `Dataset` markup is described as used by Google Dataset Search rather than Search, and ClaimReview as being phased out of Google Search.
- **ai-geo** — FacebookBot and Omgilibot were dropped from the bot tables (Meta no longer documents FacebookBot; Omgilibot has no vendor documentation), and bot documentation links point to current pages (OpenAI's moved to developers.openai.com, Anthropic's to support.claude.com).
- **ai-geo** — skill examples quoted the owner's own sites and name; they now use generic examples.
- **ai-geo** — `/geo-llms-txt` asked a site-type question with six options (AskUserQuestion allows four) and offered `llms-full.txt` as an alternative to generating `llms.txt`. It now asks mode, full-text companion and site type as separate questions.
- **ai-geo** — JSON-LD examples escape `<` so text in the data can't close the script tag.

## [2.9.0] - 2026-10-06

### Added

#### AI-Slop Plugin (new — v1.0.0)

New plugin for auditing what a codebase shows its users: copy that reads as AI-written, layouts that read as templates, metadata built from boilerplate, and factual errors in all of them.

- `/slop-audit` — report-only audit of every user-facing surface: pages and shared layout, data files that feed cards, forms, emails, visible error text, legal pages, meta and OG tags, JSON-LD, `llms.txt`, app strings and store metadata, README and `--help` text.
  - Reads the project's voice rules, documented house style and earlier audit decisions first, so deliberate choices aren't flagged and settled questions aren't asked again.
  - Counts habits that repeat across the site (em dashes, the main tagline, triplets, "X, not Y" slogans, a word the copy leans on) and how many files each appears in.
  - Checks facts: legal pages against the third parties the code loads (and the live page's scripts when given a URL), figures and names that differ between pages, claims another page contradicts, and links or components that lead nowhere.
  - Scores each area 0–100, quotes every finding with `file:line` and a concrete fix, then ends with a fix plan, its defaults and numbered questions. Edits start only after you answer; it then removes old wording from every metadata surface, runs the project's checks, and records your answers as project rules.
  - Ships its checklist as `signals.md`: sentence, structure, claims, positioning, visual and metadata tells, plus a list of things not to flag.
- Marketplace metadata version bumped `2.8.1` → `2.9.0` (new plugin).

### Changed

- **Docs rewrite after an AI slop audit (October 2026)** — root README, CONTRIBUTING.md, SECURITY.md, every plugin README, all 15 marketplace and `plugin.json` descriptions, and several skill and agent descriptions.
  - Plugin descriptions now open with what the plugin does. "AI-powered" and the "Noun - Clause" shape are gone.
  - Removed emoji headings, "Built with ❤️" closers, "Time Savings" sections with estimated hours, and unmeasured percentages.
  - Cut repeated lists and IS / IS NOT blocks. Plugin READMEs are shorter, with a short "Limits" section where one is needed.
  - The GitHub repository description now matches the README tagline.
- **CONTRIBUTING.md** — covers bug reports and fix PRs only (new plugins and features start as an issue), and describes the current `skills/` and `agents/` layout instead of the removed `commands/` folder and `/plugins-scaffold`.
- **SECURITY.md** — only the latest marketplace release gets security fixes. Reports go through the contact form, with a reply within one business day.
- **CLAUDE.md** — new Documentation Style rules that record these decisions.
- Patch releases for the docs and fixes below: ai-accessibility 1.4.2, ai-ado 1.3.3, ai-compliance 1.0.1, ai-geo 1.1.1, ai-git 1.3.2, ai-knowledge 1.5.2, ai-modernize 1.1.1, ai-performance 1.2.2, ai-security 2.0.1, ai-seo 1.0.1, ai-statusline 1.4.1, ai-swift 1.0.2, ai-workflow 2.0.1, ai-writing 1.0.1. Every `plugin.json` keyword list now matches its `marketplace.json` entry.

### Fixed

- **ai-accessibility** — WCAG criteria counts in the README and in `/accessibility-audit` reports were WCAG 2.0's numbers. They now give 78 criteria for 2.1 and 86 for 2.2, with per-level counts. The touch-target rule is 24×24px at AA (SC 2.5.8) and 44×44px at AAA (SC 2.5.5), and focus-indicator contrast cites SC 1.4.11. The README now lists the 508 / WCAG 2.0 AA option and has a Plugin Details section.
- **ai-geo** — `/geo-fix` and the README used `anthropic-ai` and `Claude-Web`, which Anthropic doesn't document. They now use ClaudeBot, Claude-User and Claude-SearchBot. Google-Extended is described as a robots.txt control token, and "SearchGPT" is now ChatGPT search. `/geo-llms-txt` no longer calls the blockquote required (the llms.txt spec requires only the H1). The README documents `--dry-run` and the v1.1.0 discoverability checks.
- **ai-knowledge** — the auto memory comparison now matches the Claude Code docs: a `MEMORY.md` index plus topic files, the first 200 lines loaded at session start, and `/memory` for browsing.
- **ai-modernize** — removed "Claude Sonnet 2" (no such model) from the README and `/modernize-audit`, and dropped stale model names from its time estimates. The README's stack list names only stacks the skill checks.
- **ai-seo** — `nuxt-simple-sitemap` is now `@nuxtjs/sitemap`, TanStack Start's head component is `<HeadContent />`, and a dead web.dev link is gone.
- **ai-writing** — `/writing-humanize` counts 26 patterns, not 24, and its before/after example no longer invents a citation.
- **ai-git** — the README no longer says the plugin has agents or that `/git-commit-push` stages all changes. It stages the changed files by name and skips secrets.
- **ai-ado** — `/ado-init` had lost its README heading and was described as writing work item guidelines. The timesheet example totals now add up, and the roadmap of unbuilt skills is gone.
- **ai-performance** — the README no longer promises custom analysis templates or CI/CD gates.
- **ai-statusline** — "three categories" of display options is now four, and the examples use a current model label.
- **ai-swift** — removed unverified figures from the README and `/swift-preflight`.
- **ai-workflow** — added the missing `/workflow-ship` section and removed unbacked "syncs via /plugin update" claims. The README's check order matches what `/workflow-preflight` runs, and its `argument-hint` is quoted so YAML reads it as a string.
- **ai-compliance** — Apache 2.0's NOTICE requirement applies only when the project ships a NOTICE file, and BSD licenses use their SPDX names.

## [2.8.1] - 2026-09-10

### Added

#### AI-Statusline Plugin (v1.3.0 → v1.4.0)

- **Monthly spend budget segment** — both script templates (Bash and PowerShell) can now display month-to-date spend across all Claude Code sessions on this machine, e.g. `mo:$47.20/$2000 2.4%`, colored on the same thresholds as the rate-limit segment (green < 50%, yellow < 80%, red above). New `SHOW_SPEND_BUDGET` toggle (default **off**), `SPEND_LIMIT_USD` cap (default `0` = no cap, bare total), and `SPEND_RESET_DAY` / `SPEND_RESET_TIME` (default 1st of the month at 00:00 UTC, matching the Anthropic console) that control when the total rolls over. Existing status lines are unchanged after upgrading.
  - Built for Enterprise seats and API-billed accounts on a monthly spend cap: the host omits `rate_limits` entirely for those accounts, so the 5h/7d segment has nothing to show.
  - The host only reports the current session's `cost.total_cost_usd`, so each render records it to `~/.claude/statusline-spend/<period-start>/<session_id>` (one file per session so concurrent sessions never contend) and the segment sums the current billing period's files. Older period directories are pruned automatically.
  - All filesystem access is guarded: a read-only or missing home directory degrades to showing the current session's cost instead of breaking the status line.
  - Caveats documented where users will see them: counts only sessions rendered after install (no backfill), counts only this machine (not claude.ai web/desktop), and is Claude Code's local estimate, which will not match the Anthropic console.
- `/statusline-wizard` and `/statusline-edit` — rate limits and the new monthly spend budget now live in their own "Usage Limits" question (AskUserQuestion allows at most 4 options per question). Selecting the spend budget prompts for the monthly cap in USD and for when the cap resets (the wizard converts the console's local-time reset into UTC). The rate-limit option's description now explains that the segment is hidden on accounts without rolling windows.

### Changed

- **ai-statusline** script templates — the context percentage now prefers the host-provided `context_window.used_percentage` (newer Claude Code versions) and falls back to computing it from `current_usage` for older versions.
- **ai-statusline** docs — the rate-limit segment's silent absence on Enterprise/API spend-cap seats is now called out in the wizard's Important Notes, the plugin README, and the wizard option description, pointing those users at `SHOW_SPEND_BUDGET`.

## [2.8.0] - 2026-09-05

### Changed

#### AI-Security Plugin (v1.5.1 → v2.0.0) — upgrade notes

- **New report format:** Audits now save a readable Markdown report and a matching JSON file for scripts and automation. Tools that read the old report layout need updating; see the [report format guide](plugins/ai-security/skills/security-audit/references/artifacts.md). Previous reports can still be used for comparisons.
- **Scheduled audits:** Use `/ai-security:security-audit` for a full audit. The `security-auditor` helper now reviews assigned parts using the active model, without restarting the entire audit process.
- Audits respect the folders and exclusions you request. Missing Claude Code file-access settings no longer block an audit or count as an application security problem.
- **Clearer completion status:** The default audit reviews repository code with practical local checks; it does not require access to production or vendor dashboards. A finished review can still flag questions for follow-up. Unread code and other unfinished review work remain partial. New JSON reports use format 1.1; older 1.0 reports retain their original status rules.
- Shortened the plugin README and added plain-language command descriptions and examples.

### Added

- **Clearer evidence:** Reports record what was checked, what supports each suspected problem, and why a concern was confirmed or dismissed. Uncertain concerns and optional improvements are kept separate from confirmed problems.
- **More consistent checks:** Reviews use OWASP ASVS 5.0.0, an application security checklist, alongside checks specific to your project. Reports explain how serious each problem is and how urgently it should be addressed.
- **Comparisons with previous audits:** Reports explain whether earlier findings remain, were fixed, were dismissed, were combined, or still need review. Finding IDs stay the same when their importance changes.
- **Report checking:** A Python tool catches missing information and inconsistent records before formatting the report. Unfinished audits can still produce useful reports clearly labeled partial.

### Fixed

- Audit reports now open with a summary and table of contents, followed by findings and next steps. Full evidence stays in the matching JSON instead of filling the Markdown with thousands of checklist entries; a full technical export remains available on request.
- Audits use at most two reviewers at a time by default and explicitly finish or stop their workers. Completed agents should no longer be left waiting or restarted by courtesy messages.
- Audits must finish available, authorized checks before handing back a report. Unfinished reports explain actual blockers or reached limits; saving a valid report is no longer a stopping point while useful checks remain.
- Removed unsupported security scores and claims that a percentage of the application meets security standards.
- Removed an incomplete example for preventing **server-side request forgery (SSRF)**, where an attacker tricks an application into making requests to unintended destinations. Guidance now covers checking the actual destination, including redirects.
- Suggested fixes are labeled as proposals until applied and tested; optional precautions are no longer automatically counted as security flaws.

## [2.7.1] - 2026-07-15

### Added

#### AI-Statusline Plugin (v1.2.4 → v1.3.0)

- **Effort level segment** — both script templates (Bash and PowerShell) now display the session's reasoning effort level, read from the status line payload's `.effort.level` field. New `SHOW_EFFORT` toggle (default on) and a new "Effort level" option in the `/statusline-wizard` and `/statusline-edit` wizards.
  - Colors match the `/effort` picker: yellow (low), green (medium), light purple (high), dark purple (xhigh), per-character rainbow (max), and a purple-explosion `✦ultracode✦` treatment.
  - **Ultracode detection**: ultracode reports as plain `xhigh` in the payload, so the scripts detect it by scanning the session transcript (`.transcript_path`) for the most recent `/effort` command output. Sessions that never ran `/effort` fall back to the payload value.
  - The segment is hidden entirely when the current model doesn't support the effort parameter (the field is absent from the payload).
- `/statusline-edit` — handles scripts generated by older plugin versions that lack `SHOW_EFFORT`: the option is omitted from the wizard and the user is pointed at `/statusline-wizard` to regenerate with effort support.

### Fixed

- **ai-statusline** script templates — token math no longer crashes when usage token fields are `null` (jq addition of `null + number` errored; now defaulted with `// 0`) or when `context_window_size` is missing/zero (was a division-by-zero); the progress bar percentage is now clamped at 100%.
- **ai-statusline** Bash template — the rate-limit segment no longer disappears when only one of the 5h/7d windows is present in the payload; each window now renders independently, matching the PowerShell template's existing behavior.

## [2.7.0] - 2026-07-09

Marketplace-wide "aged-out" audit against native Claude Code features (July 2026): native Dynamic Workflows, auto memory (per-project MEMORY.md), native `/code-review` / `/security-review`, native `/statusline`, and Tool Search (deferred MCP schemas). Every plugin was inventoried; superseded functionality was removed or repositioned, and staleness bugs found along the way were fixed.

### Removed

#### AI-Workflow Plugin (v1.5.0 → v2.0.0) — BREAKING

- `/workflow-plan-phases` and `/workflow-implement-phases` removed — superseded by Claude Code's native Dynamic Workflows (a JavaScript runtime that orchestrates subagent fan-out with per-agent token tracking and budgets, GA ~v2.1.154). The manual 30-50k-token phase sizing and `.claude/phase-coordination/` orchestration these skills implemented is now handled natively at runtime. Both skills remain available in git history.
- README reframed around the four maintained skills: `/workflow-preflight`, `/workflow-ship`, `/workflow-principles`, `/workflow-rules`; token-budget marketing claims removed; obsolete keywords (`planning`, `phases`, `orchestration`, `sub-agents`) dropped from manifests.

#### AI-Learn Plugin (removed)

- Entire plugin removed (was v1.1.0) — Claude Code's built-in **Learning** output style (`/config` → "Output style" → "Learning") natively provides the collaborative mentor / learn-by-doing mode (with `TODO(human)` markers), and an **Explanatory** style ships alongside it. Removed outright rather than deprecated so `/learn` and `/learn-review` no longer appear in the slash-command dropdown; the plugin remains available in git history. Marketplace now lists 14 plugins.

### Changed

#### AI-Knowledge Plugin (v1.5.0 → v1.5.1)

- Repositioned against Claude Code's native auto memory (default since ~v2.1.59): the README no longer premises that knowledge is lost between sessions. New "How This Differs from Claude Code's Auto Memory" section — auto memory is Claude's personal per-machine notebook; this KB is deliberate, curated, git-versioned, team-shared institutional knowledge with an Obsidian-compatible graph and query tooling. No skills changed or deprecated.

#### AI-Security Plugin (v1.5.0 → v1.5.1)

- Rewrote the dated "Why Not Just Use `/security-review`?" README section as an honest complement-not-compete comparison: native `/security-review` and `/code-review` (effort tiers, `--fix`/`--comment`, cloud ultra mode) cover core detection; this plugin adds archived OWASP-mapped audit reports, deployed-site dependency scanning without source access, `.claude/settings.json` hardening, and npm supply-chain protection.
- `/security-scan-dependencies` — noted that MCP tool schemas (Context7) are deferred by default under Tool Search and may need on-demand loading.

#### AI-Statusline Plugin (v1.2.3 → v1.2.4)

- Repositioned as an enhancement over Claude Code's native `/statusline` command: the plugin's value is the visual progress bar with color thresholds, 5h/7d rate-limit display, cost/duration segments, granular toggles, and the `/statusline-edit` flow.
- Removed vestigial "requires Claude Code 2.1.80+" caveats; refreshed "Claude Opus 4.6" example labels to "Claude Opus 4.8".

#### AI-Git Plugin (v1.3.0 → v1.3.1)

- `/git-pr-codex-loop` — added positioning note: native `/code-review` (`--fix`, `--comment`, ultra) covers automated review-and-fix loops without external dependencies; this skill remains the right tool for repos standardized on OpenAI's Codex Code Review bot.

#### AI-Accessibility (v1.4.0 → v1.4.1), AI-Performance (v1.2.0 → v1.2.1), AI-Swift (v1.0.0 → v1.0.1)

- Auditor agents (`accessibility-auditor`, `performance-auditor`, `swift-release-auditor`) reframed from "use when context is saturated" to automated/unattended domain reviews.

### Added

#### AI-Modernize Plugin (v1.0.0 → v1.1.0)

- `modernize-auditor` agent — the `/modernize-audit` and `/modernize-scan` skills delegated to an `ai-modernize:modernize-auditor` subagent that never shipped; the agent now exists (mirrors the `security-auditor` pattern, `model: inherit`), fixing the broken delegation in both skills.

### Fixed

- **ai-git** `/git-commit-push-pr` — removed the hardcoded `Co-Authored-By: Claude Opus 4.6` commit trailer; commits now carry no Claude attribution, consistent with `/git-commit-push` and repo convention.
- **ai-workflow** `/workflow-ship` — removed the same hardcoded `Claude Opus 4.6` commit trailer.
- **ai-statusline** `/statusline-wizard` — fixed a broken reference to the renamed `statusline-setup` skill (setup workflow now resolves inline).
- **ai-security** `/security-scan-dependencies` — report template scanner version updated from the stale `v1.4.0`; `/security-supply-chain` frontmatter fixed `minimumReleaseAge` → `minimum-release-age`.
- **ai-performance** `performance-auditor` agent — fixed typos ("it's methodology" → "its methodology"; skill reference `performance-auditing` → `performance-audit`).
- **ai-geo** — README version drift corrected (badge and Plugin Details now match plugin.json v1.1.0).
- **ai-ado** (v1.3.1 → v1.3.2) — README now documents the shipped `/ado-work-items` skill (7 skills, previously 6 listed).

### Audit Notes

- Verified against official docs as still current with no native overlap: ai-learn, ai-writing, ai-compliance, ai-seo, ai-geo, ai-swift, ai-ado, ai-accessibility, ai-performance skills. No hardcoded API model IDs, token-budget claims, or removed-command references remain in any plugin.

## [2.6.0] - 2026-06-13

### Added

#### AI-Git Plugin (v1.2.0 → v1.3.0)

- `/git-pr-codex-loop` — Opens a PR for the current branch, then loops on Codex Code Review until it comes back clean: resolves each finding locally, replies, and re-requests review. Never merges — the human makes the final merge decision.
  - Opens or finds the PR for the current branch (refuses to run on `main`/`master`), matching the PR attribution style of `/git-commit-push-pr`.
  - Waits for CI to go green before involving Codex, then waits for the `chatgpt-codex-connector` bot's review to fully *settle* — Codex acknowledges with a 👀 reaction (which means "received," not "done") then trickles findings in as several comments seconds apart, so the loop waits for the summary comment (or a quiet window with no new comments) before resolving, rather than acting on the first comment.
  - Recognizes Codex's no-comment "all clear": when it finds nothing, Codex may post no review and instead add a 👍 reaction to the PR description — the loop reads the issue reactions API and treats that as a clean pass.
  - Resolves every finding worst-priority-first (P0 → P1 → P2): fixes correct findings, commits, pushes, and replies on each thread with the commit SHA + what changed (no per-thread `@codex` tag), then posts a single `@codex review` comment once the whole pass is handled — triggering exactly one fresh review instead of one per comment.
  - Reads and resolves review threads via the GitHub GraphQL API (`reviewThreads` query + `resolveReviewThread` mutation), since the REST comments endpoint cannot mark a thread resolved.
  - Loops Steps 4–5 until a pass comes back clean — Codex's summary verdict or a 👍 on the PR description — and every thread is resolved, then hands back the PR URL and a summary.
  - Guardrails: never merges, never force pushes, never opens extra PRs, makes every fix locally with Claude (never delegates to Codex — the only mention it posts is one `@codex review` per pass), stops and tells the user to enable Automatic reviews if Codex never picks the PR up, and pushes back with a reasoned reply when Codex is wrong instead of churning the diff.
- Marketplace metadata version bumped `2.5.0` → `2.6.0` (significant addition).

## [2.5.0] - 2026-06-03

### Added

#### AI-Swift Plugin (new — v1.0.0)

New plugin for Swift / iOS / macOS development whose primary job is to catch release blockers **before** they reach Xcode Cloud or TestFlight, plus reusable Swift 6 + SwiftUI quality checks. Lessons are encoded portably from a real Swift 6 / SwiftUI / XcodeGen project; no project-specific identifiers are hardcoded. Every check probes the target project's shape first (XcodeGen vs plain `.xcodeproj` vs SwiftPM vs Tuist; iOS / macOS / both; Xcode Cloud or not) and only runs the applicable checks.

- `/swift-preflight` — flagship read-only release-readiness audit. Probes project shape, then runs 8 checks and prints a categorized PASS / WARN / FAIL report with `file:line`, remedy, and a one-line "why":
  1. XcodeGen pbxproj drift from `project.yml` (bundle id / team / signing hand-edited in Xcode that a CI regen would silently revert)
  2. Static build number with no `CI_BUILD_NUMBER` stamping (duplicate-build-number TestFlight rejection) plus double-increment warning
  3. Missing / malformed `ci_scripts/ci_post_clone.sh` on a generator project (stale pbxproj on CI)
  4. macOS App Store readiness — ITMS-90242 (`LSApplicationCategoryType`), ITMS-90296 (App Sandbox), ITMS-90683 (privacy usage strings), `ITSAppUsesNonExemptEncryption` export-compliance prompt, `network.client`, hardened runtime
  5. CI test isolation — tests touching the real keychain / `UserDefaults.standard` / disk / network that break on a headless runner (`errSecAuthFailed` -25293); prescribes the seam+fake and catch-all probe+`XCTSkipIf` remedies
  6. Ad-hoc signing carrying capability entitlements that require a development certificate; plus the harmful `keychain-access-groups` own-item footgun
  7. Scheme sharing + flaky-UITest release gating (unit-test-only CI scheme recommendation)
  8. Local gate health (verify script / format-lint config presence; stale-SourceKit guidance)
- `/swift-diagnose` — reactive failure diagnostician. Paste a red Xcode Cloud log, an ITMS rejection email, or a bare code (`ITMS-90296`, `-25293`) and get the root cause + exact fix, grounded in the actual repo files when present. Catalog covers ITMS-90242/90296/90683, `errSec` keychain codes (-25293/-25300/-25308/-34018), "entitlements that require signing with a development certificate", duplicate build numbers, missing ci_scripts / unshared schemes, stale SourceKit, and the Swift 6.3.x `Binding(get:set:)` IRGen crash.
- `/swift-ci-scaffold` — opt-in writer (diff + confirm). Generates `ci_scripts/ci_post_clone.sh` (`set -e`, `cd "$CI_PRIMARY_REPOSITORY_PATH"`, `brew install xcodegen`, guarded `CI_BUILD_NUMBER` stamp before generate), proposes a unit-test-only CI scheme in `project.yml`, prints the exact App Store Connect workflow checklist (workflows live in ASC, not the repo), and optionally installs a `.githooks/pre-push` gate. Refuses to add a CI regen step when `project.yml` is missing the real bundle id / team (which regen would revert).
- `/swift-verify` — portable local gate. Detects the build system and runs `xcodegen generate` (if applicable) → `swiftformat --lint` → `swiftlint --strict` → `xcodebuild test` on the cheapest valid destination (macOS for pure-Swift), or `swift build` / `swift test` for SwiftPM. `--fix` lets SwiftFormat rewrite; `--no-test` skips the build/test stage. Swift-native specialization of `/workflow-preflight`, not a duplicate.
- `/swift-concurrency-review` — read-only Swift 6 strict-concurrency + SwiftUI idiom review of changed files: Sendability across actor boundaries, `@MainActor` witness vs nonisolated requirement, Combine/`ObservableObject` reintroduction, force-unwraps, `#Predicate` macro limits, the 6.3.x `Binding` IRGen crash, missing `#if os()` guards, and unjustified `@unchecked Sendable` / `nonisolated(unsafe)` escape hatches. Defers general bug-finding to `/code-review`.
- `swift-release-auditor` agent — runs `/swift-preflight` in fresh context for automated release-readiness review (mirrors `security-auditor` / `performance-auditor`).
- Marketplace metadata version bumped `2.4.3` → `2.5.0` (significant addition).

## [2.4.3] - 2026-04-28

### Added

#### AI-Workflow Plugin (v1.4.0 → v1.5.0)

- `/workflow-rules` — Add, remove, or list curated **behavior rules** in CLAUDE.md (cross-project, picked from a shipped library). Distinct from `/workflow-principles` (project-specific coding standards): `/workflow-rules` controls *how Claude behaves* (PR/commit hygiene, scope discipline, communication style) and is identical across projects.
  - Interactive flow via `AskUserQuestion`: choose Add / Remove / List / Cancel.
  - Cross-platform target resolution — user-level `~/.claude/CLAUDE.md` (POSIX) or `%USERPROFILE%\.claude\CLAUDE.md` (Windows), or project-level `./CLAUDE.md`.
  - Each installed rule is wrapped in `<!-- workflow-rules:id=<id> -->` comment markers so adds are idempotent and removes are precise — even after the user edits the rule's title.
  - Already-installed rules are filtered from the add picker; multi-select lets the user install many at once.
  - Diff preview + explicit confirm before any write. Never auto-creates `~/.claude/CLAUDE.md` without asking.
  - Library ships lean (10 rules across PR & Commit Hygiene, Scope Discipline, Communication Style); syncs across machines via `/plugin update`.

## [2.4.2] - 2026-04-21

### Fixed

#### AI-Knowledge Plugin (v1.4.0 → v1.5.0)

- All `/kb-*` skills — Fixed `last-updated` frontmatter bug where Claude would infer the date by incrementing the existing value (often producing a date in the future) instead of checking what today actually is. Every skill that writes `created` / `last-updated` now mandates resolving today's date once at the start of its write phase by running a shell command and reusing that single value for every write. Guessing, inferring, and incrementing are explicitly forbidden.
- All `/kb-*` skills — Cross-platform date resolution documented for each writing skill: `date +%Y-%m-%d` on macOS / Linux / WSL / Git Bash, `Get-Date -Format 'yyyy-MM-dd'` on Windows PowerShell, `powershell -NoProfile -Command ...` fallback for cmd.exe, plus Node / Python portable fallbacks. Skills walk the list until one returns a valid `YYYY-MM-DD` string, making them reliable on both macOS and Windows environments.
- All `/kb-*` skills — `last-updated` is now only bumped when the file's content actually changed. Untouched files are no longer rewritten, so drive-by date bumps during cross-reference and index passes stop happening. `/kb-upgrade` explicitly notes that already-compliant files must not be rewritten on re-runs.
- Skills covered: `kb-learn`, `kb-add`, `kb-harvest`, `kb-discover`, `kb-query`, `kb-import`, `kb-absorb`, `kb-organize`, `kb-prune`, `kb-remove`, `kb-ingest`, `kb-upgrade`, `kb-init`.

## [2.4.1] - 2026-04-18

### Changed

#### AI-GEO Plugin (v1.0.0 → v1.1.0)

- `/geo-audit` — Category 1 (llms.txt Protocol Compliance) extended with four discoverability-signal checks:
  - `<head>` `<link rel="alternate" type="text/markdown" title="llms.txt" href="/llms.txt">` presence (Medium if missing)
  - `sitemap.xml` `<url><loc>/llms.txt</loc></url>` entry presence (Medium if missing)
  - `robots.txt` `# LLM index: https://<domain>/llms.txt` comment presence (Low / informational)
  - Public directory submission to llmstxt.site and directory.llmstxt.cloud (Low / manual — never auto-detected, never Critical/High)
- `/geo-audit` — "What is GEO?" report section gained "On llms.txt discovery" subsection documenting that no major LLM provider (OpenAI, Anthropic, Perplexity, Google) has publicly committed to reading `llms.txt` as a first-class signal, marked 🧪 experimental, and listing the five stackable weak signals (root serve, head link, sitemap entry, robots comment, directory submission)
- `/geo-fix` — Safe-auto fix bucket extended with three new fixes:
  - Inject `<link rel="alternate" type="text/markdown" href="/llms.txt">` via the framework-idiomatic head API (Next.js Metadata API `alternates.types`, Nuxt `useHead`, Vue + `@unhead/vue`, Astro layout, SvelteKit `<svelte:head>`, Remix `meta` export, vanilla `<head>`) — skip if already present
  - Add `/llms.txt` entry to sitemap (Next.js `app/sitemap.ts` push, static `sitemap.xml` `<url>` block with `changefreq=monthly` + `priority=0.5`, `@nuxtjs/sitemap` `urls`, `@astrojs/sitemap` `customPages`) — skip if already present
  - Add `# LLM index: https://<domain>/llms.txt` comment to `robots.txt` with auto-derived domain (falls back to prompt when unresolvable) — skip if already present
- `/geo-fix` — New informational bucket for non-automatable actions: terminal summary prints directory-submission URLs (`llmstxt.site/submit`, `directory.llmstxt.cloud`) as a manual next step (web forms, never automated)
- `/geo-fix` — Terminal summary gained "llms.txt discovery signals" block (head link / sitemap entry / robots comment statuses + build-order warning)
- `/geo-fix` — Build-order rule codified: when both `llms.txt` and the sitemap are build-time generated, the llms.txt generator MUST run before the sitemap so the sitemap can read llms.txt's mtime (warn with suggested reordering rather than silent reshuffle)
- `/geo-llms-txt` — New Step 7.5 "Wire Discoverability Signals (post-write)" offers to add the head `link[rel=alternate]` hint, sitemap `/llms.txt` entry, and `robots.txt` comment after writing llms.txt, with framework-specific code for Next.js, Nuxt, Vue + `@unhead/vue`, Astro, SvelteKit, Remix, and vanilla HTML (each step skipped silently if already present or not applicable)
- `/geo-llms-txt` — New "Build pipeline — order dependency" subsection documents per-framework rules: Next.js Metadata API has no order issue, Astro endpoint vs static differ, Nuxt prebuild hook, Vite/SvelteKit/Remix/TanStack Start warn-don't-reshuffle
- `/geo-llms-txt` — Terminal summary gained discoverability-signal statuses and manual directory-submission URLs
- `/geo-llms-txt` — Quality Assurance Checklist extended with post-write wiring items, build-order surfacing, and directory-submission printout
- Existing LLM Knowledge Gap Corrections, examples, and Quality Assurance Checklist items preserved across all three skills — `llms-full.txt` generator logic unchanged

## [2.4.0] - 2026-04-17

### Added

#### AI-GEO Plugin (v1.0.0) — New plugin

- `/geo-audit` — Comprehensive Generative Engine Optimization audit across 10 weighted categories (llms.txt Protocol, AI Crawler Access, Content Structure, Citation-Worthiness, AI-Friendly Structured Data, Semantic Chunking, Content Freshness, Entity Optimization, Conversational Alignment, Technical AI Accessibility)
  - Auto-detects framework (Next.js, Nuxt, TanStack Start, Astro, SvelteKit, Remix, vanilla HTML) and emits framework-idiomatic guidance (static/SSR preference, markdown-accessible routes, modified-time propagation)
  - Parses `robots.txt` and distinguishes training crawlers (GPTBot, ClaudeBot, Google-Extended, CCBot, Applebot-Extended, Bytespider, Amazonbot, FacebookBot, Omgilibot) from answer/citation crawlers (ChatGPT-User, OAI-SearchBot, PerplexityBot, Perplexity-User, Claude-Web) — reports per-bot status and flags inconsistent patterns rather than prescribing a blanket policy
  - Validates `llms.txt` and `llms-full.txt` against the llmstxt.org spec (H1 title, blockquote description, markdown throughout, `.md`-companion preference, staleness vs content mtime)
  - Citation-readiness score 0-100 with grade (A+ through F) and per-category weighted scoring
  - Experimental 🧪 markers for emerging practices (speakable specification, DefinedTerm, ClaimReview, markdown companion routes) so users can apply judgment
  - Context7 MCP integration for up-to-date llms.txt spec, AI bot docs (OpenAI, Anthropic, Google, Perplexity), and latest Schema.org types; falls back to training data with explicit mode indicator and liberal 🧪 flagging
  - Timestamped reports in `/docs/geo-audit/` preserve history (never overwrites); generates `README.md` index with trend indicators (📈 📉 ➡️) and `latest.md` copy
- `/geo-fix` — Safe remediation workflow that reads `latest.md` and applies fixes in four tiers: safe-auto (add `dateModified` + `article:modified_time`, migrate microdata/RDFa to JSON-LD, wrap existing Q&A prose with FAQPage schema), intent-requiring (separate training-bot and citation-bot prompts before modifying `robots.txt`; emits framework-idiomatic output like `app/robots.ts` for Next.js), content-requiring (prompts for `sameAs` URLs, TL;DR copy, FAQ extraction — never fabricates identity URLs), larger refactors (SSR migration, paragraph restructuring, conversational heading rewording). Supports `--dry-run`.
- `/geo-llms-txt` — Generate, update, or validate `llms.txt` and `llms-full.txt`. Four modes (generate/update/validate/full-text companion). Framework-aware placement (`public/llms.txt` or route handlers for Next.js, Nuxt, Astro, SvelteKit, TanStack Start, Remix, vanilla). Validation covers spec compliance, link reachability, `.md`-companion opportunities, file size, and staleness vs content source mtime. Suggests markdown companion routes (`.md` suffix) as the single biggest post-llms.txt citation-quality improvement.
- LLM knowledge-gap corrections baked into every skill prompt: GEO is not SEO; distinguish training bots from citation bots (never blanket-block); `llms.txt` is a real emerging standard; AI engines prefer markdown; FAQPage and HowTo schemas are disproportionately cited; recency matters more than for traditional SEO; SSR/static is critical (many AI crawlers don't execute JS); entity `sameAs` disambiguation is high-value (Wikipedia/Wikidata, LinkedIn, GitHub, Crunchbase, ORCID); never cloak or serve different content to AI bots; mark emerging practices with 🧪; never fabricate `sameAs` URLs
- Cross-references the companion `ai-seo` plugin — `ai-geo` reports direct users to `/seo-audit` for traditional search coverage; overlap areas (structured data, semantic HTML, authoritativeness signals) are cross-referenced rather than duplicated

#### AI-SEO Plugin (v1.0.0) — New plugin

- `/seo-audit` — Comprehensive modern SEO audit across 9 weighted categories (deprecated patterns, modern meta tags, semantic HTML, structured data, performance signals, accessibility, URL structure, security headers, framework best practices)
  - Auto-detects framework (Next.js, Nuxt, TanStack Start, Astro, SvelteKit, Remix, vanilla HTML) and emits framework-idiomatic guidance
  - Context7 MCP integration for up-to-date Google Search Central, Schema.org, and framework SEO API docs; falls back to training data with explicit mode indicator
  - Timestamped reports in `/docs/seo-audit/` preserve history (never overwrites); generates `README.md` index with trend indicators (📈 📉 ➡️) and `latest.md` copy
  - Per-category 0-100 scores and overall grade (A+ through F)
- `/seo-fix` — Safe remediation workflow that reads `latest.md` and applies fixes in three tiers: safe-auto (deprecated tag removal, `rel="noopener noreferrer"`, `loading="lazy"`, lang/viewport/charset), content-requiring (proposes meta descriptions/titles with confirm-or-edit), larger refactors (div-soup → semantic HTML5). Supports `--dry-run`.
- `/seo-schema` — JSON-LD structured data generator and validator for Article, BlogPosting, Product, Organization, LocalBusiness, FAQPage, BreadcrumbList, Event, HowTo, Recipe, VideoObject, Person, Course, JobPosting, and composite `@graph` structures. Emits framework-idiomatic injection code.
- LLM knowledge-gap corrections baked into every skill prompt: never generate `<meta name="keywords">` (deprecated 2009, Bing spam signal), never recommend X-UA-Compatible, IE conditionals, jQuery, `float` layouts, `<b>`/`<i>` for emphasis, XHTML doctype, FID optimization (replaced by INP March 2024), or separate mobile subdomains; always prefer JSON-LD over microdata/RDFa

## [2.3.4] - 2026-04-06

### Added

#### AI-Knowledge Plugin (v1.4.0)

- `/kb-upgrade` - Comprehensive KB upgrade command (replaces `/kb-obsidian`)
  - Absorbs all `/kb-obsidian` functionality (Related body links, global learnings migration, index/log creation, folder reorganization)
  - Standardizes "When to Load" column from vague free-text to structured `scope-globs — keywords` format for efficient dynamic context loading
  - Updates CLAUDE.md preamble with explicit 4-point matching instructions (pinned, scope patterns, keywords, _index.md fallback)
  - Adds loading notification directive — Claude now tells users when loading KB files (e.g., `📖 Loading KB: api-conventions.md`)
  - Adds Scope column to `_index.md` All Pages table for routing context
  - Suggests scope patterns for KB files with empty/missing scope
  - Re-runnable and idempotent — safe to run after plugin updates or any time to verify KB health

- `/kb-load` - Manually load KB articles into the current conversation
  - Accepts filename, topic name, or tag filter (e.g., `/kb-load api-conventions`, `/kb-load tag:testing`)
  - Interactive picker when no argument provided
  - Offers to follow `related` cross-references one level deep
  - Displays `📖 Loading KB:` notifications consistent with automatic loading
  - Use when Claude hasn't automatically loaded a KB file you need mid-conversation

### Changed

#### AI-Knowledge Plugin (v1.4.0)

- **Structured "When to Load" format** — All KB commands now generate structured loading criteria: backtick-wrapped scope globs + topic keywords (e.g., `` `src/api/**`, `*.controller.ts` — api, rest, middleware ``). This replaces vague free-text like "When working in packages/api/" and enables efficient dynamic context matching.
- **`scope` field supports arrays** — The frontmatter `scope` field now accepts both a single string (`scope: "src/api/**"`) and an array of strings (`scope: ["src/api/**", "*.controller.ts"]`) for matching multiple file patterns.
- **CLAUDE.md preamble improved** — The Knowledge Base section preamble now includes explicit instructions for how Claude should match scope patterns, keywords, and pinned entries, plus a loading notification directive.
- **`_index.md` includes Scope column** — The All Pages table now has a Scope column showing each article's file path matching patterns.
- **`kb-organize` refreshes "When to Load"** — Reorganizing files now also regenerates the "When to Load" column values from frontmatter.

### Removed

- `/kb-obsidian` — All functionality absorbed into `/kb-upgrade`

## [2.3.3] - 2026-04-05

### Added

#### AI-Knowledge Plugin (v1.3.0)

- `/kb-query` - Query the knowledge base and synthesize answers from multiple KB files
  - Reads `_index.md` to find relevant pages, then drills into individual articles
  - Synthesizes comprehensive answers with `[[wiki-link]]` citations to source KB files
  - Flags contradictions between KB files and gaps in coverage
  - Offers to **file answers back as new KB articles** so explorations compound into the knowledge base
  - Filed answers include `type: synthesis`, `query`, and `sources` frontmatter fields for provenance
  - Inspired by Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern

- `/kb-obsidian` - One-time migration to upgrade and make an existing KB Obsidian-compatible
  - Adds `## Related` body sections with `[[wiki-links]]` for Obsidian graph view and link navigation
  - Migrates inline `### Global Learnings` from CLAUDE.md to `docs/kb/_global-learnings.md`
  - Generates `docs/kb/_index.md` — a categorized catalog of all KB articles with one-line summaries
  - Creates `docs/kb/_log.md` — a chronological record of KB operations
  - Offers to reorganize flat KB files into category folders (architecture/, conventions/, testing/, etc.)
  - Audits and fixes frontmatter health issues
  - Fully backwards-compatible — handles all older KB structures

- **`_index.md` — Knowledge Base Index** - Auto-generated, pinned catalog of all KB articles organized by category with one-line summaries. The LLM reads this first to find relevant pages before drilling into individual articles. Created by `/kb-init` and maintained by all `/kb-*` commands.

- **`_log.md` — Activity Log** - Append-only chronological record of KB operations (ingests, queries, prunes, etc.). Provides a timeline of how the knowledge base evolved. Created by `/kb-init` and appended to by all `/kb-*` commands.

- `/kb-organize` - Standalone folder reorganization for existing flat KB structures
  - Analyzes flat KB files and suggests category folders based on tags and content
  - Common categories: architecture/, conventions/, testing/, tools/, external/, domain/
  - Preview-first — shows all proposed moves before executing
  - Updates CLAUDE.md table paths and `_index.md` after reorganization
  - Does not modify `[[wiki-links]]` (they resolve by name, not path)

### Changed

#### AI-Knowledge Plugin (v1.3.0)

- **Subfolder organization** - All `/kb-*` commands that create new KB files now prefer placing them in category subfolders (e.g., `docs/kb/architecture/`, `docs/kb/conventions/`, `docs/kb/testing/`) instead of flat in the root. Existing flat structures continue to work. `/kb-obsidian` offers to reorganize flat files into folders.
- **Obsidian-compatible Related Links** - All `/kb-*` commands that create or update KB files now maintain a `## Related` section at the end of the file body with `[[wiki-links]]` mirroring the `related` frontmatter field. Obsidian does not parse frontmatter values as navigable links, so body links are required for graph view edges and link navigation to work.
- **Global Learnings as dedicated KB file** - Global learnings are now stored in `docs/kb/_global-learnings.md` (a pinned KB file) instead of inline in CLAUDE.md's `### Global Learnings` section. This makes global learnings visible in Obsidian, searchable as a regular KB file, and eliminates duplication. Affects `/kb-init`, `/kb-learn`, `/kb-add`, `/kb-search`, `/kb-list`, and `/kb-prune`. Existing inline global learnings are preserved and can be migrated with `/kb-obsidian`.
- **Index and log maintenance** - All `/kb-*` commands that modify KB files now update `_index.md` and append to `_log.md` (conditionally — only if the files exist, for backwards compatibility).
- **Cross-reference cleanup now includes body links** - `/kb-remove` and `/kb-prune` now update both `related` frontmatter AND `## Related` body sections when cleaning up cross-references.
- **kb-prune detects out-of-sync Related sections** - Cross-reference integrity checks now flag KB files where the `## Related` body section doesn't match the `related` frontmatter.
- **kb-list and kb-search detect legacy global learnings** - These commands now check for and flag legacy inline `### Global Learnings` sections in CLAUDE.md, suggesting `/kb-obsidian` for migration.

## [2.3.2] - 2026-04-03

### Added

#### AI-Knowledge Plugin (v1.2.0)

- `/kb-harvest` - Harvest knowledge from external sources into the KB system
  - Supports local directories, individual files, glob patterns, and web URLs as sources
  - Scans sibling git repos (e.g., `C:/Source/*/docs/**/*.md`) for cross-repo knowledge ingestion
  - Fetches and distills web pages (wikis, Confluence, internal docs) via URL
  - Auto-tags with `module:{name}` based on source directory structure for filtering by module
  - Tracks provenance via `source` frontmatter field (original path or URL) for future re-harvesting
  - Discovery report with pre-checked/unchecked sources and batch selection
  - Per-article content preview and approval before writing to disk
  - Distills content into concise, actionable KB format (not copy-paste)
  - Detects topic overlap with existing KB files and proposes appending
  - Registers entries in CLAUDE.md Knowledge Base table
  - Preserves all source files and URLs (never modifies originals)

- `/kb-discover` - Analyze source code to extract implicit knowledge into KB articles
  - Mines source code for architecture patterns, naming conventions, API contracts, error handling, config structures, data models, and testing patterns
  - Supports targeted analysis (specific directories), focus areas (topics), or full codebase scan with intelligent sampling
  - Auto-detects tech stack and prioritizes analysis targets accordingly
  - Groups findings into coherent KB articles (not raw category dumps)
  - Per-article draft preview and approval — user sees the full distilled content before any file is written
  - Tracks provenance via `discovered-from` frontmatter field for re-discovery when code evolves
  - Evidence-based only — requires observed repetition, never fabricates patterns from single occurrences
  - Right-sizes articles to 50-150 lines of distilled rules for context-friendly loading

## [2.3.1] - 2026-04-03

### Added

#### AI-Knowledge Plugin (v1.1.0)

- `/kb-ingest` - Ingest specific markdown files from anywhere in the project into the KB, as a targeted alternative to `/kb-absorb`
  - Accepts one or more file paths (e.g., `/kb-ingest docs/api-guide.md`)
  - Distills content into concise, actionable KB format with proper frontmatter
  - Detects overlap with existing KB files and proposes appending instead of creating duplicates
  - Registers new KB entries in the CLAUDE.md Knowledge Base table
  - Preserves source files (never modifies or deletes originals)

### Fixed

#### AI-Knowledge Plugin (v1.1.0)

- **Fixed pinned file loading instruction in kb-init** - The CLAUDE.md template previously told Claude to check frontmatter of every KB file to find pinned entries, defeating the purpose of the dynamic loading table. Now correctly directs Claude to use the "When to Load" column ("Always (pinned)") as the source of truth

## [2.3.0] - 2026-04-02

### Added

#### AI-Knowledge Plugin (v1.0.0) - NEW PLUGIN

- **New plugin for knowledge base management** - Capture conversation learnings, maintain topic-specific KB files, and dynamically reference institutional knowledge in CLAUDE.md
- `/kb-init` - Initialize the Knowledge Base section in CLAUDE.md and create `docs/kb/` directory (idempotent)
- `/kb-learn` - Analyze conversation to extract learnings, best practices, and institutional knowledge into KB files
- `/kb-add` - Quickly add a learning or rule to the KB with interactive location picker
- `/kb-import` - Register existing KB files in CLAUDE.md (accepts file path or scans for unregistered files, adds missing frontmatter)
- `/kb-list` - List all registered KB files with status, tags, dates, pinned status, and cross-references
- `/kb-search` - Search across KB files by keyword, topic, or tag (`tag:security`)
- `/kb-prune` - Interactive cleanup: stale refs, duplicates, merges, frontmatter health, cross-reference integrity
- `/kb-auto` - Toggle automatic knowledge capture at end of conversations (per-project)
- `/kb-absorb` - Migrate existing CLAUDE.md sections and docs/ content into the KB system with interactive approval
- `/kb-remove` - Remove a KB file and its CLAUDE.md reference (accepts optional path or interactive selection)
- All KB files use YAML frontmatter with `tags`, `related`, `created`, `last-updated`, `pinned`, and `scope` fields
- Cross-references between KB files via `related: [[other-file]]` frontmatter for linked knowledge loading
- Pinned KB files (`pinned: true`) are always loaded regardless of work context

## [2.2.2] - 2026-03-31

### Fixed

#### AI-ADO Plugin (v1.3.1)

- **Fixed skill name parsing** - Changed `ado-work-items` skill name from `Azure DevOps Work Items` (with spaces) to `ado-work-items` so Claude Code can parse it correctly (fixes #8)

## [2.2.1] - 2026-03-31

### Fixed

#### AI-Statusline Plugin (v1.2.3)

- **Fixed rate limit percentage display** - Rate limit percentages now round to 2 decimal places instead of showing long floating-point numbers (e.g., `5h:12.35%` instead of `5h:12.345678%`)
  - Bash: uses jq `(. * 100 | round) / 100` for rounding, extracts integer part for color threshold comparisons
  - PowerShell: uses `[math]::Round($val, 2)` instead of `[int]` cast which truncated to whole numbers

## [2.2.0] - 2026-03-31

### Added

#### AI-Security Plugin (v1.5.0)

- `/security-supply-chain` new skill for hardening projects against npm supply chain attacks
  - Detects package manager (pnpm, npm, Yarn, Bun) and validates compatibility
  - Configures pnpm's `minimum-release-age` in `.npmrc` to quarantine newly published packages
  - Interactive timeframe selection with previews (24 hours, 3 days, 7 days, or custom)
  - Scans CI/CD configs for frozen lockfile usage and offers to add `frozen-lockfile=true`
  - Checks pnpm version and offers upgrade if below 10.16.0 minimum
  - Recommends pnpm migration for npm/Yarn/Bun users who lack quarantine protection
  - Creates two defense layers: time-based quarantine (local dev) + frozen lockfile (CI/CD)

## [2.1.0] - 2026-03-22

### Added

#### AI-Modernize Plugin (v1.0.0) - NEW PLUGIN

- **New plugin for codebase modernization assessment** - Identifies technical debt, anti-patterns, and quality issues from older AI-generated or legacy code

- `/modernize-audit` interactive skill for comprehensive modernization assessment
  - Guided configuration: AI tool history, codebase era, tech stack detection, category selection, scope, severity threshold
  - 12 assessment categories: SOLID/DRY/KISS violations, type safety, error handling, security, performance, testing, architecture, frontend debt, dependency health, AI hallucination artifacts, modern pattern gaps, configuration/DevOps
  - Modernization Score (0-100) with category breakdown
  - AI-assisted remediation time estimates (not manual development time)
  - Phased modernization roadmap with prioritized checklist
  - "Why Older AI Models Did This" educational context for each finding
  - Delegates to `ai-modernize:modernize-auditor` subagent for deep analysis

- `/modernize-scan` quick scan skill for fast, targeted assessments
  - Accepts file or directory path argument (e.g., `/modernize-scan ./src`)
  - Runs all categories with default settings, no interactive questions
  - Auto-detects technology stack
  - Produces abbreviated report with same scoring and estimate format

- Reports saved to `/docs/modernize/` with timestamped filenames

#### AI-Workflow Plugin (v1.4.0)

- `/workflow-principles` new skill for generating context-aware Development Principles in CLAUDE.md
  - Automated project discovery: detects monorepo structure, tech stack, frameworks, validation libraries, state management, testing tools
  - Interactive configuration: principle categories (SOLID, DRY, KISS, YAGNI, modularity, components, type safety, error handling, testing)
  - Monorepo-aware: detects shared packages, maps dependency direction, generates shared package rules with real package names
  - Frontend-aware: generates component architecture rules tailored to detected framework (React, Vue, Angular, Svelte)
  - Smart merge: appends, replaces, or merges with existing CLAUDE.md content
  - Supports both project CLAUDE.md and user-level ~/.claude/CLAUDE.md
  - Custom rules support for project-specific conventions
  - Uses real package names, paths, and library names from the detected project (never generic placeholders)

#### AI-Compliance Plugin (v1.0.0) - NEW PLUGIN

- **New plugin for software license compliance auditing** - Detects open-source licenses, flags legal risks, and generates attribution files

- `/compliance-license-audit` interactive skill for comprehensive license compliance audit
  - Auto-detects project license with confirmation
  - Scans all dependency manifests across 8 package ecosystems (npm, pip, NuGet, Go, Rust, Ruby, PHP, Java)
  - Classifies licenses: Permissive, Weak Copyleft, Strong Copyleft, Unknown/None
  - License compatibility analysis against the project's own license
  - Flags copyleft contamination risks with configurable risk tolerance
  - Optional transitive dependency analysis via lock files
  - Source code scanning for license headers and vendored/copied code
  - License Compliance Score (0-100)
  - Identifies unfulfilled license obligations (missing NOTICE files, attribution)
  - Provides alternative components for incompatible dependencies

- `/compliance-notice-generate` interactive skill for generating attribution files
  - Four output formats: NOTICE, THIRD-PARTY-NOTICES.md, ATTRIBUTION.md, licenses.json
  - Configurable scope: production only, all dependencies, or custom groups
  - Optional full license text inclusion
  - Extracts actual copyright notices from LICENSE files
  - Handles dual-licensed packages and license exceptions
  - Detects existing attribution files with replace/create-alongside options

- Reports saved to `/docs/compliance/` with timestamped filenames

## [2.0.2] - 2026-03-19

### Added

#### AI-Statusline Plugin (v1.2.2)

- **Added rate limit usage display** - Shows 5-hour and 7-day rate limit percentages with color-coded thresholds (green <50%, yellow 50-79%, red 80%+)
  - New `SHOW_RATE_LIMITS` configuration option (enabled by default)
  - Reads `rate_limits.five_hour.used_percentage` and `rate_limits.seven_day.used_percentage` from the statusline JSON input
  - Requires Claude Code 2.1.80+ (gracefully hidden on older versions where the field is absent)
  - Updated both Bash and PowerShell script templates
  - Added to `/statusline-wizard` and `/statusline-edit` question flows

## [2.0.1] - 2026-02-17

### Fixed

#### AI-Statusline Plugin (v1.2.1)

- **Fixed PowerShell script template bugs**
  - Fixed stdin reading using reserved `$input` automatic variable; replaced with `[System.Console]::In.ReadToEnd()` so the script actually receives JSON data when invoked via `-File`
  - Fixed progress bar using ASCII `+`/`-` instead of Unicode `▓`/`░` to match bash template and documentation
  - Fixed segment separator using `" | "` instead of `" · "` to match bash template and README examples
  - Fixed unquoted paths in `Split-Path` and `git -C` that would break on directories with spaces
  - Fixed confusing cost format string `'${0:F2}'` that resembles a variable reference; clarified with string concatenation
  - Fixed Unicode character encoding by setting `[Console]::OutputEncoding` to UTF-8 and using `[char]` codes instead of literal Unicode in source file

## [2.0.0] - 2026-02-16

### Added

#### AI-Writing Plugin (v1.0.0)

- **New plugin for writing quality tools**
  - Detect and remove signs of AI-generated writing from text
  - Based on Wikipedia's "Signs of AI writing" guide maintained by WikiProject AI Cleanup

- `/writing-humanize` skill for removing AI writing patterns
  - Identifies 24 documented AI writing patterns across 6 categories: content, language/grammar, style, communication, filler/hedging, and personality
  - Rewrites problematic sections with natural alternatives while preserving meaning
  - Detects inflated significance, promotional language, superficial -ing analyses, vague attributions, overused AI vocabulary, em dash overuse, rule of three, negative parallelisms, sycophantic tone, and more
  - Includes full before/after examples for each pattern category

#### AI-Workflow Plugin (v1.3.0)

- **Added `/workflow-ship` skill for end-to-end shipping workflow**
  - Runs preflight checks (typecheck, lint, tests) via `/workflow-preflight`
  - Auto-fixes linting and formatting issues, bails early if fixes were applied so user can review
  - Interactive branch selection with `AskUserQuestion` (prevents direct commits to main/master)
  - Commits with proper Co-Authored-By trailer and HEREDOC formatting
  - Pushes to remote with automatic upstream tracking setup
  - Creates PR with dynamic target branch selection (detects staging/main availability)
  - PR body includes summary bullets, test plan, and Claude Code attribution
  - Safety guards: never force pushes, never skips preflight, never commits secrets

### Changed

#### All Plugins

- **Migrated all commands to skills** - eliminated `commands/` directories across all 8 remaining plugins
  - All 21 slash commands now use the skills system exclusively, removing duplicate entries
  - Standalone commands converted to skill directories with `SKILL.md` files
  - Command+skill pairs merged into unified skill files (command workflow first, skill expertise below)
  - All skills include `disable-model-invocation: true` to prevent auto-invocation
  - Slash command names remain unchanged; no user-facing changes to invocation

#### AI-Accessibility Plugin (v1.4.0)

- Merged `/accessibility-audit` command into `accessibility-audit` skill
- **Overhauled accessibility audit skill for conciseness, WCAG 2.2 coverage, and pattern alignment with peer plugins**
  - Reduced SKILL.md from 1542 to 787 lines (~49% reduction) while preserving all functional content
  - Added WCAG 2.2 criteria to 4 expertise areas: Keyboard (SC 2.4.11, 2.4.13), Forms (SC 3.3.7, 3.3.8, 3.3.9), Interactive (SC 3.2.6), Responsive (SC 2.5.7, 2.5.8)
  - Added "WCAG 2.2 New Criteria" subsection with all 9 new success criteria and note on SC 4.1.1 Parsing removal
  - Removed standalone "Playwright MCP Visual Accessibility Testing" expertise area (area 9); Playwright workflow consolidated into Audit Methodology
  - Removed standalone "Code Remediation Examples" section (239 lines); findings already include remediation blocks
  - Removed "Component-Level Accessibility Assessment" from report template (duplicated findings section)
  - Reduced report template from 734 to ~186 lines with 2 format-demonstrating sample findings and clear placeholders
  - Consolidated Audit Methodology from 137 to ~48 lines with numbered checklists referencing expertise areas by name
  - Replaced "elite Accessibility Scanner" intro with professional, concise description
  - Tightened severity framework to criteria-only descriptions matching security-audit pattern
  - Added 3 concise before/after examples (Form Labels, Focus Indicators, ARIA Widget Pattern) replacing 6 verbose examples
  - Trimmed Best Practices (8 to 6), QA Checklist (10 to 8), Context-Aware (5 to 4), removed closing paragraph from Communication
- **Fixed agent skill reference**: `accessibility-auditing` to `accessibility-audit` in `accessibility-auditor` agent

#### AI-ADO Plugin (v1.3.0)

- Converted 6 commands to skills: `/ado-init`, `/ado-create-feature`, `/ado-create-story`, `/ado-create-task`, `/ado-log-story-work`, `/ado-timesheet-report`

#### AI-Git Plugin (v1.2.0)

- Converted 2 commands to skills: `/git-init`, `/git-commit-push`
- **Added `/git-commit-push-pr` skill for commit, push, and PR workflow**
  - Interactive branch selection with `AskUserQuestion` (prevents direct commits to main/master)
  - Commits with proper Co-Authored-By trailer and HEREDOC formatting
  - Pushes to remote with automatic upstream tracking setup
  - Creates PR with dynamic target branch selection (detects staging/main availability)
  - PR body includes summary bullets, test plan, and Claude Code attribution
  - Lightweight alternative to `/workflow-ship` without preflight checks
  - Safety guards: never force pushes, never commits secrets
- **Hardened `/git-commit-push` skill with safety improvements from `/git-commit-push-pr`**
  - Branch safety: blocks commits directly to main/master, suggests creating a feature branch
  - Smart file staging: prefers specific files by name over `git add .` or `git add -A`
  - Secrets detection: skips `.env`, `credentials.*`, `*.key`, `*.pem`, and other secret-like files
  - Upstream tracking: checks for remote tracking branch and uses `-u` flag when needed
  - HEREDOC formatting: uses HEREDOC for commit messages to ensure proper formatting
  - No-changes guard: detects empty state and stops early
  - Explicit safety rules: never force push, never use `git status -uall`
  - Structured step-by-step flow replacing flat numbered list
- **Improved `/git-init` skill with expanded technology support and lock file handling**
  - Added Swift/iOS detection (`Package.swift`, `*.xcodeproj`, `*.xcworkspace`) with Xcode, SPM, CocoaPods, Carthage, and Fastlane patterns
  - Added Flutter/Dart detection (`pubspec.yaml`) with platform-specific patterns for Android and iOS build artifacts
  - Added C/C++ detection (`CMakeLists.txt`, `Makefile`, `*.vcxproj`, `meson.build`) with compiled object and CMake patterns
  - Added Deno detection (`deno.json`, `deno.jsonc`, `deno.lock`)
  - Added Nuxt-specific build outputs (`.output/`, `.nitro/`, `.data/`) to Node.js patterns
  - Fixed Rust `Cargo.lock` handling: now commented out with guidance (commit for apps, ignore for libraries)
  - Fixed PHP `composer.lock` handling: now commented out with guidance (commit for apps, ignore for libraries)
  - Fixed Python `*.ipynb`: changed from default-ignore to commented out (many projects commit notebooks)
  - Fixed Go `go.work`: changed from default-ignore to commented out (some teams commit it)
  - Added `.env.template` and `.env.sample` negation patterns alongside `.env.example`
  - Updated lock file handling docs to cover Rust and PHP alongside Node.js

#### AI-Learn Plugin (v1.1.0)

- Converted 2 commands to skills: `/learn`, `/learn-review`

#### AI-Performance Plugin (v1.2.0)

- Merged `/performance-audit` command into `performance-audit` skill
- **Overhauled performance audit skill for technology-agnostic, modern analysis**
  - Replaced .NET-centric report template with stack-agnostic placeholders that adapt to any project
  - Removed pre-filled example findings (P-001 through P-007) from template; agent now discovers real findings only
  - Added Core Web Vitals (LCP, INP, CLS) as primary frontend metrics, replacing outdated FCP/TTI focus
  - Added severity scoring criteria with 1.0-10.0 scale, defined thresholds, and weighted scoring factors
  - Added framework-aware frontend guidance for React, Vue, Svelte, and Angular (previously React-only)
  - Added new "Concurrency and Thread Safety" section covering race conditions, deadlocks, connection pool exhaustion, and event loop blocking
  - Added new "Memory Performance" section with platform-specific patterns for JavaScript/Node.js and managed languages (.NET, Java, Go)
  - Added new "Observability" section covering metrics, logs, and distributed tracing (OpenTelemetry, Jaeger)
  - Added streaming/SSR performance guidance (React Server Components, Nuxt, SvelteKit, edge rendering)
  - Added GraphQL performance patterns (query depth limiting, DataLoader, persisted queries)
  - Added bundle analysis and tree-shaking to asset optimization guidance
  - Added Node.js event loop blocking example to skill examples
  - Enhanced asset loading example with modern formats (AVIF, WebP) and `<picture>` element
  - Added concurrency anti-patterns section (shared mutable state, deadlocks, connection pool exhaustion)
  - Expanded QA checklist with rollback planning, realistic data volume testing, and error path verification
  - Added template requirements for stack detection and instructions to tailor findings to project technology

#### AI-Security Plugin (v1.4.0)

- Converted `/security-init` command to skill
- Merged `/security-audit` command into `security-audit` skill
- Merged `/security-scan-dependencies` command into `security-scan-dependencies` skill
- **Overhauled security audit skill with modern attack coverage and placeholder-based templates**
  - Replaced hardcoded fake example data in report template (e.g., `src/Website.Data/Services/UserService.cs:45`) with placeholder guidance pattern (`[exact/file/path.ext:line_number]`) to prevent models from copying template examples verbatim
  - Added explicit template requirements: replace all bracketed placeholders, tailor code to detected stack, show "No [severity] issues identified" for empty severity levels
  - Added severity scoring table with 1.0-10.0 scale, defined thresholds, criteria, examples, and weighted scoring factors (exploitability, impact scope, data sensitivity, attack complexity, blast radius)
  - Added new "Supply Chain Security" section covering dependency confusion, typosquatting, lock file integrity, build pipeline secrets, Dockerfile security, and GitHub Actions injection
  - Added new "Modern API Attack Vectors" section covering GraphQL introspection/batching/depth attacks, WebSocket auth/rate limiting, SSRF cloud metadata endpoints, and API key leakage in client bundles
  - Added new "Modern Authentication Patterns" section covering passkeys/WebAuthn, OAuth 2.1/PKCE, JWT algorithm confusion, token lifecycle, and session fixation in SPAs
  - Added "Technology-Specific Security Considerations" section with language-specific vulnerabilities for Node.js (prototype pollution, ReDoS), Python (pickle, SSTI), .NET (XXE, BinaryFormatter), and Go (request smuggling, goroutine races)
  - Added 2 new examples: JWT algorithm confusion (JavaScript) and SSRF prevention (Python), bringing total to 5 multi-language examples
  - Added `allowed-tools` frontmatter to all 3 skills
- **Overhauled dependency scanning skill with expanded library detection and placeholder templates**
  - Replaced hardcoded findings (jQuery CVE, Bootstrap CVE, WordPress version, CSP header, Referrer-Policy examples) with placeholder guidance patterns
  - Fixed incorrect Context7 tool reference: `mcp__context7__get-library-docs` to `mcp__context7__query-docs`
  - Updated scanner version from v1.0 to v1.4.0 in report template
  - Expanded UI framework detection: added Solid.js, Lit, Alpine.js, HTMX, Qwik
  - Renamed "Server Frameworks" to "Meta-Frameworks" and added Remix, SvelteKit, Astro
  - Added meta-framework detection methods (Next.js `__NEXT_DATA__`, Nuxt `__NUXT__`, Remix `__remixContext`, SvelteKit `__sveltekit_`, Astro `astro-island`, Gatsby `___gatsby`)
  - Added headless CMS detection: Strapi, Sanity, Contentful, Payload CMS
  - Expanded build tool detection: added esbuild, SWC, Turbopack
  - Expanded analytics detection: added Plausible, PostHog
  - Added recent CVE examples: Lodash prototype pollution (CVE-2021-23337), Next.js SSRF (CVE-2024-34351), jsonwebtoken (CVE-2022-23529), Axios SSRF, Angular.js EOL
- **Enhanced security-init skill with expanded technology support**
  - Added Deno detection (`deno.json`, `deno.lock`) with `.deno/**` deny patterns
  - Added Swift/iOS detection (`Package.swift`, `*.xcodeproj`) with `.build/**`, `DerivedData/**`, `Pods/**` deny patterns
  - Added Kotlin/Android detection (`build.gradle.kts`, `AndroidManifest.xml`) with `build/**`, `.gradle/**`, `local.properties` deny patterns
  - Added Terraform/IaC detection (`*.tf`, `*.tfvars`) with `*.tfstate`, `.terraform/**` deny patterns
  - Added Kubernetes detection (`kustomization.yaml`, `Chart.yaml`) with `**/secrets.yaml` deny patterns
  - Added base security patterns: CI/CD secrets (`.github/secrets/**`), package manager auth (`.npmrc`, `.yarnrc.yml`), deployment configs (`.vercel/**`, `.netlify/**`)
  - Added post-install verification step to confirm settings were saved correctly
- **Fixed agent skill references**
  - `security-auditor` agent: `security-auditing` to `security-audit`, fixed `it's` to `its`, expanded focus areas with modern attack vectors
  - `security-dependency-scanner` agent: `security-dependency-scanning` to `security-scan-dependencies`, expanded focus areas with meta-frameworks, headless CMS, and build tools

#### AI-Statusline Plugin (v1.2.0)

- Merged `/statusline-wizard` command into `statusline-wizard` skill
- Converted `/statusline-edit` command to skill

#### AI-Workflow Plugin (v1.3.0)

- Merged `/workflow-plan-phases` command into `workflow-plan-phases` skill
- Merged `/workflow-implement-phases` command into `workflow-implement-phases` skill
- Merged `/workflow-preflight` command into `workflow-preflight` skill
- Renamed `/ship` skill to `/workflow-ship` for naming consistency

### Removed

#### AI-Plugins Plugin

- **Removed ai-plugins plugin entirely** - Claude Code handles plugin creation natively

## [1.9.1] - 2026-01-18

### Added

#### AI-Workflow Plugin (v1.1.0)

- **Added security scanning detection to `/workflow-preflight` command**
  - Detects and runs `pnpm audit`, `npm audit`, `yarn audit` for dependency vulnerability scanning
  - Detects `eslint-plugin-security` in devDependencies and notes when security linting is active
  - Universal Semgrep detection via multiple sources:
    - Package.json scripts (e.g., `pnpm run semgrep`)
    - Config files: `.semgreprc.yml`, `.semgrep.yml`, `semgrep.yml`, `.semgrep/`
    - CI workflows: `.github/workflows/*.yml` (extracts `--config` flags)
    - README.md documentation (Security sections)
    - Local CLI availability
    - Docker fallback when semgrep CLI not installed
  - Added Python (`pip-audit`, `safety`) and Rust (`cargo audit`) dependency scanning
  - Updated preflight skill with security scanning quick reference table

## [1.9.0] - 2026-01-14

### Added

#### AI-Learn Plugin (v1.0.0)

- **New plugin for Socratic learning mode**
  - Transforms Claude from code generator to patient coding mentor
  - Guides users through problem-solving without providing direct answers
  - Based on productive struggle methodology for retained knowledge

- `/learn` command for activating teaching mode
  - 5-phase teaching flow: Assessment, Foundation, Guided Implementation, Error Discovery, Reinforcement
  - Socratic questioning instead of direct answers
  - Hints and guidance rather than solutions
  - Escape hatch for users who explicitly request answers

- `/learn-review` command for Socratic code review
  - Reviews code through targeted questions
  - Helps users discover bugs by tracing through edge cases
  - Probes design decisions to deepen understanding
  - Question banks for logic, performance, readability, and security concerns

## [1.8.0] - 2025-12-18

### Added

#### AI-Accessibility Plugin (v1.3.0)

- **Added Section 508 / WCAG 2.0 AA option** to `/accessibility-audit` command
  - New "508 / WCAG 2.0 AA" option in WCAG version selection
  - Supports US federal accessibility requirements aligned with WCAG 2.0 Level AA

## [1.7.1] - 2025-12-17

### Fixed

#### AI-Statusline Plugin (v1.1.1)

- **Fixed PowerShell progress bar using incompatible Unicode characters**
  - Replaced `▓` and `░` with ASCII-compatible `#` and `-` characters
  - Ensures progress bar displays correctly on Windows environments

## [1.7.0] - 2025-12-16

### Added

#### AI-Statusline Plugin (v1.1.0)

- **New plugin for custom status line configuration**
  - Interactive setup wizard for configuring Claude Code's status line
  - Cross-platform support (bash for Mac/Linux, PowerShell for Windows)
  - Visual progress bar for context usage with color-coded thresholds
  - 9 configurable display options with sensible defaults

- `/statusline-wizard` command for interactive status line setup
  - Multi-step wizard using AskUserQuestion for configuration
  - Automatic OS detection for appropriate script selection
  - Backs up existing scripts and settings before overwriting
  - Makes scripts executable on Mac/Linux with `chmod +x`

- `/statusline-edit` command for editing existing configuration
  - Detects existing status line script and reads current settings
  - Pre-selects wizard options based on current configuration values
  - Updates only the configuration variables, preserving script logic
  - Directs users to `/statusline-wizard` if no script exists

- `statusline-setup` skill with complete script templates
  - Bash script template with all configurable variables
  - PowerShell script template with all configurable variables
  - Setup workflow documentation

- Configurable elements:
  - Model name (e.g., "Claude Opus 4.5")
  - Token count (e.g., "50k/100k")
  - Progress bar with percentage
  - Current directory
  - Git branch
  - Session cost (hidden by default)
  - Session duration
  - Current time
  - Claude Code version

## [1.6.3] - 2025-12-13

### Fixed

#### AI-Workflow Plugin (v1.0.3)

- **Fixed `/workflow-implement-phases` not using sub-agents for phase implementations**
  - Added explicit "Critical Requirements" section mandating Task() sub-agent usage for every phase
  - Added "CRITICAL: Mandatory Sub-Agent Requirement" section to implement-phases skill
  - Clarified orchestrator role: read plans, analyze dependencies, spawn sub-agents only
  - Added correct/wrong pattern examples showing Task() usage vs direct implementation
  - Updated parallel and sequential execution patterns with explicit Task() call examples
  - Prevents main agent from implementing phases directly, ensuring context isolation

## [1.6.2] - 2025-12-12

### Fixed

#### AI-Workflow Plugin (v1.0.2)

- **Fixed `/workflow-plan-phases` proceeding to implementation after creating plan**
  - Added explicit "Instructions" section with step-by-step workflow
  - Added "Important" section emphasizing planning-only scope
  - Command now stops after presenting the plan and directs users to `/workflow-implement-phases` for execution
  - Updated skill file with "IMPORTANT: Planning Only — Do Not Implement" section

- **Fixed `/workflow-implement-phases` not reading the plan file argument**
  - Added explicit "Instructions" section telling Claude to read the plan file
  - Added automatic plan discovery: if no file provided, searches `docs/plans/` and lets user pick
  - Plan file argument is now optional (defaults to searching `docs/plans/`)
  - Updated workflow step 1 to explicitly use Read tool for plan document

## [1.6.1] - 2025-12-10

### Changed

#### All Plugins

- **Added YAML frontmatter to all command files** with `name` and `description` attributes
  - Standardizes command metadata across all 17 commands in 7 plugins
  - Enables better command discovery and documentation
  - Follows the pattern established by ai-workflow plugin

#### AI-Workflow Plugin (v1.0.1)

- **Renamed commands to use `workflow-` prefix** for consistency with other plugins
  - `/plan-phases` → `/workflow-plan-phases`
  - `/implement-phases` → `/workflow-implement-phases`
  - `/preflight` → `/workflow-preflight`

## [1.6.0] - 2025-12-10

### Added

#### AI-Workflow Plugin (v1.0.0)

- **New plugin for development workflow automation**
  - Phase-based planning and implementation orchestration for efficient sub-agent execution
  - Preflight code quality verification system

- `/plan-phases` command for creating structured implementation plans
  - Breaks features into context-efficient phases (30-50k tokens each)
  - Whole number phases only (no sub-phases like 1.1, 1.2)
  - Clear acceptance criteria per phase
  - Dependency mapping with execution strategy recommendations
  - Outputs structured markdown to `docs/plans/`

- `/implement-phases` command for orchestrating multi-phase implementation
  - Parses plan documents and extracts phase definitions
  - Analyzes dependencies (explicit and implicit)
  - Determines optimal execution strategy (parallel/sequential/mixed)
  - Executes via Task() sub-agents with coordination directory
  - Aggregates results and provides comprehensive summary

- `/preflight` command for code quality checks
  - Auto-detects configured quality tools across ecosystems (Node.js, Python, .NET, Go, Rust)
  - Runs type checking, linting, formatting checks, and tests
  - Interactive fix mode with user consent
  - Supports `--fix`, `--check-only`, and `--verbose` arguments

- `plan-phases` skill with methodology for context-efficient phase sizing and dependency analysis
- `implement-phases` skill with dependency detection algorithms and execution patterns
- `preflight-checks` skill with comprehensive reference for quality tools across languages

### Changed

#### AI-Accessibility Plugin (v1.2.0)

- **Improved Playwright MCP detection flow** in `/accessibility-audit` command
  - Added "Skip visual testing" option when Playwright MCP tools are unavailable
  - Users can now proceed with code-based analysis without creating `.mcp.json`
  - Better handles cases where Playwright is installed globally via Claude Code `/mcp` command
- **Enhanced Accessibility Audit Skill with Improved Prompt Engineering**
  - Improvements for more accurate and actionable reports
  - Added **Code Context Accuracy** section with explicit guidance on when to include/omit code snippets
    - MUST show code when elements exist but lack attributes (e.g., missing alt, missing labels)
    - MUST omit code context when elements truly don't exist (e.g., no skip link present)
    - Prevents placeholder/guessed code in reports
  - Added **Specificity Requirements** section for precise element identification
    - Location field must enumerate specific elements, not generic descriptions
    - Code Context must show ALL affected elements (or first 3-5 if many)
    - Remediation examples must use actual values from the codebase, not placeholders
  - Enhanced **Severity Assessment Framework** with concrete examples for each level
  - Added clickable WCAG Understanding document links to compliance matrix
  - Standardized finding format with consistent bullet-point structure
  - Improved guidance on text readability with complex backgrounds (gradients, images, patterns)

## [1.5.4] - 2025-01-17

### Fixed

#### AI-Security Plugin (v1.3.2)

- **Fixed `/security-scan-dependencies` to require WebFetch or curl for HTTP header retrieval**
  - Updated command and skill documentation to explicitly prohibit Playwright or MCP browser tools
  - Added critical tool requirement section explaining that HTTP security headers (especially Content-Security-Policy) can ONLY be retrieved via WebFetch or curl
  - Browser automation tools cannot access raw HTTP response headers needed for security header analysis
  - Added "Required Tools" section to `security-dependency-scanning` skill with approved/prohibited tool lists
  - Enhanced scanning methodology with explicit WebFetch/curl usage examples
  - Updated quality assurance checklist to verify correct tool usage
  - Prevents incomplete security scans due to missing HTTP header analysis

## [1.5.3] - 2025-01-04

### Fixed

#### Marketplace

- Updated plugin versions in `marketplace.json` to match the versions in each `plugin.json` manifest

#### AI-Accessibility Plugin (v1.1.1)

- Accessibility scanning command `/accessibility-audit` now properly checks to see if Playwright MCP is installed before proceeding with an accessibility audit

## [1.5.2] - 2025-01-04

### Changed

#### AI-Accessibility Plugin (v1.1.0)

- **Added URL Accessibility Scanning** with optional Playwright MCP integration
  - New "a URL" option in scope selection for scanning live websites
  - Interactive Playwright MCP setup with automatic `.mcp.json` configuration
  - OS detection for Windows vs Linux/Mac Playwright configuration
  - Visual accessibility testing when Playwright MCP is available:
    - Real-time color contrast measurements of rendered elements
    - Visual verification of focus indicators
    - Accessibility tree analysis as perceived by assistive technologies
    - Keyboard navigation testing on live pages
    - Touch target size verification with actual pixel measurements
    - Screenshot-based visual accessibility assessment
  - Enhanced audit reports with screenshot evidence for visual findings
  - Screenshots saved to `/docs/accessibility/screenshots/` directory
- Updated `/accessibility-audit` command to support URL scanning with Question 4 for Playwright MCP preference
- Enhanced `accessibility-auditor` agent with dual analysis approach (codebase vs URL with Playwright)
- Enhanced `accessibility-audit` skill with Playwright MCP expertise and visual testing methodology

#### All Plugins

- **Improved Command Usage Documentation** to prevent erroneous argument passing
  - Added prominent command usage note in README.md clarifying that all commands are invoked without arguments
  - Added explicit "no arguments" instruction to all 13 command files across all plugins
  - Commands now explicitly state they will ignore any passed arguments and prompt interactively for all necessary information
  - Affected plugins:
    - AI-Accessibility (v1.1.0): `/accessibility-audit`
    - AI-Security (v1.3.1): `/security-audit`, `/security-init`, `/security-scan-dependencies`
    - AI-Performance (v1.1.2): `/performance-audit`
    - AI-Git (v1.1.1): `/git-init`, `/git-commit-push`
    - AI-Plugins (v1.2.2): `/plugins-scaffold`
    - AI-ADO (v1.2.2): `/ado-init`, `/ado-create-feature`, `/ado-create-story`, `/ado-create-task`, `/ado-log-story-work`, `/ado-timesheet-report`

## [1.5.1] - 2025-11-01

### Added

#### AI-Security Plugin (v1.3.0)

- `/security-scan-dependencies` command for scanning deployed websites
  - Web dependency security scanning without source code access
  - Interactive URL input and configurable scan scope (libraries, CMS, security headers, or comprehensive)
  - Frontend library detection: jQuery, React, Vue, Angular, Bootstrap, Tailwind, and more via CDN pattern matching
  - CMS platform detection with version identification:
    - Open source: WordPress, Drupal, Joomla
    - Enterprise .NET: Umbraco, Sitecore, Optimizely, Kentico
  - HTTP security headers analysis (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy)
  - Context7 MCP integration for latest version verification
  - Known CVE identification with CVSS v3.1 severity scoring
  - Timestamped reports with severity-based findings (C-001, H-001, M-001, L-001 format)
  - Hybrid Agent + Skill architecture with `security-dependency-scanner` agent and `security-dependency-scanning` skill
- Use cases: Third-party website assessment, pre-acquisition due diligence, supply chain security analysis

## [1.5.0] - 2025-10-29

### Added

#### AI-Accessibility Plugin (v1.0.0)

- `/accessibility-audit` command with WCAG 2.1/2.2 compliance checking
  - Interactive configuration for WCAG version (2.1/2.2), conformance level (A/AA/AAA), and audit scope
  - Comprehensive pattern detection: semantic HTML, ARIA, keyboard navigation, color contrast, forms, images, screen readers
  - Timestamped reports with severity-based findings, WCAG compliance matrix, and code remediation examples
  - Hybrid Agent + Skill architecture with `accessibility-auditor` agent and `accessibility-auditing` skill

#### Marketplace Documentation

- Added "Note on Audit Plugins" section clarifying audit plugins are developer-focused static code analysis tools
- Emphasizes plugins complement (not replace) runtime testing tools and professional services

### Changed

#### AI-Security Plugin (v1.2.1)

- Standardized audit plugin structure
- Renamed skill from `security-audit` to `security-auditing`
- Reduced command file complexity: 402→80 lines
- Moved comprehensive report templates from command file to SKILL.md file (single source of truth)
- Renamed skill to use 'auditing' suffix

#### AI-Performance Plugin (v1.1.1)

- Standardized audit plugin structure
- Renamed agent from `performance-optimizer` to `performance-auditor`
- Renamed skill from `performance-audit` to `performance-auditing`
- Reduced command file complexity: 471→36 lines
- Moved comprehensive report templates from command file to SKILL.md file (single source of truth)
- Renamed skill to use 'auditing' suffix

## [1.4.1] - 2025-10-24

### Fixed

#### AI-ADO Plugin (v1.2.1)

- **Fixed `/ado-timesheet-report` command**
  - Migrated from non-existent `wit_query` to `wit_my_work_items` MCP tool with client-side filtering
  - Fixed date range filtering to use date-only comparison (prevents time-of-day issues)
  - Fixed day-of-week calculation using platform-specific system commands (PowerShell on Windows, `date` on Mac/Linux)
  - Prevents off-by-one errors in current week date range calculations

### Changed

- Condensed changelog entries across all versions for improved readability while maintaining essential information

## [1.4.0] - 2025-10-23

### Added

#### AI-ADO Plugin (v1.2.0)

- `/ado-timesheet-report` command for generating flexible weekly timesheet reports
  - Flexible task filtering (closed only, worked on only, or both)
  - Multiple date field support (Closed Date or Changed Date)
  - Three grouping modes (by hierarchy, by date, or by date with hierarchy)
  - Three verbosity levels (ID & hours, with titles, or with descriptions)
  - Flexible week definitions (Monday-Sunday or Sunday-Saturday)
  - User filtering (current user or specific team member)
  - Summary statistics and formatted reports with emoji icons

## [1.3.0] - 2025-10-21

### Added

#### AI-ADO Plugin (v1.1.0)

- **AI-Powered Work Item Generation** for `/ado-create-feature`, `/ado-create-story`, and `/ado-create-task` commands
  - AI generates titles, descriptions, persona statements, and acceptance criteria
  - Review and confirmation workflow with override options
  - Analyzes CLAUDE.md for naming conventions and standards
  - Context-aware generation using parent work item details

- `/ado-log-story-work` command for rapid work logging to User Stories
  - Creates tasks with completed hours pre-populated
  - AI-powered or manual task generation
  - Automatic git commit hash detection
  - Optional placeholder task hour subtraction

#### AI-Security Plugin (v1.2.0)

- **Hybrid Agent + Skill Architecture** with `security-audit` skill for optimal context efficiency
  - Progressive disclosure design: metadata loads first, full skill loads only when needed
  - Interactive security audits without consuming context until relevant

#### AI-Performance Plugin (v1.1.0)

- **Hybrid Agent + Skill Architecture** with `performance-audit` skill for optimal context efficiency
  - Progressive disclosure design: metadata loads first, full skill loads only when needed
  - Interactive performance analysis without consuming context until relevant

#### AI-Plugins Plugin (v1.2.0)

- **Plugin Development Skills** for interactive plugin and skill creation
  - New `plugins-scaffold` and `skills-scaffold` skills
  - Auto-loads when creating plugins, manifests, commands, agents, skills, or hooks

#### AI-ADO Plugin (v1.1.0)

- **Azure DevOps Work Items Skill** for MCP-powered work item management
  - New `ado-work-items` skill enforcing proper hierarchy and naming conventions
  - HTML formatting guidance and best practices
  - Auto-loads when using Azure DevOps MCP server tools

### Changed

#### AI-Security Plugin (v1.2.0)

- Converted `security-auditor` agent to lightweight wrapper that loads `security-audit` skill in fresh context

#### AI-Performance Plugin (v1.1.0)

- Converted `performance-optimizer` agent to lightweight wrapper that loads `performance-audit` skill in fresh context

### Fixed

#### AI-ADO Plugin (v1.1.0)

- Fixed `/ado-create-story` to properly set acceptance criteria in dedicated field instead of Description field

## [1.2.0] - 2025-10-20

### Added

#### AI-Git Plugin (v1.1.0)

- `/git-init` command for automated .gitignore generation
  - Intelligent technology detection (Node.js, Python, .NET, Go, Rust, PHP, Ruby, Java, Docker, React/Next.js, Vue, Terraform)
  - Comprehensive pattern generation (80+ patterns based on tech stack)
  - Smart merge strategies with preview and confirmation workflow

#### AI-ADO Plugin (v1.0.0)

- `/ado-init` command for Azure DevOps configuration and MCP server setup
  - Interactive configuration for organization, project, team, area path, and iteration path
  - Automatic CLAUDE.md configuration with work item hierarchy standards
  - Optional `.mcp.json` creation for MCP server integration
  - Cross-platform support with PAT authentication guidance

- `/ado-create-feature` command for creating Feature work items
  - Interactive prompts for title and description with HTML formatting
  - Returns Feature ID with Azure DevOps web link

- `/ado-create-story` command for creating User Story work items
  - Interactive prompts for parent Feature, title, persona statement, acceptance criteria, and story points
  - HTML formatted with Given-When-Then acceptance criteria

- `/ado-create-task` command for creating Task work items
  - Interactive prompts for parent User Story, title, and hour estimate
  - Hour tracking with Original Estimate and Remaining Work fields

### Changed

#### AI-Git Plugin (v1.1.0)

- Renamed `/commit-push` command to `/git-commit-push` for consistency with `/git-init` naming convention

#### AI-Plugins Plugin (v1.1.0)

- Renamed `/scaffold-plugin` command to `/plugins-scaffold` for consistency with plugin naming convention

## [1.1.0] - 2025-10-19

### Added

#### AI-Security Plugin (v1.1.0)

- `/security-init` command for automated security settings initialization
  - Intelligent technology detection with comprehensive file denial patterns (40-60+ based on tech stack)
  - Smart merge strategies with preview and confirmation workflow

### Changed

#### AI-Security Plugin (v1.1.0)

- Enhanced `/security-audit` with pre-audit configuration check recommending `/security-init` for users with fewer than 4 deny rules

## [1.0.1] - 2025-10-17

### Added

#### AI-Plugins Plugin (v1.0.0)

- Initial release with `/scaffold-plugin` command for interactive plugin scaffolding (later renamed to `/plugins-scaffold`)
  - AI-assisted plugin creation with automatic directory structure, metadata, and marketplace registration

## [1.0.0] - 2025-10-17

### Added

#### Marketplace

- Initial release of Claude Code Plugins marketplace with `.claude-plugin/marketplace.json` metadata system
- Support for slash commands, agents, and skills

#### AI-Git Plugin (v1.0.0)

- `/commit-push` command for automated git commit and push (later renamed to `/git-commit-push`)
  - Intelligent commit message generation following repository conventions
  - Clean commit messages without AI attribution

#### AI-Security Plugin (v1.0.0)

- `/security-audit` command with `security-auditor` agent
  - OWASP Top 10 2021 compliance checking and vulnerability detection
  - Timestamped audit reports with risk scoring and remediation guidance

#### AI-Performance Plugin (v1.0.0)

- `/performance-audit` command with `performance-optimizer` agent
  - Performance anti-pattern detection and database optimization recommendations
  - Timestamped audit reports with impact scoring and optimization roadmap

### Documentation

- README.md, CLAUDE.md, individual plugin READMEs, and MIT license

[Unreleased]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.12.0...v3.0.0
[2.12.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.11.3...v2.12.0
[2.11.3]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.11.2...v2.11.3
[2.11.2]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.11.1...v2.11.2
[2.11.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.11.0...v2.11.1
[2.11.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.10.0...v2.11.0
[2.10.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.9.0...v2.10.0
[2.9.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.8.1...v2.9.0
[2.8.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.8.0...v2.8.1
[2.8.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.7.1...v2.8.0
[2.7.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.7.0...v2.7.1
[2.7.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.6.0...v2.7.0
[2.6.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.4.3...v2.5.0
[2.4.3]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.4.2...v2.4.3
[2.4.2]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.4.1...v2.4.2
[2.4.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.3.4...v2.4.0
[2.2.2]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.2.1...v2.2.2
[2.2.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.9.1...v2.0.0
[1.9.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.7.1...v1.8.0
[1.7.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.6.3...v1.7.0
[1.6.3]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.6.2...v1.6.3
[1.6.2]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.5.4...v1.6.0
[1.5.4]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.5.3...v1.5.4
[1.5.3]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.5.2...v1.5.3
[1.5.2]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/charlesjones-dev/ai-agent-plugins/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/charlesjones-dev/ai-agent-plugins/releases/tag/v1.0.0
