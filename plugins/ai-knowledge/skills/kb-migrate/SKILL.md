---
name: kb-migrate
description: "Move a 1.x knowledge base (the CLAUDE.md Knowledge Base table and docs/kb/) to Claude Code rules: pinned articles load every session, scoped ones when Claude touches matching files, and the rest through a short index. Shows the plan and asks first, supports --dry-run, is safe to re-run, turns on auto-capture, which replaces /kb-auto, unless you pass auto=off, and adds a short AGENTS.md section so Codex and Cursor read the knowledge base (agents=off to skip). It also finds references to renamed or removed marketplace commands in the knowledge base, CLAUDE.md, AGENTS.md, .gitignore and docs/, and proposes fixes. On a 2.x knowledge base it checks and repairs the format and runs the same command check, so running it again after a marketplace update catches newly stale references."
argument-hint: "[--dry-run] [auto=off] [agents=off]"
disable-model-invocation: true
---

# Migrate the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the target layout, the frontmatter and the checks used below. The command check (see Command references, at the end) also uses [command-map.md](command-map.md).

Arguments (may be empty): $ARGUMENTS

`--dry-run` means: build and show the plan, change nothing, and don't ask to proceed. `auto=off` means: don't turn on auto-capture at the end (Step 7). `agents=off` means: leave the `AGENTS.md` section out (kb-format.md, The AGENTS.md pointer). Ignore any other text.

This command moves files and edits CLAUDE.md. Nothing changes until the user approves the plan.

## Step 1: Take stock

1. **Git state.** Check whether the project is a git repository. If it is, run `git status --porcelain -- CLAUDE.md .claude/CLAUDE.md docs/kb .claude/rules/kb .claude/kb`. If anything there is uncommitted, the plan warns that the migration is easiest to review and undo as one commit on a clean tree, and the approval question in Step 4 mentions it.
2. **Git ignore.** Run the git check from kb-format.md.
3. **1.x pieces.** Collect:
   - The `Knowledge Base` section of `CLAUDE.md` or `.claude/CLAUDE.md`, from its heading to the next heading of the same or higher level. Inside it: the preamble, the table (Topic, File, When to Load), an inline `### Global Learnings` subsection (layouts before 1.3), the kb-auto block (`<!-- kb-auto: enabled -->` and the blockquote after it), and anything else the user wrote there. Also search the whole file for a kb-auto block outside the section.
   - Every file under `docs/kb/`, recursively, including non-markdown files such as images.
4. **2.x pieces.** List what already exists under `.claude/rules/kb/` and `.claude/kb/`, from `/kb-init` or an earlier, interrupted run.
5. If there are no 1.x pieces, go to Step 9.

## Step 2: Read every row and article

Parse each table row:

- **Topic** and **File**.
- **When to Load**:
  - `Always (pinned)` means pinned.
  - Backtick-wrapped globs before the dash (`—`) are scope patterns.
  - Comma-separated words after the dash are keywords.
  - Free text from older versions ("When working in packages/api/"): infer globs from directory or file references (`packages/api/**`) and keywords from the rest, and mark the row "inferred" so the user checks it.

Read every `.md` file under `docs/kb/` and every file a row points to. For each article, record:

- its frontmatter: `tags`, `related`, `created`, `last-updated`, `pinned`, `scope` (a string or a list), `source`, `discovered-from`, `type`, `query`, `sources`, and any other field;
- its title (the first `#` heading) and its length in lines;
- its links: the targets in `related` and `sources`, and every `[[name]]` link in the body, each resolved to the article whose file name is `name.md`;
- problems: no frontmatter; missing `tags`, `created` or `last-updated`; YAML that won't parse (often a 1.x `related` line, which goes away anyway); `@path` text outside backticks that names a real file.

Map the special files:

