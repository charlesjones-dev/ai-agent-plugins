---
name: kb-add
description: "Add knowledge to the team knowledge base from a note, project files or folders, another repo, a URL, or the project's own CLAUDE.md and docs/. Distills it into articles, picks how each one loads, records where it came from, and shows every draft before writing."
argument-hint: "[note | path, glob or URL ... | --absorb]"
disable-model-invocation: true
---

# Add to the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the layout, frontmatter, load modes and writing rules used below.

Arguments (may be empty): $ARGUMENTS

## Step 1: Work out what to add

| Arguments | Mode |
|---|---|
| None | Ask (below) |
| `--absorb` | **Absorb**: review the project's CLAUDE.md and `docs/` for content that belongs in the knowledge base |
| Only paths, globs and URLs, separated by spaces or new lines | **Sources**: distill each into articles |
| Only paths under `.claude/rules/kb/` or `.claude/kb/` | **Check**: fix up article files someone added by hand |
| Anything else | **Note**: the text is one learning or rule |

A token counts as a source when it starts with `http://` or `https://`, or when it's an existing file, an existing folder or a glob that matches files. Paths outside the project, such as a sibling repo, are fine. If some tokens are sources and the rest is prose, treat the whole text as a note and mention that the user can pass the paths alone to import them.

With no arguments, ask with AskUserQuestion:

- Header: "KB Add"
- Question: "What do you want to add to the knowledge base?"
- Options: "A note or rule" | "Files, a folder or another repo" | "A web page" | "Content already in CLAUDE.md and docs/"

Then ask for the text, paths or URLs as free text. The last option is Absorb.

## Step 2: Check the knowledge base

Run the checks from kb-format.md: stop if there's a 1.x knowledge base (point to `/kb-migrate`) or no knowledge base (point to `/kb-init`), and pass on any git warning.

Then read what exists: every article under `.claude/rules/kb/` and `.claude/kb/` (path, load mode, `paths`, `tags`, `source`, title), and `_global-learnings.md` if present. Use it to find overlaps, avoid duplicates and suggest destinations.

## Note mode

1. **Secrets.** If the text contains a secret value, strip it, keep only the rule, and tell the user what you removed.
2. **Destination.** Ask with AskUserQuestion:
   - Header: "KB Location"
   - Question: "Where should this go?"
   - Options, as they apply:
     - up to two existing articles that fit, matched on tags and topic, each with its load mode ("Append to `.claude/rules/kb/conventions/api.md` (scoped: src/api/**)");
     - a new article with a suggested path and load mode;
     - "Global learnings (loads every session)", only when the rule applies across the whole project;
     - "Somewhere else", followed by a free-text path.
3. **New article settings.** For a new article, suggest tags and ask (Header: "KB Tags"; Options: "Use suggested" | "Let me adjust"). Then suggest a load mode, inferring globs from any folders or file types the note mentions (Header: "Loading"; Question: "How should Claude Code load it?"; Options: "Scoped: {globs}" | "On-demand (keywords: {tags})" | "Pinned: every session" | "Let me adjust").
4. **Write.** Get today's date once.
   - Existing article: add the rule under `## Key rules`, in the imperative and concise. If a similar rule exists, update it instead; if the note contradicts one, replace it. Update `last-updated`, and add new tags or links.
   - New article: use the frontmatter and body from kb-format.md, in the folder that matches the load mode.
   - Global learnings: if `.claude/rules/kb/_global-learnings.md` doesn't exist, create it (frontmatter `tags: [global, cross-cutting]`, `created`, `last-updated`; heading `# Global learnings`; rules under `## Key rules`). Add the rule as a bullet, without duplicates, and remove placeholder text.
5. Add a line to `_index.md` for a new scoped or on-demand article (or update the keywords of an existing article whose `tags` changed), and append an `add` entry to the log with the destination and the rule.
6. Report what was saved and where, the entry as written, its tags and load mode, and any links added.

## Sources mode

### Find the content

