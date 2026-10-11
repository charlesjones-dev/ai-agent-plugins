# Knowledge base format

Every `/kb-*` skill in ai-knowledge 2.x works from this file. Read it before changing anything. Each skill keeps an identical copy.

## Layout

The knowledge base is stored as Claude Code rules, so Claude Code loads it without any instructions in CLAUDE.md. Paths are relative to the project root, the directory Claude Code was started in. Work only there: never create a knowledge base in a subdirectory or edit a subdirectory's CLAUDE.md.

```text
.claude/
  rules/kb/                  Claude Code loads these files by itself
    _index.md                every session: one line per scoped or on-demand article
    _global-learnings.md     every session: short cross-cutting rules
    {category}/{name}.md     scoped article (has `paths`) or pinned article (no `paths`)
  kb/                        never loaded by itself
    README.md                explains the layout to people browsing the repo
    _log.md                  append-only activity log
    {category}/{name}.md     on-demand article
```

Each article has one of three load modes:

| Mode | Location | `paths` | When it loads | Context cost |
|---|---|---|---|---|
| Scoped | `.claude/rules/kb/{category}/` | Yes | When Claude reads, writes or edits a file that matches `paths`, or reads it because a task matches its line in `_index.md` | One index line every session; the article only in sessions that load it |
| Pinned | `.claude/rules/kb/` (`_global-learnings.md` or a category folder) | No | At the start of every session | Every session |
| On-demand | `.claude/kb/{category}/` | No | When Claude reads it because the task matches its line in `_index.md` | One index line every session |

Prefer scoped. Use on-demand for knowledge that isn't tied to file paths, such as release steps, external systems or lessons from an incident. Pin only short rules that apply to nearly every task.

Keep what loads every session small:

- **Pinned articles**: few, and together under about 100 lines. They load in full every session.
- **`_index.md`**: one short line per scoped or on-demand article, so it grows with the knowledge base. Keep it under about 150 lines, below the 200 lines the Claude Code docs recommend for an instruction file. Past that, merge or prune articles.

To change an article's mode, move it to the other tree (keep its category folder), add or remove `paths`, and update its line in `_index.md` (pinned articles have none).

## How Claude Code treats these files

From the Claude Code memory docs (code.claude.com/docs/en/memory) and testing on Claude Code 2.1.296:

- Every `.md` file under `.claude/rules/` is a rule, found recursively. A rule without `paths` loads every session, so never put a README, log, draft or scratch note under `.claude/rules/kb/`.
- `paths` is the only frontmatter field Claude Code reads. It removes the frontmatter before loading a rule, so the other fields cost no context, and Claude can't see them in a loaded article. That's why cross-references go in the body (see Related articles).
- `paths` holds globs relative to the project root. Quote each one. Write `**/` for any depth (`**/*.controller.ts`) and `/**` for a folder (`src/api/**`). Brace expansion works (`src/**/*.{ts,tsx}`). In testing, a bare `*.ts` also matched nested files, but the docs describe `*.md` as matching the root only, so always write the `**/` form.
- Never give an article `paths` that match the knowledge base's own folders (`.claude/rules/kb/**`, `.claude/kb/**`, or 1.x `docs/kb/**`). Claude reads those files whenever it reads, saves or queries an article, so the article would load with nearly every knowledge base action. Scope it to what it's actually about (such as `**/CLAUDE.md`), or make it on-demand.
- Scoped rules load on Read, Write and Edit (and on `cat` or `head` of a single file), not on Grep or Glob.
- Keep the YAML valid. The docs say a rule whose frontmatter doesn't parse loses `paths` and loads every session; in testing, a rule with an unclosed list didn't load at all. Quote any value that contains `*`, `{`, `:` or `#`.
- Don't write `@path` imports in an article. Claude Code expands an import inside a rule at session start even when the rule's `paths` don't match, which defeats scoping. Put package names, decorators and handles that start with `@` in backticks.
- A matching scoped article loads in full. Aim for 50 to 150 lines per article, and split larger ones by area.

## Checks every skill runs first