| 1.x | 2.x |
|---|---|
| `docs/kb/_global-learnings.md` | `.claude/rules/kb/_global-learnings.md` (pinned) |
| Inline `### Global Learnings` in CLAUDE.md | Merged into `.claude/rules/kb/_global-learnings.md`, without duplicates |
| `docs/kb/_index.md` | Not moved. Its summaries seed the new `_index.md`, then it's deleted. |
| `docs/kb/_log.md` | `.claude/kb/_log.md` |
| `docs/kb/README.md` | `.claude/kb/README.md`, rewritten from the template in kb-format.md |
| Non-markdown files (images, PDFs) | `.claude/kb/assets/`, keeping their subpath; relative links to them in moved articles are updated |
| `docs/kb/.obsidian/` and other editor or system files (`.DS_Store`) | Not knowledge. Deleted with `docs/kb/`, and listed in the plan so the user approves it |

Edge cases:

- A row whose file doesn't exist is stale. Drop it and list it in the plan.
- A row that points outside `docs/kb/` (1.x `/kb-import` allowed any path): plan to move the file into the knowledge base like the others, and in Step 4 let the user keep it where it is instead, which drops it from the knowledge base.
- An article in `docs/kb/` without a row is migrated from its frontmatter like any other.
- A `[[name]]` link that matches no article, or more than one, can't be turned into a path. List it under "Needs your call".
- If the Knowledge Base section holds text that isn't part of the 1.x machinery (notes the user wrote under the heading), list it in the plan and ask whether to keep it in CLAUDE.md or turn it into an article.

## Step 3: Decide each article's load mode

Apply the first rule that matches:

1. **Pinned**: the row says `Always (pinned)`, the frontmatter has `pinned: true`, or it's `_global-learnings.md`. It goes to `.claude/rules/kb/{same subpath}` without `paths`.
2. **Scoped**: it has scope patterns, from the frontmatter `scope`, the row, or both (merged, without duplicates). It goes to `.claude/rules/kb/{same subpath}` with `paths`.
3. **On-demand**: everything else. It goes to `.claude/kb/{same subpath}`.

Every article keeps its row's keywords: they're added to its `tags`, whatever its mode. Scoped and on-demand articles get a line in `_index.md` with those keywords, so a scoped article still loads when a task matches its topic and no file matches its globs, as the 1.x row allowed.

Keep each article's subfolder (`docs/kb/conventions/api.md` becomes `.claude/rules/kb/conventions/api.md` or `.claude/kb/conventions/api.md`). Don't reorganize during the migration; `/kb-prune organize` does that afterward.

Turn scope patterns into `paths`:

- A pattern without `/`, such as `*.controller.ts`, becomes `**/*.controller.ts`.
- A directory, such as `src/api` or `src/api/`, becomes `src/api/**`.
- Backslashes become forward slashes, and a leading `./` is dropped.
- Absolute paths and paths outside the project are dropped and flagged.
- A pattern that points at the 1.x knowledge base (`docs/kb/**` or anything under `docs/kb/`) is dropped and flagged, not rewritten to `.claude/rules/kb/**` or `.claude/kb/**`. In 2.x it would load the article whenever Claude reads any article (kb-format.md). If no patterns are left, offer to make the article on-demand.
- Check every pattern with Glob. If none of an article's patterns matches a file, flag it, because as a scoped rule it would never load. Offer to fix the patterns or make the article on-demand.

Check the budget in kb-format.md (Layout). If the pinned articles total more than about 100 lines or there are more than five, say so and suggest which ones to make scoped (if their content is about specific folders) or on-demand. If the new `_index.md` would pass about 150 lines, suggest articles to merge with `/kb-prune` afterward. The 1.x `_index.md` catalog is replaced, not carried over.

Then look for stale command references, as Command references (at the end) describes.

## Step 4: Show the plan

