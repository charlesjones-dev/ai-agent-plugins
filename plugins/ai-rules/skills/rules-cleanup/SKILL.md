---
name: rules-cleanup
description: "Audit the user and project CLAUDE.md files, and nothing else, for rules that restate what Claude Code already does, rules a setting or hook would enforce better, stale and conflicting rules, text that costs context for little gain, and messy structure. Reports each finding with its file, line, size and a proposed fix, then applies only the fixes the user approves, with a diff and a backup. Report-only until the user approves. Use when the user runs /rules-cleanup, or asks to clean up, trim, slim down, audit, organize or optimize their CLAUDE.md."
argument-hint: "[user|project|all] [--report]"
---

# Rules Cleanup

You audit the CLAUDE.md files that Claude Code loads, and make them shorter, clearer and better organized without losing anything the user needs. The user and project files load into every session, and nested files load when Claude works in their folder. Keep a rule only when it changes what Claude does.

Claude Code's built-in `/doctor prompt-audit` also finds outdated instructions, missing files and contradictions, across all instruction files. This skill covers CLAUDE.md alone, and adds the Built-in, Setting, Low value, Placement and Format checks, token counts, backups and safe handling of ai-rules sections. If the user asks about rules, skills, subagents or output styles, tell them to run `/doctor prompt-audit` for those.

You only read and edit CLAUDE.md files. You never change settings files, hooks, skills or code. When a setting or hook would do a rule's job better, you tell the user the exact change, and they make it.

## Instructions

### Step 1: Read the arguments

- `user`: only the user file. `project`: only the project files. `all` or nothing: both.
- `--report`: report the findings and stop. Don't offer to apply anything.

### Step 2: Find the files

Resolve the home folder with the first of `echo "$HOME"`, `$env:USERPROFILE` or `echo %USERPROFILE%` that returns a path.

| Scope | Files | Who it affects |
|-------|-------|----------------|
| user | `~/.claude/CLAUDE.md` | Every project on this machine, for this user |
| project | `./CLAUDE.md`, `./.claude/CLAUDE.md`, `./CLAUDE.local.md` | `CLAUDE.md` and `.claude/CLAUDE.md` are usually committed, so everyone who clones the repo gets them. `CLAUDE.local.md` is usually gitignored and personal |
| project, parents | `CLAUDE.md` and `CLAUDE.local.md` in each folder above the working directory, up to the home folder | Load at launch, together with the project files. Common in monorepos |
| project, AGENTS.md | `./AGENTS.md` and `./.claude/AGENTS.md` | Claude Code loads these in place of CLAUDE.md when the working directory and its parents have no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md`. Audit them only in that case. Other agents read them too, so keep their text agent-neutral |
| project, nested | `CLAUDE.md` files in subfolders, found with `git ls-files '*CLAUDE.md'` or a file search that skips `node_modules`, build output and `.git` | Load when Claude works on files in that folder |
| context only | The managed policy file: `/Library/Application Support/ClaudeCode/CLAUDE.md` on macOS, `/etc/claude-code/CLAUDE.md` on Linux, `C:\Program Files\ClaudeCode\CLAUDE.md` on Windows | The whole organization. Read it to find conflicts. Never edit it |

Also note each `@path` import in these files. An import loads the imported file at the start of every session, so count its size too. Audit an imported file only if it sits in scope (in the project, or under `~/.claude/`).

If nested files exist, ask whether to include them (multi-select, up to 4 options per question, with "All nested files" first). If no file exists in scope, say so and stop. The built-in `/memory` command also lists the files Claude Code loaded in this session.

### Step 3: Measure

For each file, record its lines, words and approximate tokens (characters ÷ 4), and when it loads. Leave block-level HTML comments (`<!-- ... -->` on their own lines, outside code blocks) out of the token count, because Claude Code strips them before it loads the file. Flag any file over 200 lines, the target in Claude Code's docs. Find the five largest sections (a `##` heading and its content) across all files, with their share of the total.

### Step 4: Audit

Read every file in full. Then read [references/checks.md](references/checks.md) and work through its checks in order. These are the kinds of finding:

| Kind | Meaning | Usual fix |
|------|---------|-----------|
| Built-in | Restates what Claude Code already does | Delete |
| Setting | A setting, permission rule or hook enforces this, and a CLAUDE.md line only asks | Make the change the user approves, then delete the line |
| Stale | Points at files, commands, tools, models or flags that don't exist any more | Fix or delete |
| Conflict | Two rules disagree, within a file or across files | The user picks one |
| Low value | Vague, a persona, history, an inventory Claude can read from the code, or a long example that adds little | Delete or condense |
| Placement | In the wrong file, or loads every session when it's needed only sometimes | Move |
| Format | Structure problems: duplicate or empty headings, emphasis everywhere, rules buried in prose, broken Markdown | Rewrite the structure, not the meaning |

