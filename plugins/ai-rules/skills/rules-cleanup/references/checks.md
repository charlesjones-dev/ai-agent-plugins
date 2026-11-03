# Cleanup checks

Work through these checks in order. Each one names the finding kind it produces. The examples are typical cases, not a complete list, and they can go out of date. Before you report one, confirm it against the files, your own system prompt and the tools in this session.

## 1. Built-in: restates Claude Code's own instructions

Claude Code's system prompt already covers a lot of everyday behavior. A CLAUDE.md line that says the same thing costs context and changes nothing.

Typical examples. Report one only after you find the matching instruction in your own system prompt:

- Read a file before editing it. Prefer editing an existing file to creating a new one. Don't create documentation files unless asked.
- Don't add features, refactors or abstractions beyond what the task needs.
- Commit or push only when asked. Don't force push, rewrite history or skip hooks without being asked.
- Confirm before risky, hard-to-reverse or outward-facing actions.
- Use the dedicated file and search tools instead of shell commands where one fits. Run independent tool calls in parallel.
- Use the `gh` CLI for GitHub.
- Report results honestly, including failed tests and skipped steps.
- Reference code as `file_path:line_number`.

Not Built-in:

- A rule that changes a default, such as "commit after each finished task" or "never ask before running the test suite". That is an override. Keep it, and list it under "Kept on purpose".
- A rule that adds detail the default lacks, such as which test command to run or which branch to target.

## 2. Setting: a setting or hook would enforce it

CLAUDE.md is guidance that Claude reads. Settings, permission rules and hooks are enforced by Claude Code itself, so they work even when the guidance is missed. Propose the change, and show the exact JSON or hook and the file it goes in: `~/.claude/settings.json` for the user, `.claude/settings.json` for the project (shared), or `.claude/settings.local.json` (personal). Check the setting names against the Claude Code settings docs before you quote them.

| A rule like | Is better as |
|-------------|--------------|
| "Never read `.env` or the secrets folder" | A `permissions.deny` rule, such as `"permissions": { "deny": ["Read(./.env)", "Read(./secrets/**)"] }` |
| "You may run the tests without asking" | A `permissions.allow` rule for that command |
| "Never add a Co-Authored-By trailer or a 'Generated with' line" | `"attribution": false` (Claude Code v2.1.281 or later. On earlier versions, set `attribution.commit` and `attribution.pr` to `""`) |
| "Run the formatter after every edit" | A `PostToolUse` hook that matches `Edit|Write` and runs the formatter |
| "Always use model X" or "think hard on every task" | The `model` setting or `/model`, and `/effort` |
| "Keep replies short" or "explain as you go" | An output style, such as `/output-style concise` |
| "Set NODE_ENV=test when you run tests" | The `env` setting, or the test script itself |
| A status line or terminal display preference | `/statusline` |

Keep the rule when no setting covers all of it. Then report only the part a setting covers.

## 3. Stale: points at things that are gone

Check each of these before you report it:

- Paths to files or folders that don't exist.
- Scripts and commands that aren't in `package.json`, the `Makefile`, `justfile`, `scripts/` or the CI config.
- Tool names that aren't in this session's tool list. Tools get renamed, so a rule can name a tool that no longer exists.
- Slash commands and skills that aren't in this session's skills list. Plugins rename and remove commands.
- Model names and IDs older than the models available now.
- Hosts, services, branches or environments the repo no longer uses, when the repo shows the replacement.
- Dates in the past attached to "for now", "until" or "temporarily".

Propose the fix when the replacement is clear. Otherwise propose deleting the line, and say what you checked.

## 4. Conflict: rules disagree

Compare every rule against the others:

- Within one file, such as "keep PR bodies short" and a PR template with eight sections.
- Across files. Claude Code loads all these files together, so when two rules contradict, Claude may follow either one. A conflict with the managed policy file keeps the policy rule, because the user can't change or exclude that file.
- Against an ai-rules managed section. Propose changing the unmanaged rule, or changing the section with `/rules-setup`.

Quote both rules with their file and line. Don't pick a side yourself.

## 5. Low value: costs context for little gain

- **Vague rules** that don't change behavior: "write clean code", "follow best practices", "be careful".
- **Personas**: "You are a senior engineer with 20 years of experience."
- **History**: "We used to use X", changelogs, migration diaries, dated notes about finished work.
- **Inventories Claude can read for itself**: file trees, lists of every npm script, dependency versions copied from a manifest, lists of every route or component. They go stale. Keep only what Claude can't find quickly, such as which of five test commands is the right one.
- **Long examples** where one sentence would do. Keep an example when the exact format matters, such as a template Claude must copy.
- **The same rule said twice**, in one file or across files. Keep the clearest one, in the right file.
- **Notes for people, not for Claude**, such as who owns a section or when to review it. Turn them into block-level HTML comments (`<!-- ... -->` on their own lines). Claude Code strips those before it loads the file, so they cost no context.

## 6. Placement: in the wrong file, or loaded too often

- A personal preference in a committed project file affects every teammate. Move it to the user file or `CLAUDE.local.md`.
- A fact about one project in the user file loads in every project. Move it to that project's `CLAUDE.md`.
- Rules for one folder or file type load every session. Move them to a nested `CLAUDE.md` in that folder, or to `.claude/rules/<topic>.md` with `paths` frontmatter, such as `paths: ["src/api/**"]`. Claude Code loads those only when Claude works on matching files.
- Long reference material needed only sometimes, such as release steps, a runbook or API notes, loads every session for no gain. Move it to a file Claude reads on demand, such as `docs/release.md`, and leave one line in CLAUDE.md that says when to read it. Don't use an `@` import for this, because an import loads the file every session.

## 7. Format: structure and Markdown

Fix the structure, never the meaning:

- **Headings**: one topic per `##` heading, no skipped levels, no duplicate headings (merge them), no empty sections.
- **One rule per bullet.** Split rules buried in long paragraphs into bullets. Keep a short intro paragraph when it explains why the rules exist.
- **Emphasis**: current Claude models follow instructions closely, and ALL CAPS or IMPORTANT and MUST on every rule makes them apply rules too broadly. Keep strong emphasis on at most a few rules that are truly critical, and write the rest plainly.
- **Broken Markdown**: unclosed code fences, tables without a separator row, list items that lost their indent.
- **Whitespace**: trailing spaces, more than one blank line in a row.
- **Size**: Claude Code's docs target under 200 lines per CLAUDE.md file, because longer files cost more context and Claude follows them less reliably. For a longer file, say which moves under Placement would bring it under the target.
- **Order**: group related rules. A project file often reads best as overview, commands, architecture and conventions, workflow, then gotchas. A user file often reads best as how to communicate, working habits, tool rules, then personal facts. Don't reorder text that points at other parts by position, such as "the rules below", unless you fix the pointer too.
