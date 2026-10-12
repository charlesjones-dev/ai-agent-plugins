# AI Agent Plugins

[![Version](https://img.shields.io/badge/version-3.0.1-blue.svg)](https://github.com/charlesjones-dev/ai-agent-plugins/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/charlesjones-dev/ai-agent-plugins.svg)](https://github.com/charlesjones-dev/ai-agent-plugins/stargazers)

Plugins for git and project workflows, code audits and release checks. All 13 run in Claude Code, and 8 of them also run in Codex and Cursor. Each plugin adds its own commands, so install only the ones you need.

> **Coming from `claude-code-plugins-dev`?** Version 3.0.0 renamed the repository and the marketplace. Your current install keeps working. See [Moving from claude-code-plugins-dev](#moving-from-claude-code-plugins-dev) to switch to the new name.

## Plugins

Each skill is a command you run by name, such as `/git-init` in Claude Code and Cursor. Interactive skills ask for what they need; the rest run directly on your codebase. A few take flags, such as `/seo-fix --dry-run` and `/swift-verify --fix`. See each plugin's README.

| Plugin | What it does | Commands | Runs in |
|--------|--------------|----------|---------|
| [ai-accessibility](plugins/ai-accessibility/) | WCAG audits of code, or a live URL through Playwright MCP | `/accessibility-audit` | Claude Code, Codex, Cursor |
| [ai-ado](plugins/ai-ado/) | Azure DevOps work items, hour logging and timesheets through the Azure DevOps MCP server | `/ado-init`, `/ado-create`, `/ado-log-story-work`, `/ado-timesheet-report` | Claude Code |
| [ai-compliance](plugins/ai-compliance/) | License audits of open-source dependencies, plus NOTICE and ATTRIBUTION file generation | `/compliance-license-audit`, `/compliance-notice-generate` | Claude Code, Codex, Cursor |
| [ai-git](plugins/ai-git/) | .gitignore generation, preflight checks (typecheck, lint, format, security and tests), and commit, push and PR creation | `/git-init`, `/git-preflight`, `/git-commit-push-pr` | Claude Code, Codex, Cursor |
| [ai-knowledge](plugins/ai-knowledge/) | A team knowledge base kept in git as Claude Code rules, so each article loads when Claude works on matching files, every session, or on demand | `/kb-init`, `/kb-migrate`, `/kb-add`, `/kb-learn`, `/kb-discover`, `/kb-query`, `/kb-prune` | Claude Code |
| [ai-modernize](plugins/ai-modernize/) | Technical debt audits for code written with older AI models | `/modernize-audit` | Claude Code, Codex, Cursor |
| [ai-performance](plugins/ai-performance/) | Performance bottleneck audits with an impact score for each finding | `/performance-audit` | Claude Code, Codex, Cursor |
| [ai-security](plugins/ai-security/) | Security audits with Markdown/JSON reports that track findings across runs, a planner for sandboxed audits on a stronger model, a live-site dependency scan, and settings and supply-chain hardening. Complements native `/security-review` | `/security-init`, `/security-audit`, `/security-cvp-audit`, `/security-scan-dependencies`, `/security-supply-chain` | Claude Code |
| [ai-seo](plugins/ai-seo/) | Search audits through three lenses: SEO (deprecated patterns LLMs still generate), AEO (being the direct answer in featured snippets and voice assistants) and GEO (being cited in AI answers). Also applies framework-specific fixes, writes JSON-LD, FAQ sections, question maps and llms.txt | `/seo-audit`, `/seo-fix`, `/seo-schema`, `/seo-faq`, `/seo-questions`, `/seo-llms-txt` | Claude Code, Codex, Cursor |
| [ai-slop](plugins/ai-slop/) | Audits user-facing copy, layouts and metadata for AI-written tells and factual errors, like a privacy policy that misses the trackers the code loads, and rewrites a file or pasted text to remove AI writing patterns | `/slop-audit`, `/slop-rewrite` | Claude Code, Codex, Cursor |
| [ai-statusline](plugins/ai-statusline/) | Adds progress bars, rate-limit widgets, a month-to-date spend budget for accounts without rate limits, and effort-level and sandbox indicators to Claude Code's native `/statusline` | `/statusline-wizard`, `/statusline-edit` | Claude Code |
| [ai-swift](plugins/ai-swift/) | Swift/iOS/macOS release checks that catch Xcode Cloud and TestFlight blockers before upload | `/swift-preflight`, `/swift-diagnose`, `/swift-ci-scaffold`, `/swift-verify`, `/swift-concurrency-review` | Claude Code, Codex, Cursor |
| [ai-workflow](plugins/ai-workflow/) | An unattended run that takes a branch through Claude Code, Codex and Cursor Bugbot review, merge and deploy, and CLAUDE.md rules that keep PR descriptions and commit messages short and accurate | `/workflow-babysit`, `/workflow-rules` | Claude Code |

The Claude Code-only plugins depend on Claude Code subagents, settings files, rules, the status line or CLAUDE.md.

The audit skills take their settings as arguments, so a scheduled or unattended run doesn't stop to ask. For example, `/accessibility-audit 2.2 AA src/`, `/modernize-audit src --defaults`, `/seo-audit geo` or `/swift-preflight --check-only`. In Claude Code, `/security-audit` can also split its review between parallel `security-auditor` subagents.

> **Note on audit plugins:** The audit plugins read your code and report what they find, and a few can also check a live URL. Use them to catch problems during development, then confirm with runtime testing and manual review.

## Install

### Claude Code

[Install Claude Code](https://www.claude.com/product/claude-code), then add the marketplace and install the plugins you want:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install <plugin-name>@ai-agent-plugins

# For example:
/plugin install ai-git@ai-agent-plugins
/plugin install ai-security@ai-agent-plugins
```

Then run any of the plugin's commands:

```
/git-init              # Generate a .gitignore for the project
/security-init         # Add file-access deny rules for secrets
/ado-init              # Set up Azure DevOps and its MCP server
```

### Codex

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add <plugin-name>@ai-agent-plugins

# For example:
codex plugin add ai-git@ai-agent-plugins
```

Codex lists only the plugins marked Codex in the table and prefixes each skill with its plugin name, such as `ai-git:git-init`. Start a new session after installing, then type `$` to pick a skill or open `/skills`. Codex runs a skill only when you pick it, with two exceptions: it can start the slop audit when you ask whether a site or README reads as AI-written, and the git preflight checks when you ask it to check your code before a commit. Plugins don't load in the Codex IDE extension, so use the Codex CLI or the ChatGPT desktop app.

### Cursor

Cursor installs plugins from team marketplaces on its Teams and Enterprise plans. An admin adds this repository under **Dashboard > Plugins & MCPs > Team Marketplaces > Add Marketplace > Import from Repo**, using `https://github.com/charlesjones-dev/ai-agent-plugins`. Cursor lists only the plugins marked Cursor in the table.

To use a plugin on one machine instead, copy its folder to `~/.cursor/plugins/local/`, for example `plugins/ai-git` to `~/.cursor/plugins/local/ai-git`, then run **Developer: Reload Window**. On Teams and Enterprise plans, local plugins load only if an admin turns on **Allow Local Plugin Imports**, which is off by default on Enterprise. Run a skill with `/` and its name, such as `/git-init`.

### Other agents

The plugins that run in Codex and Cursor follow the [Agent Plugins](https://agent-plugins.org/) 1.0 format, with a `plugin.json` at the root of each plugin folder. Other agents that support the standard can load them from `plugins/<plugin-name>`.

## Moving from claude-code-plugins-dev

Version 3.0.0 renamed the repository from `claude-code-plugins-dev` to `ai-agent-plugins`, and the marketplace to match. GitHub redirects the old URLs, so existing installs and links keep working.

Claude Code keeps your plugins under the old marketplace name, so commands that use `@ai-agent-plugins` won't find them. To switch:

```
/plugin marketplace remove claude-code-plugins-dev
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install <plugin-name>@ai-agent-plugins
```

Removing the old marketplace uninstalls its plugins, so reinstall the ones you use.

Four plugins merged into others. Claude Code switches an existing install's setting over to the plugin that replaced it, but you still need to install that plugin once:

| Old plugin | Now part of | Run once |
|------------|-------------|----------|
| ai-writing | ai-slop | `/plugin install ai-slop@ai-agent-plugins` |
| ai-aeo, ai-geo | ai-seo | `/plugin install ai-seo@ai-agent-plugins` |
| ai-cvp | ai-security | `/plugin install ai-security@ai-agent-plugins` |

These commands were renamed or merged into another command:

| Old command | New command |
|-------------|-------------|
| `/writing-humanize` | `/slop-rewrite` |
| `/aeo-audit`, `/geo-audit` | `/seo-audit aeo`, `/seo-audit geo` (or `/seo-audit` for all three lenses) |
| `/aeo-fix`, `/geo-fix` | `/seo-fix` |
| `/aeo-faq`, `/aeo-questions`, `/geo-llms-txt` | `/seo-faq`, `/seo-questions`, `/seo-llms-txt` |
| `/cvp-defense-audit` | `/security-cvp-audit` |
| `/git-commit-push` | `/git-commit-push-pr --no-pr` |
| `/workflow-ship` | `/git-commit-push-pr --preflight`, in ai-git |
| `/workflow-preflight` | `/git-preflight`, in ai-git |
| `/modernize-scan` | `/modernize-audit <path> --defaults` |
| `/ado-create-feature`, `/ado-create-story`, `/ado-create-task`, `/ado-work-items` | `/ado-create feature`, `/ado-create story`, `/ado-create task` |
| `/kb-ingest`, `/kb-import`, `/kb-harvest`, `/kb-absorb` | `/kb-add` with a file, folder, repo or URL, or `/kb-add --absorb` |
| `/kb-search`, `/kb-list` | `/kb-query search <terms>`, `/kb-query list` |
| `/kb-organize`, `/kb-remove` | `/kb-prune organize`, `/kb-prune remove <article>` |
| `/kb-upgrade` | `/kb-migrate` |

ai-knowledge 2.0 also changes where the knowledge base lives. See [Knowledge bases from ai-knowledge 1.x](#knowledge-bases-from-ai-knowledge-1x).

If you used `/workflow-ship` or `/workflow-preflight`, install ai-git. Commands removed without a replacement in this marketplace are listed under [Deprecated & Removed](#deprecated--removed).

3.0.0 also removes the `accessibility-auditor`, `modernize-auditor`, `performance-auditor`, `security-dependency-scanner` and `swift-release-auditor` subagents. They couldn't load the skills they wrapped. Run the matching skill with arguments instead, such as `/performance-audit` or `/swift-preflight --check-only`.

In Codex, run `codex plugin marketplace remove claude-code-plugins-dev`, then follow the [Codex steps](#codex).

### Knowledge bases from ai-knowledge 1.x

ai-knowledge 2.0 stores the knowledge base as Claude Code rules instead of a table in CLAUDE.md, so Claude Code loads each article at the right time by itself.

In 1.x, articles lived in `docs/kb/`, and a table in CLAUDE.md told Claude when to read each one. The table loaded in every session, and an article only reached Claude if Claude read the table, matched a row and chose to open the file. Claude Code loads files in `.claude/rules/` on its own:

- **Scoped articles** live in `.claude/rules/kb/` with `paths` frontmatter, such as `src/api/**`. Claude Code loads one when Claude reads, writes or edits a matching file, and a session that never touches those files spends no context on it.
- **Pinned articles** also live in `.claude/rules/kb/`, without `paths`, and load at the start of every session, as they did before.
- **On-demand articles** cover topics rather than files, such as release steps or an external system. They live in `.claude/kb/`, each with one line in `.claude/rules/kb/_index.md`, which loads every session, and Claude opens an article when a task matches its line. This is the only part that still depends on Claude choosing to read a file, the way the whole 1.x table did.

`_index.md` also lists each scoped article with its keywords, so Claude can read one when the topic comes up before it touches a matching file, as a 1.x row's keywords allowed. When a scoped or on-demand article loads, Claude says so in one line, such as `📖 Loaded KB: conventions/api.md`.

Because Claude Code reads `.claude/rules/` itself, teammates get the knowledge base from git without installing the plugin, and CLAUDE.md no longer carries a table. The plugin is what you use to capture, add, query, prune and migrate articles.

The articles can't stay in `docs/kb/` behind short rule files that point to them. Claude Code expands an `@` import inside a rule at the start of every session, even when the rule's `paths` don't match, so every article would load every time.

1.x had `/kb-auto` to remind you to capture learnings. 2.0 replaces it with auto-capture: when you turn it on, Claude saves corrections, rules and decisions the team should know as they come up, without you running `/kb-learn`, and tells you in one line what it saved so you can undo it. `/kb-init` and `/kb-migrate` turn it on for you unless you pass `auto=off`. It's set per developer, so it doesn't change anything for teammates, and it works whether Claude Code's auto memory is on or off. Everything it writes shows up in your diff before it reaches anyone.

Codex and Cursor don't load `.claude/rules/`, so `/kb-init` and `/kb-migrate` also add a short section to `AGENTS.md` that tells those agents how to read the knowledge base (`agents=off` skips it). They can read it but not add to it: the `/kb-*` commands and auto-capture run only in Claude Code.

Two things change for you:

- The knowledge base is now in a hidden folder. If your `.gitignore` excludes `.claude/`, it won't reach git. Every `/kb-*` command checks for this and suggests a fix.
- 2.0 drops Obsidian support. The `related` and `sources` frontmatter and `[[wiki-links]]` become plain paths in an optional Related section, which Claude can follow.

Run `/kb-migrate` once in each project that has a 1.x knowledge base, or `/kb-migrate --dry-run` to preview it first. It sorts each article into scoped, pinned or on-demand from its table row and frontmatter, moves it with `git mv` so its history follows, keeps each row's keywords in its tags, turns links into plain paths, and removes the CLAUDE.md table, the `/kb-auto` block and `docs/kb/.obsidian/`. At the end it turns on auto-capture for you, unless you pass `auto=off`. It also finds notes that still name renamed or removed commands, such as `/writing-humanize` or `/geo-audit`, in the knowledge base, CLAUDE.md, AGENTS.md and `docs/`, and proposes fixes. Run it again after a later update to catch new ones. The [ai-knowledge README](plugins/ai-knowledge/README.md) has the details.

## Deprecated & Removed

Plugins and skills that Claude Code now covers natively, or that moved into another plugin, are retired here. Removed plugins and skills live on in git history.

| Item | Status | Superseded by | Details |
|------|--------|---------------|---------|
| ai-writing (`/writing-humanize`) | 🗑️ Removed (October 2026, v3.0.0) | ai-slop **`/slop-rewrite`** | Same rewrite, now sharing one signal list with `/slop-audit`, and it takes pasted text or a file path as arguments |
| ai-aeo, ai-geo | 🗑️ Removed (October 2026, v3.0.0) | ai-seo **`/seo-audit aeo`**, **`/seo-audit geo`** | One plugin and one audit for SEO, AEO and GEO, with a score per lens. All checks and fixes carried over |
| ai-cvp (`/cvp-defense-audit`) | 🗑️ Removed (October 2026, v3.0.0) | ai-security **`/security-cvp-audit`** | Same sandboxed audit planner, next to `/security-audit` |
| ai-workflow `/workflow-claude-actions` | 🗑️ Removed (October 2026, v3.0.0) | Native **`/install-github-app`** | Its review workflow posts inline comments, and both workflows run on Claude Code's default model, Opus 5.5. To refresh older workflows, run it again and pick "Update workflow file with latest version" |
| ai-workflow `/workflow-principles` | 🗑️ Removed (October 2026, v3.0.0) | Native **`/init`** | `/init` writes CLAUDE.md from the project's own build commands and conventions |
| ai-git `/git-pr-codex-loop` | 🗑️ Removed (October 2026, v3.0.0) | Native **`/code-review --fix`** and **`/autofix-pr`** | Both loop on review comments and CI failures. `/workflow-babysit` still triages Codex Code Review findings as part of its run |
| ai-knowledge `/kb-auto` | 🗑️ Removed (October 2026, v3.0.0) | ai-knowledge **auto-capture** | `/kb-init` and `/kb-migrate` turn it on unless you pass `auto=off`. Claude saves team rules, corrections and decisions to the knowledge base as they come up, and reports each save in one line that offers an undo. It's set per developer and works with Claude Code's auto memory on or off |
| ai-knowledge `/kb-load` | 🗑️ Removed (October 2026, v3.0.0) | Native **@-mentions** | Mention the article's file, such as `@.claude/kb/deploys.md`. Scoped and pinned articles now load by themselves as rules |
| ai-learn (`/learn`, `/learn-review`) | 🗑️ Removed (July 2026) | Native **Learning** output style (`/config` → "Output style" → "Learning") | Built-in collaborative mentor mode with `TODO(human)` markers; an **Explanatory** style also ships natively |
| ai-workflow `/workflow-plan-phases` | 🗑️ Removed (July 2026, v2.0.0) | Native **Dynamic Workflows** | JavaScript runtime orchestrating subagent fan-out with per-agent token budgets; replaces manual 30–50k-token phase sizing |
| ai-workflow `/workflow-implement-phases` | 🗑️ Removed (July 2026, v2.0.0) | Native **Dynamic Workflows** | Runtime-managed orchestration replaces manual `Task()` fan-out and phase-coordination bookkeeping |

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).

## Author

**Charles Jones**

- Website: [charlesjones.dev](https://charlesjones.dev)
- GitHub: [@charlesjones-dev](https://github.com/charlesjones-dev)

## Links

- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Codex plugins](https://learn.chatgpt.com/docs/plugins)
- [Cursor plugins](https://cursor.com/docs/plugins)
- [Agent Plugins specification](https://agent-plugins.org/)
- [Agent Skills specification](https://agentskills.io/specification)

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=charlesjones-dev/ai-agent-plugins&type=date&legend=bottom-right&sealed_token=_0yv5MGXVJ1oD5GXaPNG5bkcHVoquKUyqcfEsy0s4G9DScPsO-0c-mdNKq9Azb5rK8laSJeQe1yfD0SbfA2OnhgIP3jkbS-_Ygm5B0vLqnAOQeC6dKQjZKh_y3h3X8azNaQLG8fOidK3SLPhlOB9MKSNrHg-kB1xDFDVtOsTypQ-ztjPzxdjM_t5yLiN)](https://www.star-history.com/?type=date&legend=bottom-right&repos=charlesjones-dev%2Fai-agent-plugins)