Rules for judging:

- **The source of truth for Built-in is your own system prompt.** You are running under Claude Code's instructions right now. A rule is Built-in only if you can point to the instruction in your own system prompt that already says the same thing. If you can't find one, it isn't Built-in, even if the reference file lists it as a typical example.
- **An override is not redundant.** A rule that changes a default on purpose, such as "commit after each finished task" when Claude Code's default is to commit only when asked, is the user's choice. Leave it, and list it under "Kept on purpose" so the user sees you considered it.
- **Check before you call something stale.** Confirm that a path, script or command really is missing (read `package.json`, the `Makefile`, the folder) before you report it.
- **Every finding needs evidence:** the file and line, a short quote, why it qualifies, the proposed fix, and the approximate tokens saved.
- **Sections managed by ai-rules** sit between `<!-- ai-rules:begin ... -->` and `<!-- ai-rules:end ... -->` markers. Don't propose edits inside them, because an edit makes `/rules-setup` treat the section as edited. If a managed section has a finding, propose the `/rules-setup` change instead, such as turning off a module or removing the section, and tell the user to run `/rules-setup` themselves. You may move a whole managed block, markers included, without changing it.
- Keep the user's voice. A Format fix changes structure. It never changes what a rule means.

### Step 5: Report

Write the report in chat:

1. **Files**: a table with each file, its lines, words, approximate tokens, and when it loads. Add a total row.
2. **Largest sections**: the five largest, with their share of the total.
3. **Findings**: a numbered list (`#1`, `#2`, ...), grouped by kind in the order of the table above. Each finding has its file and line, a quote of at most one line, why, the proposed fix and the tokens saved. For a Setting finding, show the exact JSON or hook, and the settings file it goes in.
4. **Kept on purpose**: overrides of defaults you checked and left alone, one line each.
5. **After cleanup**: the approximate tokens before and after, if the user applies every proposed fix.

If there are no findings, say the files are already lean, give the measurements, and stop.

With `--report`, stop here.

### Step 6: Choose what to apply

Ask:

- Question: "Which fixes should I apply?"
  - Header: "Apply"
  - Options:
    - "All proposed fixes (recommended)"
    - "Pick by kind": multi-select questions of the kinds that have findings, at most 4 options per question
    - "Pick one by one": multi-select questions of the findings, at most 4 options per question and 4 questions per call, labeled `#<n> <short summary>`
    - "None": stop with no changes

Then settle what each chosen fix needs:

- **Conflict:** ask which rule wins for each conflict, with both quotes. A conflict with the managed policy file always keeps the policy rule.
- **Setting:** show the change again and ask "Did you make this change?" ("Yes, delete the rule" / "Not yet, keep the rule"). Delete the rule only on yes.
- **Placement into a committed project file, or out of one:** warn that the project file is shared with everyone who clones the repo.
- **Placement into an on-demand file:** propose the target path, and leave a one-line pointer in CLAUDE.md that says when to read the file. Don't use an `@` import for this, because an import loads the file every session.

### Step 7: Preview and write

1. For each file you will change, write the proposed content to a scratch folder (your scratchpad directory, or a temporary folder), never next to the file.
2. Show `git diff --no-index -- "<file>" "<scratch copy>"` for each file. Without git, show the changes as plain text.
3. Ask "Write these changes?" with "Yes, write them" and "Cancel".
4. On yes, back up each file first to `<home>/.claude/backups/ai-rules/<name>-cleanup-<YYYYMMDD-HHMMSS>.md`, where `<name>` is `user-CLAUDE` for the user file and `<project folder>-<file name>` for a project file. Create the folder if needed.
5. Write the files, and create any new on-demand files the user approved.
6. Check the result:
   - The text inside every ai-rules managed block is exactly as it was, unless the user moved the whole block.
   - Every heading and fenced code block is still closed.
   - Measure the files again.
7. Report the backup paths, the fixes applied, and the tokens before and after. If a project file changed, remind the user to review and commit it themselves. Say that the changes apply to new sessions, and that the current session still has the old text loaded.

## Rules

- Never write a file without showing the diff and getting a yes.
- Never edit settings files, hooks, skills, the managed policy file, or text inside ai-rules markers.
- Never delete a rule because it looks unusual. Delete it only when a check in the reference file applies, and the finding names the evidence.
- Never commit or push.
