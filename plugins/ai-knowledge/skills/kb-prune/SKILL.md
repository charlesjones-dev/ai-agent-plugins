---
name: kb-prune
description: "Clean up the team knowledge base: find duplicates, contradictions, broken links, stale articles, scoped globs that match nothing and pinned articles that cost too much context, then merge, fix or remove with your approval. Also removes a single article, or sorts articles into category folders."
argument-hint: "[remove <article> | organize]"
disable-model-invocation: true
---

# Prune the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the layout, frontmatter, load modes and file-move rules used below.

Arguments (may be empty): $ARGUMENTS

| Arguments | Mode |
|---|---|
| None | **Audit**: review the whole knowledge base |
| `remove {article}` | **Remove** one article (a file name, path or topic) |
| `remove` | **Remove**, choosing the article from a list |
| `organize` | **Organize** articles into category folders |

Every change needs the user's approval.

## Step 1: Check the knowledge base

Run the checks from kb-format.md: stop if there's a 1.x knowledge base (point to `/kb-migrate`) or no knowledge base (point to `/kb-init`). Then read every article under `.claude/rules/kb/` and `.claude/kb/` with its frontmatter, plus `_index.md`.

## Audit mode

### Find issues

1. **Index**: scoped or on-demand articles with no line in `_index.md`; lines pointing at files that don't exist, or at pinned articles; lines whose summary, keywords or "loads with" globs no longer match the article.
2. **Load modes**:
   - Scoped articles whose `paths` match no file (check each pattern with Glob). They never load.
   - Pinned articles and `_index.md` against the budget in kb-format.md (Layout). Flag pinned articles over about 100 lines in total or more than five of them, and suggest which to scope or make on-demand. Flag an index over about 150 lines, and suggest merges.
   - Pinned or on-demand articles whose rules are clearly about certain folders or file types: suggest `paths` so they load only there.
   - Files under `.claude/rules/kb/` that aren't articles (a README, log or notes). They load every session.
3. **Frontmatter**: no frontmatter; YAML that won't parse; missing `tags`, `created` or `last-updated`; 1.x fields (`scope`, `pinned`, `related`, `sources`) or `[[name]]` links, which `/kb-migrate` fixes. Flag articles whose `last-updated` is more than 90 days old as **review suggested**: stable knowledge is fine, but worth a quick check.
4. **Duplicates and merges**: articles that overlap heavily, and articles on closely related topics that would read better as one (`api-auth.md` and `api-tokens.md`). Shared tags are a good hint. Merging scoped articles combines their `paths`.
5. **Contradictions**: rules in different articles, or between an article and the global learnings, that conflict.
6. **Related**: entries that point at files that don't exist (**broken**), usually because an article moved or was deleted.
7. **Global learnings** (`_global-learnings.md`): entries that are **outdated** (check whether the files or patterns they mention still exist), **duplicated** in another article, or **area-specific**, which should move to a scoped article so they stop loading every session.
8. **Organization**: if five or more articles sit loose at the root of `.claude/rules/kb/` or `.claude/kb/`, suggest category folders (see Organize mode).

### Report

```text
Knowledge base audit
====================

Index ({n})
- tools/release.md is on-demand but missing from _index.md

Load modes ({n})
- testing/e2e.md: paths match no files (e2e/**; the folder is now tests/e2e/)
- Pinned: 4 articles, 210 lines. Suggest scoping security/auth.md to src/auth/**
- .claude/rules/kb/notes.md isn't an article and loads every session

Frontmatter ({n})
- conventions/naming.md: missing created
- tools/ci.md: last updated 140 days ago (review suggested; may still be right)

Merge candidates ({n})
- api-auth.md + api-tokens.md → api-auth.md (shared tags: api, auth)

Contradictions ({n})
- api-conventions.md: "Return 404 for missing records" vs api-errors.md: "Return 410"

Related ({n})
- tools/release.md → .claude/kb/tools/deploy.md doesn't exist (broken; moved to .claude/kb/ops/deploy.md?)

Global learnings ({n})
- "Use the query builder in src/db/" is area-specific: move to a scoped article for src/db/**

Summary: {n} healthy articles, {n} issues
```

With no issues: "The knowledge base is clean: {n} articles, {n} global learnings, no issues found."

### Approve

Ask (Header: "KB Cleanup Plan"; Question: "Here's what I recommend. How do you want to proceed?"; Options: "Apply all" | "Let me review each one" | "Cancel"). When reviewing, ask about each action:

