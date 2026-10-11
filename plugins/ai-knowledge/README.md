# AI Knowledge Plugin

Keeps a team knowledge base in git as Claude Code rules. Each article loads when Claude works on the files it covers, in every session, or on demand from a short index, so the knowledge reaches Claude without anyone asking for it. With auto-capture on, Claude also adds to it as you work.

## Overview

The plugin writes what your team learns (things that didn't work, conventions, client requirements, codebase gotchas) into short topic articles and stores them where Claude Code loads them natively:

- **Scoped articles** live in `.claude/rules/kb/` with `paths` frontmatter. Claude Code loads one when Claude reads, writes or edits a matching file, and Claude also reads one when a task matches its keywords in the index.
- **Pinned articles** live in `.claude/rules/kb/` without `paths`. Claude Code loads them at the start of every session, so keep them few and short. `_global-learnings.md` is one.
- **On-demand articles** live in `.claude/kb/`. They're for knowledge that isn't tied to file paths, such as release steps or an external system. Claude reads one when a task matches its keywords in the index.

An always-loaded index rule, `.claude/rules/kb/_index.md`, lists every scoped and on-demand article in one line with its keywords (and, for scoped ones, its paths). Whenever Claude reads an article from the index, or a scoped article loads because Claude opened a matching file, Claude says so in one line, such as `📖 Loaded KB: conventions/api.md`, so you know which knowledge is in play. Pinned articles load without a notice.

Because the knowledge base is made of ordinary rule files, Claude Code loads it for everyone who clones the repository, with or without the plugin. The plugin adds the commands that write, query and maintain it.

The approach is inspired by Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, where the LLM does the filing and cross-referencing.

## How It Relates to Claude Code's Memory

Claude Code already has three ways to remember things. This plugin builds on rules and works whether auto memory is on or off.

| | What it holds | Shared | Loads |
|---|---|---|---|
| **CLAUDE.md** | Instructions for every session: build commands, layout, conventions that apply everywhere | Through git | Every session |
| **Auto memory** (can be turned off) | Notes Claude writes for itself on your machine: your preferences, corrections, project context | No, one machine | First 200 lines of `MEMORY.md` every session |
| **Rules** (`.claude/rules/`) | Topic files, optionally scoped to paths | Through git | Every session, or when matching files are touched |
| **This plugin** | Team knowledge, written as rules plus an index of articles that aren't pinned. Claude adds to it as you work when auto-capture is on | Through git | Per article: scoped, pinned or on demand |

Auto memory and auto-capture both save as you work, but auto memory keeps personal notes on one machine and skips what Claude can work out from the code, while auto-capture writes team rules into the repository for everyone. Many developers run with auto memory off; auto-capture doesn't need it. Keep CLAUDE.md for what every session needs, and use `/kb-add --absorb` to move area-specific sections out of it into scoped articles.

## Commands

| Command | Description |
|---------|-------------|
| `/kb-init [auto=off] [agents=off]` | Set up `.claude/rules/kb/` and `.claude/kb/`, turn on auto-capture for you (`auto=off` to skip), and add a short `AGENTS.md` section for Codex and Cursor (`agents=off` to skip). On an existing knowledge base, report auto-capture and switch it with `auto=on` or `auto=off` |
| `/kb-migrate [--dry-run] [auto=off] [agents=off]` | Move a 1.x knowledge base (CLAUDE.md table and `docs/kb/`) to the new layout, turn on auto-capture for you (`auto=off` to skip), and add the `AGENTS.md` section (`agents=off` to skip). Also fix references to renamed or removed marketplace commands. On a 2.x knowledge base, check and repair the format and run the same command check |
| `/kb-add [note \| path \| URL ... \| --absorb]` | Add a note, project files, a folder, another repo or a web page. `--absorb` reviews CLAUDE.md and `docs/` for content to move |
| `/kb-learn [focus]` | Review what the current conversation taught and save it. Claude also runs it on its own (`auto`) for auto-capture, or when you ask it to save something to the knowledge base |
| `/kb-discover [paths] [--focus topics]` | Write down conventions found in the source code |
| `/kb-query <question> \| search <terms> \| tag:<tag> \| list` | Answer from the knowledge base with citations, search it, or list every article and how it loads |
| `/kb-prune [remove <article> \| organize]` | Find and fix duplicates, contradictions, broken links, stale articles and globs that match nothing. Remove one article, or sort articles into folders |

Every command shows its plan or draft and asks before it writes. The exceptions are auto-capture and saves you ask for in conversation, which write one learning and report it in one line that offers an undo.

## Installation

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-knowledge@ai-agent-plugins
```

## Getting Started

1. Run `/kb-init` in the project root. It also turns on auto-capture for you; use `/kb-init auto=off` to leave it off. If the project has a 1.x knowledge base, it tells you to run `/kb-migrate` instead.
2. If CLAUDE.md or `docs/` already holds area-specific rules, run `/kb-add --absorb` to move them into articles.
3. Run `/kb-discover` to capture conventions the code follows but nobody wrote down.
4. At the end of a productive conversation, run `/kb-learn`. For a single rule, run `/kb-add` followed by the rule.
5. Commit `.claude/rules/kb/` and `.claude/kb/`.
6. Run `/kb-prune` now and then.

## Auto-capture

Auto-capture saves team knowledge as it comes up, the way auto memory saves personal notes, so you don't have to remember to run `/kb-learn`. It's set per developer: `/kb-init` and `/kb-migrate` turn it on for you unless you pass `auto=off`, and it stays off for teammates until they run one of them.

**What it saves.** When it's on, the plugin's SessionStart hook adds a short instruction to Claude's context at the start of each session and again after `/clear` or compaction. Claude watches for knowledge a teammate's session would also need: a correction to how something is done in the project, a rule or convention you state, a decision you settle, or a gotcha it confirms in the code. When one comes up, it runs `kb-learn` with `auto`, which:

- checks the knowledge base first and updates an existing article rather than adding a duplicate, replacing a rule the new one contradicts;
- skips personal preferences, details of the current task, things the code already shows, and secrets;
- picks the load mode: scoped with `paths` when the learning is tied to files, `_global-learnings.md` only for short rules that apply everywhere, and on demand otherwise;
- updates `_index.md` and `_log.md`.

**Notices and undo.** Each save ends Claude's reply with one line, for example:

```text
📖 Saved to KB: conventions/api-errors.md (scoped to src/api/**). Say "undo" to remove it.
```

Saying "undo" reverses that save: it deletes the new article, or restores the article it changed, and removes the log entry. Nothing is committed, so everything auto-capture writes shows up in `git diff` for review before you commit it.

**Permission prompts.** Claude Code protects the `.claude/` folder: allow rules in settings can't pre-approve writes there, so how a save goes depends on the permission mode. In auto mode, the default for interactive sessions since Claude Code v2.1.283, the classifier reviews each save; in testing it allowed them without a prompt. In accept-edits and manual mode, the first save in a session asks; choose "Yes, and allow Claude to edit files in this project's .claude folder for this session" and the rest of the session's saves go through. Bypass mode doesn't ask.

**Turning it on and off.** `/kb-init` and `/kb-migrate` turn it on unless you pass `auto=off`. Running `/kb-init` again on an existing knowledge base keeps your earlier choice, and `/kb-init auto=on` or `/kb-init auto=off` switches it. The setting is per developer and per project, and it never touches a shared file:

- In a git repository it's `git config --local ai-knowledge.autoCapture true` (or `false`), stored in `.git/config` and shared by the clone's worktrees. `git config --global ai-knowledge.autoCapture true` turns it on in every repository that has a 2.x knowledge base.
- Outside git it's `"env": { "AI_KNOWLEDGE_AUTO_CAPTURE": "1" }` in `.claude/settings.local.json`.
- The `AI_KNOWLEDGE_AUTO_CAPTURE` environment variable (`1` or `0`) overrides both.

A change takes effect from the next session or `/clear`. The hook prints nothing when auto-capture is off or the project has no 2.x knowledge base. It's a POSIX shell script that runs on macOS, Linux and Windows with Git Bash, with a PowerShell version for Windows without Git Bash. Without the instruction, Claude runs `kb-learn` on its own only when you ask it to save something to the knowledge base.

## How Loading Works

```text
.claude/
  rules/kb/
    _index.md                  every session: one line per scoped or on-demand article
    _global-learnings.md       every session: short cross-cutting rules
    conventions/api.md         scoped: loads with files matching its paths
  kb/
    README.md, _log.md         never loaded
    tools/release.md           on demand: read when a task matches its index line
```

A scoped article looks like this:

```markdown
---
paths:
  - "src/api/**"
  - "**/*.controller.ts"
tags: [api, rest]
created: 2026-04-02
last-updated: 2026-08-14
---

# API conventions

## Key rules

- Version every route as /api/v{n}/{resource}.

## Related

- `.claude/rules/kb/security/auth-rules.md`
```

Its index line reads `` `.claude/rules/kb/conventions/api.md`: API conventions (api, rest; loads with src/api/**, **/*.controller.ts) ``.

Things to know:

- `paths` is the only field Claude Code reads. It strips the frontmatter before loading an article, so `tags` and dates cost no context. The plugin also records `source` for content from files and URLs, `discovered-from` for `/kb-discover` articles, and `type` and `query` for answers filed by `/kb-query`.
- Because the frontmatter is stripped, cross-references go in an optional `## Related` section at the end of the body, as repo-relative paths Claude can follow.
- Scoped articles load by themselves when Claude reads, writes or edits a matching file, not when it only searches. Their index line also lets Claude read one when a task matches its keywords before any file is opened.
- On-demand articles depend on Claude acting on the index, so for anything tied to files, scoped is more reliable.
- An `@path` import inside a rule loads at session start even when the rule's paths don't match, so articles don't use imports.
- Run `/context` to see which rules loaded at launch: the index and the pinned articles.
- Keep what loads every session small: pinned articles under about 100 lines in total, and the index under about 150 lines (one line per article). `/kb-prune` flags both.

## Codex, Cursor and other agents

The plugin runs only in Claude Code, but the knowledge base is plain Markdown that any agent can read. Codex and Cursor read `AGENTS.md`, not `.claude/rules/`, so `/kb-init` and `/kb-migrate` add a short section to `AGENTS.md` (creating the file if needed) that tells them how to use it:

- read `_index.md` and the pinned articles at the start of a task;
- before reading or changing a file, read the scoped articles whose `paths` match it;
- read the article a line in `_index.md` names when a task matches that line.

In those agents, loading depends on the agent following that section, so it's less reliable than in Claude Code, and nothing is captured: auto-capture and the `/kb-*` commands run only in Claude Code.

The section sits between `<!-- ai-knowledge:start -->` and `<!-- ai-knowledge:end -->`, and nothing else in `AGENTS.md` is touched. Running `/kb-init` again refreshes it, `/kb-migrate` on a 2.x knowledge base repairs it, and `/kb-init agents=off` removes it. Claude Code reads `AGENTS.md` only when the project has no `CLAUDE.md` or `CLAUDE.md` imports it, and the section is addressed to other agents, so it changes nothing in Claude Code.

## Moving from 1.x

Version 2.0.0 replaces the CLAUDE.md "Knowledge Base" table and `docs/kb/` with Claude Code rules. Run `/kb-migrate` once in each project (`/kb-migrate --dry-run` previews it). It:

- moves each article with `git mv`, so history follows it: pinned articles and scoped ones (from `scope` and the table's globs) to `.claude/rules/kb/`, and keyword-only ones to `.claude/kb/`;
- keeps each table row's keywords in the article's `tags`, and lists every scoped and on-demand article in the new index, so a scoped article still loads when a task matches its topic, as the 1.x row allowed;
- turns `scope` into `paths`, drops `pinned` (the location decides now), and rewrites `*.ext` globs as `**/*.ext`;
- drops the `related` and `sources` fields and turns their links, and any `[[name]]` links in article bodies, into plain paths in a `## Related` section. It deletes `docs/kb/.obsidian/` along with `docs/kb/`;
- removes the Knowledge Base section and the kb-auto block from CLAUDE.md, and turns on auto-capture for you unless you pass `auto=off`;
- finds notes that still point at commands this marketplace renamed or removed, such as `/writing-humanize` or `/geo-audit`, or at moved report folders such as `docs/geo-audit/`. It looks in the knowledge base, CLAUDE.md, CLAUDE.local.md, AGENTS.md, other `.claude/rules/` files, `.gitignore` and `docs/`, from a map of every rename and removal since 1.0. Simple renames inside the knowledge base are applied with the migration. For a command that now needs arguments or was removed, it proposes a rewrite of the whole sentence for you to accept, and it changes files outside the knowledge base only when you say yes. In `.gitignore` it adds the new report folder next to the old one. Dated notes, logs and changelogs stay as they are;
- is safe to run again. On a migrated knowledge base it checks the format and runs the same command check, so running `/kb-migrate` after a later marketplace update also catches commands that update renamed.

Every other command stops and points to `/kb-migrate` while a 1.x knowledge base is present, so nothing gets written to the old layout.

| 1.x command | In 2.0.0 |
|---|---|
| `/kb-init` | `/kb-init`, which now sets up the rules layout |
| `/kb-learn` | `/kb-learn`, which Claude can now also run itself for auto-capture |
| `/kb-add` | `/kb-add <note>` |
| `/kb-ingest` | `/kb-add <path>` |
| `/kb-harvest` | `/kb-add <path outside the project, glob or URL>` |
| `/kb-absorb` | `/kb-add --absorb` |
| `/kb-import` | `/kb-add <path under .claude/rules/kb/ or .claude/kb/>`. Nothing needs registering any more |
| `/kb-discover` | `/kb-discover` |
| `/kb-query` | `/kb-query <question>` |
| `/kb-search` | `/kb-query search <terms>` or `/kb-query tag:<tag>` |
| `/kb-list` | `/kb-query list` |
| `/kb-load` | Claude Code loads scoped and pinned articles itself. To pull in any other article, @-mention it in your prompt (`@.claude/kb/tools/release.md`) |
| `/kb-prune` | `/kb-prune` |
| `/kb-organize` | `/kb-prune organize` |
| `/kb-remove` | `/kb-prune remove <article>` |
| `/kb-upgrade` | `/kb-migrate`, which also checks the format of a 2.x knowledge base |
| `/kb-auto` | Auto-capture, which `/kb-init` and `/kb-migrate` turn on unless you pass `auto=off`. It's per developer instead of a CLAUDE.md block, and Claude saves as it works instead of offering at the end. Claude Code's auto memory is a separate, machine-local option |

## Plugin Details

- **Version**: 2.0.0
- **Author**: [Charles Jones](https://charlesjones.dev)
- **License**: MIT

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
