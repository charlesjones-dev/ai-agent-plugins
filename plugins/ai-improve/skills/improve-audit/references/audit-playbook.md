# Audit playbook

What to look for in each category. Every subagent, or every direct pass, reads its category's section and "Finding format" at the end. Match the depth to the repository's size. A 2,000-line CLI gets a lighter pass than a 500,000-line monorepo.

A finding needs evidence. "There are probably N+1 queries somewhere" isn't a finding. "`orders/api.ts:142` runs one query per order item inside a loop" is.

## 1. Correctness and bugs

Real bugs found by reading the code, not guesses.

- **Error handling:** swallowed exceptions, empty catch blocks, a catch that only logs on a critical path, UI code with no error state.
- **Async hazards:** promises nobody awaits, races on shared state, missing cancellation or cleanup, such as stale closures in effects and listeners nobody removes.
- **Null and undefined:** non-null assertions on values that can be null, optional chaining that hides a value that must exist, unchecked array indexing.
- **Boundaries:** off-by-one errors, empty collections, timezone and locale assumptions, integer overflow in counters and IDs.
- **State machines:** impossible combinations that the types allow, status enums with unhandled branches. Look for a `default:` that silently does nothing.
- **Concurrency:** check-then-act on a shared resource, several writes with no transaction, retried operations that aren't idempotent, such as webhooks and queue jobs.
- **Type escape hatches:** clusters of `any`, `as` casts and `@ts-ignore`. Each one is a place where someone overruled the compiler.
- **Resource leaks:** handles, connections and subscriptions nobody closes, and a missing `finally`.

## 2. Security

Report only what the code shows. Frame each finding as defensive maintenance: name the code pattern, explain what it costs in production, and describe the fix. Keep the fix at the level of code changes, configuration changes and tests. Never include step-by-step misuse details, or a demonstration against a running system. A regression test for the fix can hold the smallest input that triggers the bug.

**Secrets:** never copy a secret value into a finding or a plan, because those files get committed. Give the `file:line` and the credential type only, such as "a live payment API key at `config.ts:12`". The fix sketch always includes rotation, not only removal. A committed secret stays exposed after someone deletes it.

**By design isn't a finding:** standard platform conventions are intentional, such as honoring `https_proxy` and `NO_PROXY`, reading `~/.netrc`, or a local developer tool that runs the configured package manager. A trade-off that a decision record documents is also settled. Flag one of these only when the implementation adds risk beyond the convention or the documented decision. A stale decision record is a finding of its own: when the code no longer does what the record says, report the drift and don't use the record to dismiss it.

- **Credential hygiene:** hardcoded keys, tokens and passwords, credentials in committed `.env` files, credentials written to logs, events or history stores.
- **Data that reaches an interpreter or a privileged API:** SQL or shell commands built from request data, HTML sinks fed by user content, dynamic execution with runtime input, file paths built from request data. Describe the safer API or the validation boundary.
- **Access control:** endpoints and server actions with no server-side identity check, authorization enforced only in the client, access to an object by ID with no ownership or tenant check, state-changing routes with no check that the request is authentic.
- **Unbounded work on outside input:** a loop, a regular expression, a parser or an allocation whose cost grows without limit on input that someone else controls.
- **Input contracts:** API boundaries that trust request bodies without schema validation, file uploads with no limit on type, size or storage, request data assigned wholesale into persistence models.
- **Dependencies:** run the ecosystem's audit command, such as `npm audit`, `pip-audit` or `cargo audit`, in read-only mode. Report only critical and high advisories that reach runtime code or the build and release path.
- **Production configuration:** broad CORS where credentials are allowed, missing response headers such as a content security policy on sensitive browser surfaces, cookies without `HttpOnly`, `Secure` or `SameSite`, debug or verbose behavior left on in production.
- **Data minimization:** personal or sensitive operational data in logs, stack traces returned to clients, internal error details in API responses.

## 3. Performance

Look for the algorithmic and architectural wins, not micro-optimizations.

- **N+1 patterns:** a query or fetch per item inside a loop or per rendered row, with no batching.
- **Wrong complexity:** nested scans of one collection, a `find` or `filter` repeated inside a hot loop where a keyed lookup belongs.
- **Caching gaps:** the same expensive computation or fetch repeated per request or per render, no memoization at a clear function boundary, no caching of stable data.
- **Payload size:** over-fetching, such as whole rows where IDs are enough, unbounded lists with no pagination, large JSON sent to clients.
- **Frontend, when there is one:** heavy dependencies used for something small, no code splitting on rarely used routes, unoptimized images and fonts, client-side fetches for data that was available at render time, render waterfalls.
- **Backend:** synchronous work that belongs in a queue, a connection per request where pooling exists, indexes that the query patterns suggest are missing. Report a missing index for verification, and don't claim it without schema evidence.
- **Build and CI:** slow CI from missing caches, repeated pipeline steps, test suites that could run in parallel.

## 4. Test coverage

Find the untested code that is dangerous. A coverage percentage doesn't show it.

- Map the critical paths (money, auth, data changes, the feature the repository exists for) and check which have no coverage or trivial coverage.
- A module with high churn in `git log` and no tests is the top refactor risk. Report it as a candidate for characterization tests first.
- **Test quality:** tests that assert nothing meaningful, mocks so heavy that the test checks the mocks, snapshot tests nobody reads, flaky patterns such as real timers, real network calls and order dependence.
- **Missing layers:** a suite of unit tests with no integration coverage of the API boundaries, or slow end-to-end tests for what a unit test would catch.
- **Verification baseline:** can one command tell whether the codebase works? If not, that's the first finding, and its plan comes before any risky change.

