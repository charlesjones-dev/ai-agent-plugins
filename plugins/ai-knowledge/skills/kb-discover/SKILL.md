---
name: kb-discover
description: "Read the source code to find knowledge nobody wrote down (architecture, naming, API contracts, data models, error handling, configuration, testing patterns) and save it as knowledge base articles scoped to the code they describe. Shows each draft before writing."
argument-hint: "[paths ...] [--focus topic,topic]"
disable-model-invocation: true
---

# Discover knowledge in the code

Read [kb-format.md](kb-format.md) first. It defines the layout, frontmatter, load modes and writing rules used below.

Arguments (may be empty): $ARGUMENTS

This command mines source code, not documentation. Use `/kb-add` for docs, other repos and URLs.

## Step 1: Choose what to analyze

- **Paths** (`src/api src/models`): analyze those folders or files.
- **`--focus api,auth,config`**: look for those topics across the codebase.
- **No arguments**: ask with AskUserQuestion:
  - Header: "KB Discover"
  - Question: "What should I analyze? Point me at folders (such as `src/api`), give me topics (such as `api, auth, error-handling`), or ask for a full scan and I'll sample the codebase for its most important patterns."
  - Options: "Folders" | "Topics" | "Full scan"

  Then ask for the folders or topics as free text when needed.

## Step 2: Check the knowledge base

Run the checks from kb-format.md: stop if there's a 1.x knowledge base (point to `/kb-migrate`) or no knowledge base (point to `/kb-init`), and pass on any git warning. Read the existing articles, including their `paths` and `discovered-from`, so you don't rediscover what's already captured.

## Step 3: Survey the codebase

1. **Structure**: map the top-level layout (`*`, `src/*`, `lib/*`, `app/*`, `packages/*`).
2. **Stack**: look for `package.json` and `tsconfig.json` (Node, TypeScript), `requirements.txt`, `pyproject.toml` or `setup.py` (Python), `go.mod` (Go), `Cargo.toml` (Rust), `*.csproj` or `*.sln` (.NET), `pom.xml` or `build.gradle` (Java), `Gemfile` (Ruby). A project can use several.
3. **Promising folders**: API layers (`api/`, `routes/`, `controllers/`, `handlers/`), data models (`models/`, `entities/`, `schemas/`, `types/`), configuration (`config/`, `settings/`, root config files), services (`services/`, `domain/`, `core/`), infrastructure (`middleware/`, `plugins/`, `interceptors/`), shared code (`utils/`, `lib/`, `shared/`) and tests (`tests/`, `__tests__/`, `spec/`).
4. **Size**: count files per folder. Read everything in small folders (under 10 files). In medium ones (10 to 30), read the key files and sample the rest. In large ones, read entry points, index files, representative samples and the most imported files.

For a full scan, start with entry points, then route definitions, data models, configuration, middleware chains, base classes and shared abstractions, and test setup (fixtures reveal assumptions).

## Step 4: Analyze

Look for knowledge in these areas, and skip any area where the code has nothing meaningful. Don't invent patterns.

1. **Architecture**: layering (controllers, services, repositories), dependency injection, module boundaries and how modules talk, shared versus isolated code, monorepo structure.
2. **Naming and style**: file, class, function and folder naming; export patterns (barrel files, named or default exports); how code is ordered inside files.
3. **API contracts**: route naming and versioning, request and response shapes, authentication and authorization, error format and status codes, pagination and filtering, middleware order.
4. **Data model**: ORM patterns, common fields (timestamps, soft deletes, audit fields), relationships, where validation happens, migrations.
5. **Errors**: error class hierarchy, where errors are caught or passed on, logging, retries and circuit breakers, graceful degradation.
6. **Configuration**: how config loads and is validated, environment variable naming, feature flags, how secrets are supplied (the pattern, never the values), environment-specific behavior.
7. **Testing**: test layout and naming, fixtures and factories, mocking approach, what is and isn't tested, setup and teardown.
8. **Cross-cutting conventions**: log format, shared utilities and how they're meant to be used, shared types, constants and enums, comment conventions (TODO, FIXME, HACK).