```text
KB migration plan
=================

Pinned (load every session): {n} articles, {lines} lines
  docs/kb/_global-learnings.md → .claude/rules/kb/_global-learnings.md
  docs/kb/security/auth.md → .claude/rules/kb/security/auth.md

Scoped (load when Claude reads or edits matching files, or a task matches the index line): {n} articles
  docs/kb/conventions/api.md → .claude/rules/kb/conventions/api.md
    paths: src/api/**, **/*.controller.ts   (was *.controller.ts)
    index line: API error format (api, rest; loads with src/api/**, **/*.controller.ts)

On-demand (listed in .claude/rules/kb/_index.md): {n} articles
  docs/kb/tools/deploy.md → .claude/kb/tools/deploy.md
    index line: release steps and rollback rules (deploy, release, rollback)

Other files
  docs/kb/_log.md → .claude/kb/_log.md
  docs/kb/_index.md → deleted (replaced by .claude/rules/kb/_index.md)
  docs/kb/README.md → .claude/kb/README.md (rewritten)
  docs/kb/.obsidian/ → deleted with docs/kb/ (editor settings, not knowledge)

Frontmatter and links
  conventions/api.md: scope → paths, pinned removed, tags + rest (row keyword),
    related removed; Related section: .claude/rules/kb/security/auth.md, .claude/kb/tools/deploy.md

CLAUDE.md
  Remove "## Knowledge Base" (lines {a}-{b}): preamble, table ({n} rows), kb-auto block
  Stale rows dropped: "{Topic}" → {path} (file missing)

AGENTS.md
  Add the ai-knowledge section so Codex and Cursor read the knowledge base {or: skipped, agents=off}

Command references (inside the knowledge base: applied with the migration; outside it: asked after)
  rename
    docs/kb/_global-learnings.md:12  `/ai-writing:writing-humanize` → `/ai-slop:slop-rewrite`
    CLAUDE.md:9 (outside)  `ai-geo@claude-code-plugins-dev` → `ai-seo@ai-agent-plugins`
  changed
    docs/kb/_global-learnings.md:14 → see Needs your call
    .gitignore:4 (outside)  keep docs/geo-audit/ and add docs/seo-audit/ on the next line
  removed
    CLAUDE.md:22 (outside) → see Needs your call
  left as history
    docs/kb/tools/seo.md:8  "On 2026-05-01 we ran /geo-audit" (dated)

Needs your call
  {inferred rows, globs that match nothing, budget, links that match no article, extra text in the section}
  docs/kb/_global-learnings.md:14 (changed)
    now:      Commit with `/ai-git:git-commit-push` once tests pass.
    proposed: Commit with `/ai-git:git-commit-push-pr --no-pr` once tests pass.
  CLAUDE.md:22 (removed)
    now:      Load an article with /kb-load when Claude misses it.
    proposed: To pull in an article Claude missed, @-mention its file, such as @.claude/kb/tools/release.md.
  docs/kb/tools/seo.md:3 (ambiguous: history or instruction?)
    now:      We moved to /geo-audit after the March review.

Warnings
  {uncommitted changes, ignored paths}

Moves use git mv, so history follows each file. Nothing has changed yet.
```

With `--dry-run`, end with "Dry run: nothing changed. Run `/kb-migrate` to apply this plan." and stop.

Otherwise ask with AskUserQuestion:

- Header: "KB Migrate"
- Question: "Apply this migration?" (add "There are uncommitted changes in these paths." when Step 1 found some)
- Options: "Migrate" | "Let me adjust" | "Cancel". When "Needs your call" proposes rewrites of `changed` or `removed` command references inside the knowledge base, replace "Migrate" with two options: "Migrate, with the proposed rewrites" | "Migrate, leave those references for me"

With "Let me adjust", take free-text changes (a different mode, other paths or keywords, a new name, an article to leave out of the knowledge base, a different rewrite or a reference to leave alone), show the updated plan, and ask again. An article left out moves to `docs/` (or a path the user names), so `docs/kb/` ends up empty. With "Cancel", stop without changes.