1. **1.x layout.** The project has a 1.x knowledge base if any of these is true:
   - `CLAUDE.md` or `.claude/CLAUDE.md` has a `Knowledge Base` heading followed by a table with a `When to Load` column;
   - either file contains `<!-- kb-auto: enabled -->`;
   - `docs/kb/` contains a `.md` file.

   Skills other than `/kb-init` and `/kb-migrate` then stop without writing anything and say: "This project has a 1.x knowledge base (the CLAUDE.md table and `docs/kb/`). Run `/kb-migrate` once to move it to the new layout, then run this command again." Never write to the 1.x layout.
2. **2.x layout.** The knowledge base exists if `.claude/rules/kb/_index.md` exists. If it doesn't, skills other than `/kb-init` and `/kb-migrate` say "There's no knowledge base here yet. Run `/kb-init` first." and stop.
3. **Git.** Run `git rev-parse --is-inside-work-tree`. In a git repository, run `git check-ignore -q .claude/rules/kb/_index.md` and `git check-ignore -q .claude/kb/README.md` (this works before the files exist). If either is ignored, warn that teammates won't get the knowledge base, and suggest a fix, for example replacing a `.claude/` line in `.gitignore` with `.claude/*`, `!.claude/rules/` and `!.claude/kb/`. Don't edit `.gitignore` without asking.

## Frontmatter

Every article starts with YAML frontmatter:

```yaml
---
paths:
  - "src/api/**"
  - "**/*.controller.ts"
tags: [api, rest, conventions]
created: 2026-04-02
last-updated: 2026-04-02
---
```

| Field | Required | Meaning |
|---|---|---|
| `paths` | Scoped articles only | Globs that make Claude Code load the article. Put it first. Leave it out entirely (not empty) for pinned and on-demand articles. |
| `tags` | Yes | Lowercase topic tags. They're also the keywords on the article's `_index.md` line. Content from another repo gets a `module:{name}` tag. |
| `created` | Yes | Date the article was created (`YYYY-MM-DD`). |
| `last-updated` | Yes | Date its knowledge last changed. Moving a file or reformatting frontmatter doesn't change it. |
| `source` | For content taken from files or URLs | Where it came from: a path or URL, or a list of them. `/kb-add` uses it to refresh the article later. |
| `discovered-from` | For `/kb-discover` articles | The directories or files that were analyzed. |
| `type`, `query` | For answers filed by `/kb-query` | `type: synthesis` and the question. The articles consulted go in the Related section. |

Keep any other fields a file already has. In 1.x, `scope` held the globs, `pinned: true` marked pinned articles, and `related` and `sources` held `[[name]]` links. In 2.x, `scope` is `paths`, the location decides pinning, and links are plain paths in the body. If a 2.x article still has any of these fields or a `[[name]]` link, tell the user that `/kb-migrate` fixes them.

## Related articles

- An article can end with an optional `## Related` section that lists other articles bearing on the same tasks, one repo-relative path in backticks per line (`- \`.claude/rules/kb/security/auth-rules.md\``). Claude Code strips frontmatter, so the body is the only place Claude sees cross-references, and it can follow a plain path. Leave the section out when nothing is worth following.
- There's no frontmatter field for links. When a link helps in both directions, add it to both articles.
- When an article moves or is deleted, update or remove the Related entries that point at it.

## The index rule

`.claude/rules/kb/_index.md` has no `paths`, so it loads every session. It has one line for every scoped and on-demand article. Pinned articles have no line, because they're always loaded. Each line gives the path, a short summary and the keywords from `tags`. A scoped line also names its `paths` after "loads with", so a 1.x row's keywords still load a scoped article when no file matches. Sort the lines by path:

```markdown
---
tags: [index, meta]
created: {date}
last-updated: {date}
---

# Knowledge base

This project keeps team knowledge in `.claude/rules/kb/` and `.claude/kb/`. Pinned articles in `.claude/rules/kb/` load in every session. The articles listed below don't:

- When a task involves an article's keywords, read it before you start, unless it's already in your context, and say so in one line: `📖 Reading KB: tools/deployment.md`.
- An article marked "loads with" also loads by itself when you read or edit a file matching those globs. Claude Code adds it as a system reminder that begins `Contents of` followed by the article's path under `.claude/rules/kb/`. The first time each one arrives that way, tell the user on its own line in your reply, even though it came from a system reminder: `📖 Loaded KB: conventions/api.md` (the path after `.claude/rules/kb/`). Pinned articles get no notice.
- If an article's Related section lists others that bear on the task, read those too.

## Articles

- `.claude/kb/tools/deployment.md`: release steps and rollback rules (deploy, release, rollback)
- `.claude/rules/kb/conventions/api.md`: API error format (api, errors; loads with src/api/**)
```