Only count something as a convention when it repeats. A pattern in 1 of 20 files isn't one.

## Step 5: Group the findings into articles

Group findings by topic as they naturally fall, not one article per area above. Good: "API conventions", "Data model patterns", "Testing strategy", "Project architecture". Too narrow: "How the User model works". Too broad: "Everything about the codebase". Too vague: "Naming things".

For each proposed article, prepare:

- a path: scoped articles go to `.claude/rules/kb/{category}/{name}.md`, using existing folders where they fit;
- the load mode: usually scoped, with `paths` covering the code it describes (`src/api/**`, `**/*.controller.ts`). Use on-demand for architecture that spans the whole codebase but matters only for some tasks, and suggest pinned only for a short overview nearly every task needs;
- tags, the distilled rules, and `discovered-from` (the folders or files analyzed);
- whether it overlaps an existing article, in which case plan to append to that article.

## Step 6: Report the findings

```text
KB Discover: findings
=====================

Analyzed: src/api/ (23 files), src/models/ (15 files), src/config/ (4 files)
Stack: TypeScript, Express, Prisma, Jest

1. API conventions
   → .claude/rules/kb/conventions/api-conventions.md (scoped: src/api/**, src/routes/**)
   → tags: api, rest, conventions, express
   → from: src/api/, src/middleware/
   - Routes follow /api/v{n}/{resource}
   - Every handler is wrapped in asyncHandler()
   - Responses use a { data, meta, error } envelope

2. Testing strategy
   → .claude/rules/kb/testing/testing-strategy.md (scoped: tests/**, **/*.test.ts)
   → tags: testing, jest, fixtures
   → from: tests/
   - Test files mirror src/
   - Integration tests hit a real test database; repositories aren't mocked

Overlap with existing articles: none
```

Ask (Header: "KB Discover: Findings"; Question: "I found {n} areas worth saving. Which should I create?"; Options: "Create all" | "Let me pick" | "Adjust and create" | "Cancel"). With "Let me pick", take comma-separated numbers. With "Adjust and create", take free-text changes (rename, merge two, add or remove findings, change paths or load modes).

## Step 7: Draft and approve each article

Get today's date once (kb-format.md, Dates). Then, one article at a time:

1. Write the article: rules in the imperative ("Use UUIDs for primary keys", not "The codebase uses UUIDs"), short reasons where they aren't obvious, short code snippets only where they make a rule clearer, 50 to 150 lines. Add the frontmatter from kb-format.md, including `discovered-from`, and a Related section of paths to articles that bear on the same tasks, if any.
2. Show the full draft and ask (Header: "KB Discover: {topic}"; Options: "Approve" | "Edit and approve" | "Skip"). With "Edit and approve", apply the corrections and show the result once more.
3. Write only after approval.
4. When appending to an existing article, add only new knowledge, show just the new lines and the frontmatter changes for approval, merge tags, add to `discovered-from` and update `last-updated`.

After the first three articles, offer to approve the rest without review.

## Step 8: Finish

1. Where new articles and existing ones bear on the same tasks, list each in the other's Related section as a path (kb-format.md, Related articles).
2. Add `_index.md` lines for the new scoped and on-demand articles, with each one's `tags` as keywords and its `paths` after "loads with".
3. Append to the log:

   ```markdown
   ## [{date}] discover | Knowledge found in the code
   - Analyzed: {folders and files}
   - Created: {paths}
   - Updated: {paths}
   ```

4. Report the articles created and updated with their load modes and key rules, the links added, and coverage: what was analyzed, whether large folders were sampled rather than read in full, and which other folders might be worth a `/kb-discover {folders}` run.

## Quality rules

- Capture rules that change how Claude writes code here, not API documentation. Ask: would knowing this change the code Claude writes?
- Never record secrets, private hostnames or IP addresses found in code. Record the pattern ("the database URL comes from `DATABASE_URL`").
- Be concrete: "Routes use /api/v2/{resource}/{id}" beats "Routes follow REST conventions."
- Check `paths` with Glob before writing: a scoped article whose globs match nothing never loads.
