---
name: kb-init
description: "Set up a team knowledge base as Claude Code rules: .claude/rules/kb/ for articles Claude Code loads by itself and .claude/kb/ for on-demand articles. Turns auto-capture on for you unless you pass auto=off. On an existing knowledge base it doesn't redo setup: it turns auto-capture on if you never set it, keeps your earlier choice otherwise, and auto=on|off switches it. Also adds a short section to AGENTS.md so Codex and Cursor read the knowledge base (agents=off to skip). Points to /kb-migrate when the project has a 1.x knowledge base."
argument-hint: "[auto=on|off] [agents=off]"
disable-model-invocation: true
---

# Set up the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the layout, the files, the checks and the auto-capture setting used below.

Arguments (may be empty): $ARGUMENTS

Auto-capture is on by default: `/kb-init` turns it on for this developer in this project without asking. `auto=off` keeps it off, and `auto=on` turns it back on after an earlier `auto=off`. `agents=off` leaves the `AGENTS.md` section out (kb-format.md, The AGENTS.md pointer). Ignore any other text.

## Step 1: Check the project

1. Look for a 1.x knowledge base as kb-format.md describes. If there is one, create nothing, change no setting, and say:

   > This project has a 1.x knowledge base (the CLAUDE.md table and `docs/kb/`). Run `/kb-migrate` to move it to the new layout, or `/kb-migrate --dry-run` to preview the plan first. Setting up the new layout next to the old one would split the knowledge base in two. At the end of the migration, `/kb-migrate` turns on auto-capture for you unless you pass `auto=off`.

   Then stop.
2. If `.claude/rules/kb/_index.md` exists, the knowledge base is already set up: go to Step 4.
3. Note any other `.md` files already under `.claude/rules/kb/` or `.claude/kb/`, and run the git check from kb-format.md.

## Step 2: Create the files

Get today's date once (kb-format.md, Dates). Create only files that don't exist, and never overwrite one.

1. **`.claude/rules/kb/_index.md`** from the template in kb-format.md, with `- None yet.` as the list. If articles already exist (added by hand, for example), list every scoped article under `.claude/rules/kb/` and every on-demand article under `.claude/kb/` instead, one line each from the article's title, `tags` and `paths`.
2. **`.claude/kb/README.md`** from the template in kb-format.md.
3. **`.claude/kb/_log.md`** as kb-format.md describes, with this entry:

   ```markdown
   ## [{date}] init | Knowledge base set up
   - Created: {the files created in this run}
   ```

4. **`AGENTS.md`**: add the pointer section from kb-format.md, creating the file if needed, unless the arguments include `agents=off`. This is the one file outside `.claude/` that `/kb-init` writes, and only between its marker comments.

Don't create `_global-learnings.md` yet. `/kb-learn` and `/kb-add` create it with the first cross-cutting rule, so an empty placeholder doesn't load into every session.

Don't add anything to CLAUDE.md. Claude Code loads `_index.md` and the scoped articles without being told to.

## Step 3: Auto-capture on a new knowledge base

Don't ask. With `auto=off`, set it off; otherwise set it on (kb-format.md, Auto-capture). Off still writes the `false` setting in a git repository, so a later `/kb-init` keeps that choice and reports it clearly. Go to Step 5.

## Step 4: An existing knowledge base

Don't redo the setup. Only create `.claude/kb/README.md` or `.claude/kb/_log.md` if one is missing, as Step 2 describes.

Bring the `AGENTS.md` pointer up to date (kb-format.md, The AGENTS.md pointer): add it if it's missing, replace it if it differs from the template, and remove it with `agents=off`.

Read the current auto-capture state and where it comes from (kb-format.md, Auto-capture). Don't ask:

- With `auto=on` or `auto=off`, apply it.
- With neither, and no setting yet (this developer never ran `/kb-init` or `/kb-migrate` here, as when a teammate clones a project that already has a knowledge base), turn it on.
- With neither, and a setting already there, keep it. The report says how to switch.

If the `AI_KNOWLEDGE_AUTO_CAPTURE` environment variable decides the state, say that changing the project setting won't take effect until the variable is removed, and say where it's probably set (the shell, or the `env` block of a settings file).

## Step 5: Report

Show:

- which files were created and which already existed (on an existing knowledge base, say it's already set up);
- any git-ignore warning from Step 1;
- the `AGENTS.md` section: added, updated, already current, or removed, and that it lets Codex, Cursor and other agents that read `AGENTS.md` use the knowledge base (`/kb-init agents=off` removes it);
- auto-capture: on or off for this developer, where the setting is stored, and that it starts with the next session or `/clear`. If it was just turned on, follow auto-capture for the rest of this session too, as kb-format.md says. If it's off, mention `/kb-init auto=on`; if it's on, mention `/kb-init auto=off`;
- for a new knowledge base, how loading works, in three lines: pinned articles load every session; scoped ones load when Claude touches matching files, or when a task matches their line in `_index.md`; on-demand ones only from the index. Claude names each scoped or on-demand article it loads in a one-line notice;
- that Claude Code's auto memory, when it's on, keeps personal notes on each machine, while this knowledge base holds what the team shares through git;
- next steps, for a new knowledge base:
  - `/kb-add <note, path or URL>` adds knowledge; `/kb-add --absorb` reviews CLAUDE.md and `docs/` for content that belongs here
  - `/kb-learn` reviews the conversation and saves what it taught
  - `/kb-discover [paths]` writes down conventions found in the code
  - `/kb-query <question>` answers from the knowledge base, and `/kb-query list` shows what's in it
  - `/kb-prune` cleans it up
- a reminder to commit `.claude/rules/kb/`, `.claude/kb/` and `AGENTS.md`.