## 5. Tech debt and architecture

- **Duplication:** the same logic written in three or more places, and copies that have drifted apart.
- **Layering violations:** UI code that imports data-layer internals, circular dependencies, a `utils` module that everything imports and that holds unrelated code.
- **Dead code:** modules nothing uses, feature flags that are fully rolled out but still branch, commented-out blocks with no explanation, dependencies in the manifest that nothing imports.
- **Oversized modules:** files ten times the repository's median size that everything touches, functions with ten or more parameters or deep conditional nesting.
- **Inconsistent patterns:** three ways to fetch data, handle errors or style components in one repository. Pick the one the team moved to most recently, and plan the consolidation.
- **Abstraction mismatches:** an abstraction with a single implementation, or no abstraction where one change always means editing the same several files together.

## 6. Dependencies and migrations

- A core framework or runtime that is major versions behind, where staying behind has a real cost: end of life, an end to security fixes, or an ecosystem that has moved on. Not every minor bump.
- Deprecated APIs in use that have an announced removal date.
- Abandoned dependencies on critical paths: no release in years, or an archived repository.
- Two dependencies that solve the same problem, such as two date libraries or two HTTP clients.
- A lockfile that disagrees with the manifest, and versions pinned differently across a monorepo.
- For each migration candidate, estimate how many files it touches. That number drives the effort, and whether to recommend the migration at all.

## 7. Developer experience and tooling

- **Missing or broken:** a typecheck script, lint config, a formatter, pre-commit hooks, an editor config.
- **Slow feedback:** a dev server or test run that takes minutes to start, no watch mode, CI with no caching.
- **Onboarding friction:** README setup steps that are wrong or incomplete, required environment variables nobody documents, no `.env.example`.
- **No agent instructions:** a missing `AGENTS.md` or `CLAUDE.md`. Where agents will carry out the plans, this fix has high leverage. Recommend one, and put its outline in the plan.
- **Errors and logging:** unstructured logs on services, no request or correlation IDs, debugging that needs a code change.

## 8. Docs

The lowest default priority. Report a gap only when it has a concrete cost.

- A published package whose public API has no reference docs.
- Architecture decisions that nobody can reconstruct, in an area the team still argues about.
- Stale docs that are wrong, which is worse than missing: setup steps that fail, API examples that no longer compile.

## 9. Direction: features and what to build next

This category looks forward: what is the codebase trying to become? **Every suggestion must cite evidence from the repository.** A suggestion that fits any project in the category, such as "add dark mode" or "add AI", is noise. Sources of grounded evidence:

- **Unfinished intent:** TODO and FIXME clusters around one theme, feature flags nobody rolled out, stubbed or half-built modules, commented-out feature code, work abandoned mid-feature in the git history.
- **Stated but not delivered:** promises in the README, docs or roadmap with no matching code, CLI flags and config options that do nothing, issue templates for features that don't exist. A product brief or requirements doc that names users, use cases or a direction the code hasn't reached is the strongest evidence. Prefer it to inferred intent. Never propose something a decision record already rejected. Note the contradiction instead.
- **One-sided surfaces:** export with no import, create with no bulk create, outgoing webhooks with no incoming ones, an entity with every CRUD operation but one, a public API that internal code clearly needed and built by hand.
- **Cheap next steps:** capabilities that the existing architecture makes unusually cheap, such as a plugin system that is one interface away, or an integration the data model already supports.
- **Manual work around the project:** things its users clearly do by hand, visible in docs, examples and issues, that the project could take over.

Direction findings use the standard format with two changes. **Impact** is the value to users or the product: who wants this, and why now. **Confidence** is how well the evidence grounds the suggestion, not how sure you are that it's the right call. Strategy belongs to the maintainer. Give grounded options with honest trade-offs. Effort estimates are coarser here, so say so. The plan for a direction finding is usually a design or spike plan (investigate, prototype, define the API, list the open questions) and not a plan to build the whole feature.

## Finding format

Every finding, from every category and every subagent, comes back in this shape:

```markdown
### [CATEGORY-NN] Short imperative title

- **Evidence**: `path/file.ts:123`: one sentence on what's there. (Repeat per location. Give the 2 to 5 strongest locations, and add "and about N similar sites" when it's widespread.)
- **Impact**: HIGH, MED or LOW, then what goes wrong or what this costs. HIGH harms users, data, money or security. MED costs the team real time, or harms users in an uncommon case. LOW is a rough edge. Be concrete: "every order-list render runs 1+N queries", not "suboptimal".
- **Effort**: S, M or L for the fix, with its tests. S touches one or two source files. M touches several. L spans modules, or needs a migration.
- **Risk**: What the fix could break. LOW, MED or HIGH, plus one line on why.
- **Confidence**: HIGH (read the code, certain), MED (strong signal, needs verification) or LOW (a smell that needs investigation). A LOW finding gets an "investigate" plan, not a "fix" plan.
- **Fix sketch**: One to three sentences. Not the plan. Enough to judge the effort honestly.
```

Category prefixes: `BUG`, `SEC`, `PERF`, `TEST`, `DEBT`, `DEPS`, `DX`, `DOCS`, `DIR`.

## Ranking

Order the findings by leverage: impact divided by effort, lowered for low confidence and for a risky fix. Break ties in this order:

1. A finding that unblocks others, such as a verification baseline or characterization tests, moves up.
2. A HIGH-confidence security finding goes above a non-security finding of equal leverage.
3. Prefer a finding whose fix is easy to verify. Executor models succeed at those.
4. "Not worth doing" is a valid verdict. Record it with one line of reasoning, so the user knows it was considered.
