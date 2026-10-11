---
name: kb-query
description: "Answer a question from the team knowledge base with cited articles and offer to file the answer back as an article. Also searches by keyword or tag:name and lists every article with how it loads."
argument-hint: "<question> | search <terms> | tag:<tag> | list"
disable-model-invocation: true
---

# Query the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the layout, frontmatter and load modes used below.

Arguments (may be empty): $ARGUMENTS

## Step 1: Pick the mode

| Arguments | Mode |
|---|---|
| `list` | **List**: show every article and how it loads |
| `tag:{name}` | **Search** by tag |
| `search {terms}` | **Search** by keyword |
| One or two words, with no question mark or question word | **Search** by keyword, then offer an answer |
| Anything else | **Answer** the question |
| None | Ask (below) |

With no arguments, ask with AskUserQuestion:

- Header: "KB Query"
- Question: "What do you want to know? Ask a question, search for a keyword or `tag:name`, or list the knowledge base."
- Options: "Ask a question" | "Search" | "List everything"

Then ask for the question or search terms as free text.

## Step 2: Check the knowledge base

Run the checks from kb-format.md: stop if there's a 1.x knowledge base (point to `/kb-migrate`) or no knowledge base (point to `/kb-init`).

Gather the articles: every `.md` file under `.claude/rules/kb/` and `.claude/kb/` except `_index.md`, `_log.md` and `README.md`. If there are none, say "The knowledge base has no articles yet. Add some with `/kb-learn`, `/kb-add` or `/kb-discover`." and stop.

List and Search modes are read-only.

## List mode

For each article, read its frontmatter and title, and work out its load mode from its location and `paths`. Also check:

- frontmatter: missing, YAML that won't parse, missing `tags`, `created` or `last-updated`, 1.x fields (`scope`, `pinned`, `related`, `sources`) or `[[name]]` links;
- a scoped or on-demand article without a line in `_index.md`, or an index line pointing at a missing file;
- a scoped article whose `paths` match no file (check with Glob);
- Related entries that point at files that don't exist.

```text
Knowledge base
==============

Pinned (every session): {n} articles, {lines} lines
| Article | Tags | Updated | Notes |
|---|---|---|---|
| _global-learnings.md | global | 2026-09-14 | 12 rules |

Scoped: {n} articles (each also has an index line)
| Article | Paths | Tags | Updated | Notes |
|---|---|---|---|---|
| conventions/api-conventions.md | src/api/**, **/*.controller.ts | api, rest | 2026-08-02 | |
| testing/e2e.md | e2e/** | testing | 2026-05-30 | paths match no files |

On-demand: {n} articles
| Article | Index line | Tags | Updated | Notes |
|---|---|---|---|---|
| tools/release.md | release steps and rollback rules | release, deploy | 2026-07-11 | |

Related
- conventions/api-conventions.md → security/auth-rules.md, conventions/api-errors.md

Summary: {n} articles, {n} with problems
```

If there are problems, suggest the fix: `/kb-prune` for content, links and paths that match nothing; `/kb-migrate` for 1.x fields, `[[name]]` links and format problems; `/kb-add {path}` for an article added by hand.

## Search mode

1. **By tag** (`tag:security`): match the tag against each article's `tags`, ignoring case. Also list articles whose Related section points at a match.
2. **By keyword**: search article content (Grep, ignoring case), file and folder names (`api` matches `api-conventions.md`), titles and tags. Search `_global-learnings.md` too.

```text
KB search: "{query}"
====================

1. .claude/rules/kb/conventions/api-conventions.md (scoped: src/api/**)
   tags: api, rest | see also: security/auth-rules.md | updated 2026-08-02
   > matching line
   > matching line

2. .claude/kb/tools/release.md (on-demand)
   tags: release | updated 2026-07-11
   > matching line

Linked to a match:
3. .claude/rules/kb/security/auth-rules.md, linked from api-conventions.md

Global learnings:
   > matching rule

{n} matches in {n} articles.
```

With no matches: "Nothing in the knowledge base matches '{query}'. It has {n} articles tagged: {tags}."

When the search came from one or two words rather than `search` or `tag:`, end by offering to answer it as a question.

## Answer mode

### Find the relevant articles

1. Read `_index.md` for the scoped and on-demand articles and their keywords.
2. Match the question's keywords against file names, titles, tags, index lines and, for scoped articles, the folders their `paths` cover.
3. Read the most relevant articles in full, usually 3 to 8.
4. Follow the Related paths in those articles to others that look pertinent.
5. Read `_global-learnings.md` for cross-cutting rules that apply.

### Answer

- Draw on several articles where you can; connecting them is the point.
- Cite the article behind each part of the answer by its path ("Per `conventions/api-conventions.md`, every route is versioned").
- Point out contradictions between articles.
- Name gaps: if the knowledge base doesn't cover part of the question, say so and suggest how to fill it (`/kb-discover src/deploy`, or `/kb-add` with a doc or URL). Answer that part from the code only if you checked the code, and say that you did.
- Use the format that fits: prose to explain, bullets for rules, a table to compare, code blocks for examples.

### Offer to file the answer

Ask (Header: "File Answer to KB?"; Question: "This answer drew on {n} articles. Save it as an article for future sessions?"; Options: "Save as an article" | "Skip"). Recommend saving when the answer drew on three or more articles, or produced a comparison, an overview or a decision record. Still offer, without pushing, when it only restated one article. With "Skip", stop; nothing is written.

### File it

1. **Where**: suggest a path and load mode. A synthesis of scoped articles about the same folders can be scoped to them; most syntheses are on-demand. Ask (Header: "KB File Location"; Options: "{suggested path} ({mode})" | "Somewhere else").
2. **Write**: get today's date once (kb-format.md, Dates). Rewrite the answer in article style: headings, imperative rules where they fit, no conversational phrasing, citations kept as paths. Frontmatter adds `type: synthesis` and `query: "{the question}"`, plus `tags`, `created` and `last-updated`, and `paths` if scoped. End with a `## Related` section listing the articles consulted, as paths.
3. **Reverse links**: add the new article's path to the Related section of its main sources, and update their `last-updated`.
4. **Index**: add its line to `_index.md`, whether it's scoped or on-demand.
5. **Log**: append

   ```markdown
   ## [{date}] query | {topic}
   - Question: "{the question}"
   - Consulted: {articles}
   - Filed as: {path}
   ```

6. Report the path, load mode, tags and links added.