## Step 5: Migrate

Get today's date once (kb-format.md, Dates). Use it for the log and `_index.md` only: the knowledge in the articles hasn't changed, so their `last-updated` stays as it is.

Run no git commands that change state other than `git mv` and `git rm`: don't `git add`, commit or stash. The user reviews and commits the result.

1. **Folders.** Create every destination folder.
2. **Moves.** Move each file as kb-format.md describes (`git mv` for tracked files). If the destination already exists from an earlier run: when the content is the same, delete the 1.x copy; when it differs, show both and ask which to keep, or merge them.
3. **Frontmatter.** In each moved article:
   - scoped: write `paths` first, as a list of the quoted patterns from Step 3;
   - remove `scope`, `pinned`, `related` and `sources`;
   - add any missing field: infer `tags` from the content and path; take `created` from `git log --diff-filter=A --follow --format=%as -- {path} | tail -1` and `last-updated` from `git log -1 --format=%as -- {path}`, or today's date when git has no history for the file;
   - add each of the row's keywords that `tags` lacks (lowercase), for every article, pinned and scoped included. Index lines read keywords from `tags`, so a keyword left out here is lost;
   - keep every other field and value as it was.
4. **Command references.** In each moved article, apply the `rename` hits from the plan, and the proposed `changed` and `removed` rewrites if the user chose them. Change nothing else, and don't touch files outside the knowledge base yet (Step 8 asks about them).
5. **Links.** In each moved article, turn the targets of the removed `related` and `sources` fields into repo-relative paths at their new locations, in backticks, listed in a `## Related` section at the end of the body (kb-format.md, Related articles). Merge them with an existing Related section, replacing its `[[name]]` entries, and drop duplicates. A `[[name]]` link in running text becomes the target's path in backticks. Leave links listed under "Needs your call" as plain text without brackets, and report them.
   - put `@path` text that names a real file in backticks.
6. **Global learnings.** Merge an inline `### Global Learnings` subsection into `.claude/rules/kb/_global-learnings.md`, creating it if needed (frontmatter `tags: [global, cross-cutting]`, `created`, `last-updated`; heading `# Global learnings`; rules under `## Key rules`). Drop duplicates and placeholder text such as "_No global learnings captured yet..._".
7. **Assets.** Move non-markdown files and fix relative links to them in the moved articles.
8. **Index.** Write `.claude/rules/kb/_index.md` from the template in kb-format.md, with a line for each scoped and on-demand article. Take summaries from the old `_index.md` where it has them, otherwise from the article's title and opening sentence. Then delete `docs/kb/_index.md` (`git rm` if tracked).
9. **README.** Write `.claude/kb/README.md` from the template in kb-format.md. If a 1.x README existed, move it there first and then replace its content, so its history carries over.
10. **CLAUDE.md.** Remove the Knowledge Base section (heading, preamble, table, inline global learnings, kb-auto block) and any kb-auto block elsewhere. Keep the text the user chose to keep in Step 4. Leave everything else as it was, and collapse any run of three or more blank lines left behind into one blank line. Don't add a pointer: `_index.md` tells Claude about the knowledge base.
11. **`AGENTS.md`.** Add the pointer section from kb-format.md, creating the file if needed, unless the arguments include `agents=off`. Change nothing outside its marker comments.
12. **`docs/kb/`.** Delete what's left in it that the plan listed, such as `.obsidian/` and `.DS_Store` (`git rm -r` for tracked files, a plain delete for the rest), then the folder itself. Leave `docs/` alone, and don't recreate it if it ends up empty: git doesn't keep empty folders.
13. **Log.** Append to `.claude/kb/_log.md`:

    ```markdown
    ## [{date}] migrate | Moved the 1.x knowledge base to Claude Code rules
    - Pinned: {n}, scoped: {n}, on-demand: {n}
    - Removed the Knowledge Base section{ and the kb-auto block} from CLAUDE.md
    - {Added the AGENTS.md pointer | Skipped the AGENTS.md pointer (agents=off)}
    - Frontmatter fixes: {n}; links turned into paths: {n}; command references updated: {n}
    ```