With no scoped or on-demand articles, the list is the single line `- None yet.` Whenever an article is added, moved, deleted, re-scoped or re-tagged, update its line. Change `last-updated` only when the list changes.

## The README

`.claude/kb/README.md` is for people browsing the repository. Claude Code never loads it. Write it with this content:

```markdown
# Knowledge base

This is the project's team knowledge base. Claude Code loads it on its own; the ai-knowledge plugin adds the `/kb-*` commands that write and maintain it.

- `.claude/rules/kb/` holds articles Claude Code loads by itself. An article with `paths` frontmatter loads when Claude reads or edits a matching file. One without `paths`, such as `_global-learnings.md`, loads in every session. `_index.md` lists every article that isn't pinned, with its keywords, so Claude can also read one when a task matches.
- `.claude/kb/` holds on-demand articles, which Claude reads when a task matches their line in `_index.md`, plus this README and `_log.md`.

Keep secrets out of every article: this folder is committed and shared.

Commands: `/kb-add`, `/kb-learn`, `/kb-discover`, `/kb-query`, `/kb-prune`.
```

## The AGENTS.md pointer

Claude Code loads the knowledge base by itself. Agents that don't load `.claude/rules/`, such as Codex and Cursor, read `AGENTS.md` instead, so `/kb-init` and `/kb-migrate` keep this section in the project-root `AGENTS.md`, creating the file if it doesn't exist. With `agents=off`, they leave it out and remove it if it's there.

Write it exactly as below, including the two marker comments, so a later run can find and replace it. Add it at the end of the file, and never change anything outside the markers. If the section is already there but differs from this template, replace everything between the markers.

```markdown
<!-- ai-knowledge:start -->
## Team knowledge base

This project keeps its team knowledge base in `.claude/`. Claude Code loads it by itself. Other agents, read it like this:

- At the start of a task, read `.claude/rules/kb/_index.md`, plus every article under `.claude/rules/kb/` whose frontmatter has no `paths` (such as `_global-learnings.md`).
- Before you read or change a file, check the `paths` globs in the frontmatter of the other articles under `.claude/rules/kb/`, and read each article whose globs match that file.
- When a task matches a line in `_index.md`, read the article that line names.

Follow these articles the way you follow the rest of this file.
<!-- ai-knowledge:end -->
```

Claude Code reads `AGENTS.md` only when the project has no `CLAUDE.md`, or when `CLAUDE.md` imports it. Either way the section is addressed to other agents, so it doesn't change what Claude Code loads.

## The log

`.claude/kb/_log.md` is append-only, newest entry last. If it's missing, create it with `tags: [log, meta]`, `created` and `last-updated` in the frontmatter and a `# Knowledge base log` heading. Append an entry only after files changed, and set the log's `last-updated` to the entry's date:

```markdown
## [YYYY-MM-DD] {operation} | {one-line summary}
- Created: {paths}
- Updated: {paths}
```

Operations are `init`, `migrate`, `add`, `learn`, `discover`, `query` and `prune`.

## Dates

Never guess, infer or increment a date. Before the first write, get today's date once from the first command that works, and use that value for every `created`, `last-updated` and log entry in the run:

- macOS, Linux, WSL, Git Bash: `date +%Y-%m-%d`
- Windows PowerShell or pwsh: `Get-Date -Format 'yyyy-MM-dd'`
- Windows cmd.exe: `powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd'"`
- With Node or Python: `node -e "console.log(new Date().toISOString().slice(0,10))"` or `python -c "import datetime; print(datetime.date.today().isoformat())"`

Change `last-updated` only when an article's knowledge changed. Don't rewrite a file whose content would come out the same.

