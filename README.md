# Claude Code Plugins for Developers

[![Version](https://img.shields.io/badge/version-2.12.0-blue.svg)](https://github.com/charlesjones-dev/claude-code-plugins-dev/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/charlesjones-dev/claude-code-plugins-dev.svg)](https://github.com/charlesjones-dev/claude-code-plugins-dev/stargazers)

Claude Code plugins for code audits, release checks and day-to-day git and project workflows. There are 17 plugins; each adds its own slash commands, so install only the ones you need.

## Available Plugins

> **Usage note:** Each skill is a slash command, for example `/accessibility-audit`. Interactive skills ask for what they need; the rest run directly on your codebase. A few take flags, such as `/seo-fix --dry-run` and `/swift-verify --fix`. See each plugin's README.

| Plugin | Description | Skills (Slash Commands) | Agents |
|--------|-------------|------------------------|--------|
| [ai-accessibility](plugins/ai-accessibility/) | WCAG audits of code, or a live URL through Playwright MCP | `/accessibility-audit` | `accessibility-auditor` |
| [ai-ado](plugins/ai-ado/) | Azure DevOps work items, hour logging and timesheets through the Azure DevOps MCP server | `/ado-init`, `/ado-work-items`, `/ado-create-feature`, `/ado-create-story`, `/ado-create-task`, `/ado-log-story-work`, `/ado-timesheet-report` | - |
| [ai-aeo](plugins/ai-aeo/) | Answer Engine Optimization: checks that pages are ready to be the direct answer in featured snippets, voice assistants and answer boxes, maps questions to pages and builds FAQ sections | `/aeo-audit`, `/aeo-fix`, `/aeo-questions`, `/aeo-faq` | - |
| [ai-compliance](plugins/ai-compliance/) | License audits of open-source dependencies, plus NOTICE and ATTRIBUTION file generation | `/compliance-license-audit`, `/compliance-notice-generate` | - |
| [ai-cvp](plugins/ai-cvp/) | Plans a sandboxed security audit on the strongest model you can use: read-only recon, a tailored audit prompt and launch checklist, and a prompt for verifying and fixing what the audit proves | `/cvp-defense-audit` | - |
| [ai-geo](plugins/ai-geo/) | Generative Engine Optimization: AI crawler rules, topical authority, evidence, authorship and third-party validation checks for being cited in AI answers, plus llms.txt | `/geo-audit`, `/geo-fix`, `/geo-llms-txt` | - |
| [ai-git](plugins/ai-git/) | .gitignore generation, commit and push, PR creation, and a Codex review loop | `/git-init`, `/git-commit-push`, `/git-commit-push-pr`, `/git-pr-codex-loop` | - |
| [ai-knowledge](plugins/ai-knowledge/) | Git-versioned team knowledge base in `docs/kb/`, browsable in Obsidian, next to Claude Code's per-machine auto memory | `/kb-init`, `/kb-learn`, `/kb-add`, `/kb-query`, `/kb-import`, `/kb-ingest`, `/kb-harvest`, `/kb-discover`, `/kb-absorb`, `/kb-remove`, `/kb-load`, `/kb-list`, `/kb-search`, `/kb-prune`, `/kb-auto`, `/kb-organize`, `/kb-upgrade` | - |
| [ai-modernize](plugins/ai-modernize/) | Technical debt audits for code written with older AI models | `/modernize-audit`, `/modernize-scan` | `modernize-auditor` |
| [ai-performance](plugins/ai-performance/) | Performance bottleneck audits with an impact score for each finding | `/performance-audit` | `performance-auditor` |
| [ai-security](plugins/ai-security/) | Security audits with Markdown/JSON reports that track findings across runs, a live-site dependency scan, and settings and supply-chain hardening. Complements native `/security-review` | `/security-init`, `/security-audit`, `/security-scan-dependencies`, `/security-supply-chain` | `security-auditor`, `security-dependency-scanner` |
| [ai-seo](plugins/ai-seo/) | SEO audits that catch deprecated patterns LLMs still generate, with framework-specific fixes | `/seo-audit`, `/seo-fix`, `/seo-schema` | - |
| [ai-slop](plugins/ai-slop/) | Audits user-facing copy, layouts and metadata for AI-written tells and factual errors, like a privacy policy that misses the trackers the code loads | `/slop-audit` | - |
| [ai-statusline](plugins/ai-statusline/) | Adds progress bars, rate-limit widgets, a month-to-date spend budget for accounts without rate limits, and effort-level and sandbox indicators to Claude Code's native `/statusline` | `/statusline-wizard`, `/statusline-edit` | - |
| [ai-swift](plugins/ai-swift/) | Swift/iOS/macOS release checks that catch Xcode Cloud and TestFlight blockers before upload | `/swift-preflight`, `/swift-diagnose`, `/swift-ci-scaffold`, `/swift-verify`, `/swift-concurrency-review` | `swift-release-auditor` |
| [ai-workflow](plugins/ai-workflow/) | Preflight checks, a commit-push-PR ship skill, an unattended run that takes a branch through Claude Code, Codex and Cursor Bugbot review, merge and deploy, Claude Code GitHub Actions setup on the newest Opus, a Development Principles generator and CLAUDE.md behavior rules | `/workflow-preflight`, `/workflow-ship`, `/workflow-babysit`, `/workflow-claude-actions`, `/workflow-principles`, `/workflow-rules` | - |
| [ai-writing](plugins/ai-writing/) | Rewrites text to remove AI writing patterns | `/writing-humanize` | - |

> **Note on audit plugins:** The audit plugins read your code and report what they find, and a few can also check a live URL. Use them to catch problems during development, then confirm with runtime testing and manual review.

## Quick Start

[Install Claude Code](https://www.claude.com/product/claude-code) first.

1. Add this marketplace:

```
/plugin marketplace add charlesjones-dev/claude-code-plugins-dev
```

2. Install the plugins you want from the table above:

```
/plugin install <plugin-name>@claude-code-plugins-dev

# For example:
/plugin install ai-git@claude-code-plugins-dev
/plugin install ai-security@claude-code-plugins-dev
```

3. Run any of the plugin's slash commands:

```
/git-init              # Generate a .gitignore for the project
/security-init         # Add file-access deny rules for secrets
/ado-init              # Set up Azure DevOps and its MCP server
```

## Deprecated & Removed

As Claude Code ships features natively, plugins and skills that duplicate them are retired here. Removed plugins and skills live on in git history.

| Item | Status | Superseded by | Details |
|------|--------|---------------|---------|
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

- [Claude Code plugins documentation](https://docs.claude.com/en/docs/claude-code/plugins)

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=charlesjones-dev/claude-code-plugins-dev&type=date&legend=bottom-right&sealed_token=_0yv5MGXVJ1oD5GXaPNG5bkcHVoquKUyqcfEsy0s4G9DScPsO-0c-mdNKq9Azb5rK8laSJeQe1yfD0SbfA2OnhgIP3jkbS-_Ygm5B0vLqnAOQeC6dKQjZKh_y3h3X8azNaQLG8fOidK3SLPhlOB9MKSNrHg-kB1xDFDVtOsTypQ-ztjPzxdjM_t5yLiN)](https://www.star-history.com/?type=date&legend=bottom-right&repos=charlesjones-dev%2Fclaude-code-plugins-dev)