- **Folders**: find `.md`, `.mdx` and `.txt` files recursively. Skip `CHANGELOG.md`, `LICENSE*`, `node_modules/`, `.git/`, `dist/`, `build/` and `coverage/`.
- **Files and globs**: check that each file exists and is text. Skip binaries and say so.
- **URLs**: fetch each one with WebFetch. Record a failed fetch and its error.
- Read the first 30 or so lines of each file, or the fetched page, for a title and summary.
- For sources outside the project, infer a module name: in `{base}/{module}/docs/...` or `{base}/{module}/...` it's `{module}`; otherwise use the folder above the docs folder. Those articles get a `module:{name}` tag.
- Sources under `.claude/rules/kb/` or `.claude/kb/` go to Check mode instead.

### Choose sources

When a folder, glob or several sources were given, show a numbered report grouped by source:

```text
KB Add: sources found
=====================

billing-module (../billing-module/docs/): 3 files
  1. [x] api-conventions.md: "API conventions and patterns"
  2. [x] deployment.md: "Deployment procedures"
  3. [ ] README.md: "Module README" (probably not knowledge-base material)

Web: 2 URLs
  4. [x] https://wiki.example.com/billing/api: "Billing API integration guide"
  5. [ ] https://wiki.example.com/onboarding: failed (404 Not Found)
```

Check the sources that hold actionable knowledge and uncheck READMEs, changelogs, generated content and failed fetches. Ask (Header: "KB Add: Sources"; Question: "Which should I add? Give numbers to toggle, such as `1,3`, or confirm."; Options: "Proceed with selection" | "Select all" | "Let me pick" | "Cancel"). A single file or URL skips this step.

### Plan

For each selected source:

1. Read it in full (or use the fetched page) and classify it: **actionable** (rules, conventions, decisions, constraints, gotchas, API contracts), **reference** (tutorials, onboarding, API listings; flag it, and include it only if the user wants), or **not suitable** (generated, binary, empty, a pure changelog; skip it and say why).
2. Pick a destination: a new article in a category folder (`external/` suits other repos and sites), or an existing article on the same topic. If an article already has this `source`, propose refreshing that article with what changed instead of creating a new one.
3. Suggest tags (with `module:{name}` for outside sources) and a load mode: scoped when the content is about specific folders or file types of this project, otherwise on-demand. Pinned only if the user asks.

Show the plan and ask (Header: "KB Add: Plan"; Options: "Proceed with all" | "Let me adjust" | "Cancel"):

```text
1. ../billing-module/docs/api-conventions.md
   → new: .claude/rules/kb/external/billing-api-conventions.md (scoped: src/billing/**)
   → tags: module:billing, api, conventions
   → actionable

2. https://wiki.example.com/billing/api
   → new: .claude/kb/external/billing-api-integration.md (on-demand: billing, api, integration)
   → reference (you asked to include it)

3. ../billing-module/docs/deployment.md
   → append: .claude/kb/tools/deployment.md (overlapping topic)
```

With "Let me adjust", take free-text changes to destinations, tags, load modes or the list, then show the plan again.

### Draft and approve

Get today's date once. Then, one article at a time:

1. Distill the source into an article (kb-format.md, Writing articles). This rule matters most: turn the source into short, actionable rules; don't copy it. Strip any secrets, tokens, cookies or session data that came with fetched content.
2. Set `source` to the original path or URL. For an existing article that already has a `source`, make it a list and add the new one.
3. Show the full draft, frontmatter included, or for an append, only the new lines and the frontmatter changes. Ask (Header: "KB Add: {file name}"; Options: "Approve" | "Edit and approve" | "Skip"). With "Edit and approve", apply the user's corrections and show the result once more.
4. Write only after approval. When appending, add only knowledge the article doesn't already have, merge tags and update `last-updated`.

After the first three articles, offer to approve the rest without review ("Approve the remaining {n} articles without review?").

### Finish

Where new and existing articles bear on the same tasks, list each in the other's Related section as a path (kb-format.md, Related articles). Add `_index.md` lines for new scoped and on-demand articles, and append an `add` entry to the log listing the sources and the files created or updated. Report each article with its source and the key rules it captured, and say that the sources weren't changed. Mention that running `/kb-add` on the same source later refreshes the article.

## Absorb mode

This replaces 1.x `/kb-absorb`. Moving content out of CLAUDE.md can weaken every session, so be conservative.

### Survey