- index line: "Add, fix or remove the line for {article}?"
- globs that match nothing: "Fix the paths to {suggestion}, make it on-demand, or leave it?"
- pinned budget or an area-specific pinned article: "Scope {article} to {globs}, make it on-demand, or keep it pinned?"
- non-article file in `.claude/rules/kb/`: "Move {file} to `.claude/kb/`, or delete it?"
- frontmatter: "Add or fix frontmatter for {article}?" (show it)
- merge: "Merge {a} and {b} into {target}?"
- contradiction: "Which is right: '{rule a}' or '{rule b}'?"
- broken Related entry: "Point it at {new path}, or remove it?"
- duplicate: "Keep it in {article} and remove it from the global learnings?"
- global learning: "Move '{rule}' to {article}?"

### Apply

Get today's date once (kb-format.md, Dates). Apply only what was approved:

1. **Index**: add, fix or remove lines.
2. **Load modes**: move articles between the trees and set or remove `paths` (kb-format.md, Moving and deleting files). Moving doesn't change `last-updated`; new or changed `paths` do.
3. **Frontmatter**: add missing fields and fix the YAML. Leave 1.x fields for `/kb-migrate` and mention it.
4. **Merges**: combine the content into the target, merge `tags`, `paths`, `source` and the Related sections, delete the merged-away file, point other articles' Related entries at the target, and update `_index.md`.
5. **Contradictions**: correct the wrong rule.
6. **Related**: repoint or remove broken entries.
7. **Duplicates and global learnings**: remove or move entries as approved. Create the target article if needed.

Update `last-updated` on every article whose content changed, and on no other. Remove empty sections and folders left behind.

Append to the log:

```markdown
## [{date}] prune | Cleanup
- Index fixes: {n}; load-mode changes: {n}; frontmatter fixes: {n}
- Merges: {n}; contradictions resolved: {n}; link fixes: {n}
- Deleted: {paths}
```

Report the files created, updated, moved and deleted, and the final count of articles by load mode with the pinned line total.

## Remove mode

1. **Find the article.** Match the argument against file names (with or without `.md`), paths and titles. With several matches, or no argument, list the articles with their load modes and ask which one (Header: "KB Remove"). If nothing matches, say so and suggest `/kb-query list`.
2. **Confirm.** Show the file, its load mode, its `_index.md` line if any, and every article whose Related section points at it. Ask (Header: "Confirm Removal"; Options: "Delete it" | "Move it out of the knowledge base" | "Cancel"). Moving out keeps the file but stops it loading: ask where (default `docs/{name}.md`).
3. **Remove.** Delete it (`git rm` if tracked) or move it (`git mv`). Remove its `_index.md` line. Remove its entry from other articles' Related sections, dropping a section that ends up empty, and update `last-updated` on the articles that changed (with today's date, from kb-format.md).
4. **Log**: append `## [{date}] prune | Removed {name}` with whether the file was deleted or moved, and which articles had links cleaned.
5. **Report** what was removed and which links were cleaned.

## Organize mode

1. Find articles loose at the root of `.claude/rules/kb/` or `.claude/kb/`. `_index.md`, `_global-learnings.md`, `_log.md` and `README.md` stay where they are. With fewer than three loose articles, say there's too little to organize yet and stop.
2. For each loose article, read its tags and content and suggest a category folder, reusing existing folders first:

   | Folder | For |
   |---|---|
   | `architecture/` | system design, patterns, data flow, module boundaries |
   | `conventions/` | naming, style, API contracts |
   | `testing/` | test patterns, fixtures, mocking |
   | `tools/` | build tools, deployment, CI/CD, environments |
   | `external/` | knowledge from other repos or websites |
   | `domain/` | business rules and domain logic |

   Use other names when the content calls for them, and don't create a folder that duplicates an existing one.
3. Show the moves:

   ```text
   KB organize
   ===========

   | Now | Moves to | Why |
   |---|---|---|
   | .claude/rules/kb/api-conventions.md | .claude/rules/kb/conventions/api-conventions.md | tags: api, conventions |
   | .claude/kb/release.md | .claude/kb/tools/release.md | tags: release, ci |

   New folders: conventions/, tools/
   Staying: _index.md, _global-learnings.md, _log.md, README.md
   ```

   Ask (Header: "KB Organize"; Options: "Apply all" | "Let me adjust" | "Cancel"). With "Let me adjust", take new destinations as free text and show the plan again.
4. Move each file (kb-format.md, Moving and deleting files), staying in the same tree so its load mode doesn't change. Update the paths in `_index.md` and in other articles' Related sections. Don't change `last-updated`: the knowledge didn't change.
5. Append `## [{date}] prune | Organized {n} articles into folders` with the moves to the log, and report the files moved and folders created.