## Step 6: Verify

- Run `git status --short` and confirm the moves show as renames.
- Re-read every new file. Each article has one frontmatter block of valid YAML with quoted globs; only scoped articles have `paths`; no article has `scope`, `pinned`, `related` or `sources`; no `[[` is left in any article; every Related entry is a path that exists; nothing under `.claude/rules/kb/` is a README, log or note.
- Every scoped and on-demand article has a line in `_index.md` with its `tags` as keywords, and every line points at a file that exists.
- `docs/kb/` is gone, and CLAUDE.md has no Knowledge Base table or kb-auto marker, so the 1.x check now passes.

Fix anything that fails before reporting.

## Step 7: Auto-capture

After a real run, turn on auto-capture for this developer without asking, unless the arguments include `auto=off`, in which case set it off (kb-format.md, Auto-capture). A dry run changes nothing; its plan says whether auto-capture would be turned on or left off.

## Step 8: Report

- How many articles are pinned, scoped and on-demand, with the pinned line total.
- Every move, frontmatter fix and pattern change, the lines removed from CLAUDE.md, and anything left for the user to decide.
- The `AGENTS.md` section: added, so Codex, Cursor and other agents that read `AGENTS.md` use the knowledge base, or skipped with `agents=off`.
- Auto-capture: on or off for this developer, and where the setting is stored. If a kb-auto block was removed, add: "`/kb-auto` is gone. Auto-capture replaces it: Claude saves team knowledge as it comes up, without being asked. It's now on for you; turn it off any time with `/kb-init auto=off`, or back on with `/kb-init auto=on`. Claude Code's auto memory is a separate option that keeps personal notes on one machine, and auto-capture works whether it's on or off."
- Files outside the knowledge base: search the repo (skipping `.git/`, dependency folders and the knowledge base itself) for files that still mention `docs/kb/`, and add the command references the plan found outside the knowledge base. If there are any, list each file with its proposed changes and ask one question (Header: "Other files"; Question: "Update these files outside the knowledge base as proposed?"; Options: "Update all" | "Let me pick" | "Leave them"). Apply only what the user approves. In `.gitignore`, add the new line after the old one and keep the old one. If you can't ask, end the report with the list and the question.
- How to check it worked: start a new session and run `/context` to see `_index.md` and the pinned articles among the loaded rules. Then ask Claude to read a file that matches a scoped article; the article loads with it.
- Next: review the diff and commit it as one change (for example `git add -A docs/kb .claude CLAUDE.md AGENTS.md`). Don't commit for the user. Once it's committed, Claude Code loads the knowledge base for every teammate, with or without the plugin; teammates who use the `/kb-*` commands should update ai-knowledge to 2.x.

## Step 9: Check a 2.x knowledge base

With no 1.x pieces left, check the 2.x format instead. This is also how to repair a knowledge base edited by hand or moved by an older version of this skill.

If `.claude/rules/kb/_index.md` doesn't exist and there's no other `.md` file under `.claude/rules/kb/` or `.claude/kb/`, say "There's no knowledge base to migrate. Run `/kb-init` to start one." and stop.

Check:

- files under `.claude/rules/kb/` that aren't articles, such as a README, a log or notes (they'd load every session): move them to `.claude/kb/`;
- 1.x fields: `scope` becomes `paths`; an article in `.claude/kb/` with `pinned: true` moves to `.claude/rules/kb/`; an article in `.claude/rules/kb/` without `paths` that has `pinned: false` is probably pinned by mistake, so ask whether to scope it, make it on-demand, or pin it;
- frontmatter: missing required fields and YAML that won't parse;
- 1.x links: `related` or `sources` fields and `[[name]]` links anywhere in an article. Convert them as Step 5 does (paths in a Related section);
- `paths` that match the knowledge base's own folders (`.claude/rules/kb/**`, `.claude/kb/**`): propose dropping them, and making the article on-demand if no patterns are left, because the article would load with every knowledge base read;
- Related entries that point at files that don't exist;
- `paths`: patterns in a form Step 3 would rewrite, and patterns that match no file;
- the pinned articles and `_index.md` against the budget in kb-format.md;
- `_index.md`: scoped or on-demand articles without a line, lines pointing at missing files or at pinned articles, lines whose keywords or "loads with" globs don't match the article's `tags` and `paths`, and a header that differs from the template in kb-format.md;
- `@path` imports in articles;
- the `AGENTS.md` pointer: missing, or different from the template in kb-format.md (with `agents=off`, a section that should be removed);
- stale command references, found as Command references describes, across the whole knowledge base and the other files it lists. This is how a migrated project catches commands that a later marketplace release renamed or removed.

Show the findings in the format of Step 4, including its Command references section. With `--dry-run`, stop there. Otherwise ask (Header: "KB Format Check"; Options: "Fix all" | "Let me pick" | "Cancel"; when there are proposed `changed` or `removed` rewrites inside the knowledge base, replace "Fix all" with "Fix all, with the proposed rewrites" | "Fix all, leave those references for me"). Apply what was approved the way Step 5 does, then ask about files outside the knowledge base the way Step 8 does. Append a `migrate | Format check` entry to the log, and report what changed. If nothing needs fixing, say "The knowledge base already matches the 2.x format."

## Command references

Notes written for an older version of this marketplace can send Claude to commands that no longer exist. [command-map.md](command-map.md) lists every command, skill, subagent, plugin, marketplace name and report path that was renamed, merged or removed, with its replacement and how to match it. Read it before scanning.

**Where to look:**

- the knowledge base: every article being migrated (1.x), or every article under `.claude/rules/kb/` and `.claude/kb/` (Step 9);
- `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` and `AGENTS.md`;
- `.claude/rules/**/*.md` outside `.claude/rules/kb/`;
- `.gitignore`;
- `docs/**/*.md` outside `docs/kb/`.

Skip history: `_log.md`, changelogs and release notes (`CHANGELOG*`, `HISTORY*`, `RELEASES*`, files named for a release or date), and dependency or build folders. Also skip text the migration removes anyway, such as the CLAUDE.md Knowledge Base section and the kb-auto block.

**How:** for each row, search for every form the map's matching rules list, and read the whole sentence around each hit. Then sort the hit:

- **History**: a statement about what happened on a past date, a log line, quoted output, or a sentence about the rename itself. Leave it, and list it under "left as history" only when the plan should explain why it wasn't changed.
- **Ambiguous**: you can't tell whether it's history or an instruction, or whether a bare name means the marketplace command. List it under "Needs your call" without a rewrite. Don't change it.
- **`rename`**: swap the old text for the new, in the same form (`/x`, `/plugin:x`, `$plugin:x` or the bare name), keeping New's arguments.
- **`changed`** and **`removed`**: in the same form as the old text, propose a rewrite of the whole sentence, so it still reads correctly with the new command and its arguments, or with the built-in alternative. If nothing replaces an instruction, propose removing it. These go under "Needs your call". In CLAUDE.md, AGENTS.md and rule files, put any `@path` example in backticks: a bare `@path` there is an import that loads the file at every session start.
- **`.gitignore`**: for a report folder that moved, propose adding the new folder on the line after the old one and keeping the old one, since old reports may still be there. Never remove the old line.

**Applying:** inside the knowledge base, `rename` hits are part of the approved migration or format check, and `changed` and `removed` rewrites apply only when the user chose them. Files outside the knowledge base change only after the separate question in Step 8.