1. **CLAUDE.md.** Split it into sections and classify each:
   - **Core**: the project overview, architecture, build and test commands, workflow, git conventions, rules that apply everywhere. It stays.
   - **Candidate**: knowledge that matters only for one area (a package, a folder, a file type) or one task (deployment, a vendor's API). It can become a scoped or on-demand article.
   - **Redundant**: duplicates an article or is out of date.

   When in doubt, classify a section as core. Moving a section that applies everywhere into a pinned article saves no context, because pinned articles load every session too, so only scoped and on-demand candidates are worth moving.
2. **`docs/`.** Find `.md` files (outside the knowledge base folders) and classify them as **candidate** (rules, conventions, guides Claude should follow in some context), **reference only** (human-facing tutorials, onboarding, API references) or **skip** (generated or irrelevant).
3. **Other docs.** Check `*.md` in the project root (other than CLAUDE.md and README.md), `.github/` (CONTRIBUTING, templates), and `CONTRIBUTING.md`, `ARCHITECTURE.md`, `DECISIONS.md` and ADR folders. Classify them the same way.

Don't touch CLAUDE.md files in subdirectories; Claude Code already loads them only when Claude works in that folder.

### Report and approve

```text
Documentation review
====================

CLAUDE.md
  Can move ({n}):
    1. "{heading}" (lines {a}-{b}) → .claude/rules/kb/{category}/{name}.md (scoped: {globs})
       Why: {it only applies to ...}
  Stays ({n}): "{heading}": {reason}
  Possibly redundant ({n}): "{heading}": {reason}

docs/ ({n} files)
  Can absorb ({n}):
    2. docs/guides/api-guide.md → .claude/kb/conventions/api-guide.md (on-demand: api, rest)
  Reference only ({n}): docs/onboarding.md
  Skipped ({n}): docs/generated/

Other documentation ({n})
  ...
```

Ask (Header: "KB Absorb"; Question: "How do you want to proceed?"; Options: "Move all candidates" | "Let me review each one" | "Cancel"). When reviewing, show each candidate's content and destination (Options: "Move to the knowledge base" | "Keep where it is" | "Different destination" | "Skip"). Confirm every CLAUDE.md section on its own even after "Move all candidates".

### Move

Get today's date once.

- **A CLAUDE.md section**: write a distilled article (kb-format.md, Writing articles) with the chosen load mode, then remove the section from CLAUDE.md. Don't leave a pointer behind: the scoped article loads when its files are touched, and an on-demand article has its line in `_index.md`.
- **A file from `docs/` or elsewhere**: by default, write a distilled article with `source` set to the file and leave the original where it is, since people may read it there. If the file is already short, rule-like and only meant for Claude, offer to move it into the knowledge base instead (`git mv`, then add frontmatter).

Then list related articles in each other's Related sections as paths, add `_index.md` lines for new scoped and on-demand articles, and append an `add | Absorbed project documentation` entry to the log listing what moved. Report the sections moved out of CLAUDE.md, the files absorbed, the articles created, and how many lines shorter CLAUDE.md is now. Remind the user to review the diff and check that Claude still has the context it needs, and that git can restore anything moved by mistake.

## Check mode

This replaces 1.x `/kb-import`. In 2.x there's nothing to register: a file under `.claude/rules/kb/` loads by its location and frontmatter. The check makes hand-added files follow the format.

For each given file:

1. Read it. If there's no frontmatter, propose it: tags inferred from the content and path, `created` and `last-updated` from today's date. If fields are missing, propose them. If it has 1.x fields (`scope`, `pinned`, `related`, `sources`) or `[[name]]` links, convert them the way `/kb-migrate` does: `paths` for `scope`, location for `pinned`, and plain paths in a Related section for the links.
2. Check that its location matches what the user wants. A file in `.claude/rules/kb/` without `paths` loads every session, so ask whether to keep it pinned, scope it (suggest globs from its content), or make it on-demand. Scoped articles and files in `.claude/kb/` need a line in `_index.md`.
3. Show the proposed changes and ask (Header: "KB Check: {file name}"; Options: "Looks good" | "Let me adjust" | "Skip").

Apply what was approved, append an `add | Checked {n} files` entry to the log, and report each file's load mode and the fixes made.