## Writing articles

- Distill; don't paste. Write rules in the imperative ("Use X", "Never do Y") with just enough of the reason that the rule isn't followed blindly. Prefer bullets to prose.
- Cover one topic per article. Use this body:

  ```markdown
  # {Topic}

  {One or two sentences: what this covers and when it applies.}

  ## Key rules

  - {Rule}

  ## Context

  {Optional background.}

  ## Related

  - `.claude/kb/tools/other-article.md`
  ```

  The Context and Related sections are optional.

- Never store secrets: API keys, tokens, passwords, connection strings, private hostnames or IP addresses, cookies or session data. Record the rule instead ("Service X's key comes from the `X_API_KEY` environment variable") and tell the user what you left out.
- The knowledge base reaches the whole team through git. Personal preferences belong in Claude Code's auto memory or `CLAUDE.local.md`, not here.
- Read the existing articles before writing. Update an entry rather than adding a duplicate, and when new information contradicts an old rule, replace the old rule.
- Name files in kebab-case after the topic (`api-error-format.md`). Use category folders such as `architecture/`, `conventions/`, `testing/`, `tools/`, `domain/` and `external/`, and reuse folders that already exist. A knowledge base with fewer than five articles can stay flat.

## Auto-capture

Auto-capture is set per developer and per project. It stays off for a developer until they run `/kb-init` or `/kb-migrate`, which turn it on unless given `auto=off`. When it's on, the plugin's SessionStart hook adds a short instruction to Claude's context at the start of each session and again after `/clear` and compaction. Claude then saves corrections, stated rules, settled decisions and confirmed gotchas as they come up, by invoking `kb-learn` with `auto`, and reports each save in one line that offers an undo. The hook prints nothing when auto-capture is off or the project has no 2.x knowledge base.

The setting is never committed and never changes a shared file:

| Project | Where the setting lives | On | Off |
|---|---|---|---|
| Git repository | `git config --local ai-knowledge.autoCapture` (in `.git/config`, shared by the clone's worktrees) | `git config --local ai-knowledge.autoCapture true` | `git config --local ai-knowledge.autoCapture false` |
| Not a git repository | `env.AI_KNOWLEDGE_AUTO_CAPTURE` in `.claude/settings.local.json` | `"1"` | `"0"` |

- When the `AI_KNOWLEDGE_AUTO_CAPTURE` environment variable is set (from the shell or any settings file's `env`), it decides: `1`, `true`, `on` or `yes` means on, and any other value means off. Otherwise git config decides, with the same values. Otherwise it's off. A developer can turn it on in every repository with `git config --global ai-knowledge.autoCapture true`.
- **Reading it**: check the variable first (`printenv AI_KNOWLEDGE_AUTO_CAPTURE`, or `$env:AI_KNOWLEDGE_AUTO_CAPTURE` in PowerShell). If it's unset, run `git config --get ai-knowledge.autoCapture` in the project, or read `.claude/settings.local.json` outside git. Report where the value came from.
- **Changing it**: in a git repository, run the command from the table. Write `false` rather than unsetting, so a global `true` doesn't apply. Outside git, set `env.AI_KNOWLEDGE_AUTO_CAPTURE` in `.claude/settings.local.json`, keeping everything else in the file, or create the file with only that key. If the variable is also set somewhere else with a different value, tell the user which one wins.
- The hook reads the setting when a session starts, so a change applies from the next session or `/clear`. After turning it on, follow auto-capture for the rest of the current session as well.

## Moving and deleting files

- Create the destination folder first (`mkdir -p`, or `New-Item -ItemType Directory -Force` in PowerShell). `git mv` fails when it's missing.
- Move files that git tracks (`git ls-files --error-unmatch {path}` succeeds) with `git mv`, so their history follows them. Move untracked files, and files outside a git repository, with a plain move.
- Delete only after the user confirms, with `git rm` for tracked files.
- After a move or delete, update `_index.md`, the Related entries in other articles and any other text that used the old path.
- If you can't ask the user a question (no AskUserQuestion tool), print the question and its options as text and end your turn. Never treat silence as approval.
