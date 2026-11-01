# The Nine CI Checks

Each check says what to measure, where to look, the usual causes, the fixes, and how to estimate a saving. "The summary" means the output of `ci_timings.py summarize` and its `summary.json`.

Every fix goes in one of three groups:

- **Free:** a config change that keeps the same checks and costs nothing extra.
- **Costs money:** bigger or paid runners, a runner provider, or more runner minutes on a private repo.
- **Runs fewer or different checks:** anything that skips tests, runs them only for some changes, moves them to a later stage, or swaps a tool for one that checks different things.

Only free fixes go in the report's Findings table. The other two groups go under "For You to Decide".

## Shared rules

- **Two kinds of saving.** A fix to the job that finishes last shortens the wait for a CI result. A fix to any other job saves runner minutes, and shortens the wait only if that job then becomes the last one. The summary's "Finishes last most often" column names the job on the critical path. Say which kind each saving is.
- **Count the jobs a fix touches.** A setup fix shared by four jobs saves its seconds four times in runner minutes, but only once on the critical path.
- **Billing.** GitHub bills hosted runners per job, rounded up to a whole minute, and public repos use standard hosted runners for free. A new job or shard on a private repo adds at least one billed minute per run. Check the repo's visibility in the summary before you call a change free.
- **Runner specs and limits change.** Before you state a runner's cores or memory, or a plan's limit on concurrent jobs, look up GitHub's current "GitHub-hosted runners" reference and "Actions limits" pages. Public and private repos get different standard runners. Quote the page and the date you read it.
- **Measured, then estimated.** Prefer a measured comparison: the same step in runs that hit the cache, the same job on another runner, or the shard that's already fast. Otherwise do the arithmetic from measured numbers and show it. Mark every figure that isn't measured as an estimate.

## C1. Queueing on the default runners

**Measure.** "Machine wait by runner" in the summary, and the Queue column of the slowest jobs. GitHub creates a job only once the jobs it `needs:` have finished, so the queue time is machine wait, with one exception. A job with an `environment:` that has required reviewers or a wait timer waits for that approval, and the wait shows up as queue time. Leave those jobs out of machine-wait findings. Also read "Delay before a run's first job" and "Commits that ran a workflow for both push and pull request".

**Look at.** `runs-on` in each workflow, `concurrency:` blocks, the `on:` triggers, the number of jobs per commit (matrix size included), and the macOS and Windows jobs. macOS runners usually have a lower limit on concurrent jobs.

**Usual causes:**

- The account hits its limit on concurrent jobs. Many jobs per commit times many open PRs fills it fast, especially when agents push often.
- Superseded runs keep going after a new push to the same PR.
- A workflow runs twice per commit, once for `push` and once for `pull_request`.
- Tiny jobs whose setup costs more than their work, each taking a runner slot.
- A self-hosted pool or a larger-runner group that is too small.
- Runs wait in a `concurrency:` group without `cancel-in-progress`.

**Fixes:**

- Free: add `concurrency: { group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }` to PR workflows. Use `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` when runs on the default branch must finish.
- Free: limit `push` to the default branch (`on: push: branches: [main]`) when `pull_request` already covers PR branches.
- Free: merge tiny jobs that share setup into one job. Do this when each job's setup is larger than its work.
- Costs money: larger runners, a paid runner provider, or more self-hosted capacity.

**Saving.** A queue fix saves up to the job's queue median on each commit, and the p90 shows the worst waits. Cancelling superseded runs saves the runner minutes of every run cancelled. Estimate that from the share of PR commits followed by another push within the run's length.

## C2. Slow lint

**Measure.** The lint step's work time in the step tables. Look for a cache line for the linter's cache in the sampled logs.

**Look at.** The lint command in the workflow and in `package.json` scripts (or `Makefile`, `pyproject.toml`, `.pre-commit-config.yaml`). Read the linter config: type-aware rules, plugins, ignore patterns, and the files it lints.

**Usual causes:**

- No lint cache, or a cache that never hits. ESLint's default cache checks file modification times, and every checkout sets new ones.
- Type-aware rules (typescript-eslint with `project` or `projectService`) run on the whole repo.
- The linter scans generated files, build output or vendored code.
- Lint runs again inside the test or build job.
- The linter runs on one thread.

**Fixes:**

- Free: ESLint `--cache --cache-strategy content --cache-location <file>`, with that file restored and saved through `actions/cache`. Prettier 3 has `--cache` too.
- Free: ignore generated, build and vendored folders.
- Free: drop the extra lint run from other jobs.
- Free: use the linter's own parallel mode when the installed version has one, such as ESLint's `--concurrency` option. Check the installed version first.
- Runs fewer or different checks: lint only the changed files on PRs, or switch to a faster linter whose rules differ.

**Saving.** With a warm cache, a lint run checks only the changed files. Estimate the saving from the share of files a typical PR changes (`git diff --stat` on recent merges), and mark it as an estimate.

## C3. Slow typechecking

**Measure.** The typecheck step's work time. It may hide inside a build step, so look for `tsc`, `vue-tsc`, `mypy`, `pyright` or the build tool's own type check.

**Look at.** `tsconfig*.json` (`incremental`, `composite`, `skipLibCheck`, `include`), project references, the build tool's typecheck plugin, and `mypy.ini` or `pyproject.toml`.

**Usual causes:**

- No incremental cache, or the `.tsbuildinfo` or `.mypy_cache` file isn't kept between runs.
- `skipLibCheck: false`, so every `.d.ts` file in `node_modules` gets checked.
- The project gets checked twice, for example by `tsc` and again by the bundler's checker, or once per package without project references.
- `include` reaches test fixtures, generated files or build output.

**Fixes:**

- Free: `incremental: true`, with the build info file cached by `actions/cache`. The cache key should include the lockfile and tsconfig hashes.
- Free: `tsc --build` with project references in a monorepo.
- Free: `skipLibCheck: true` when the team agrees that library types don't need checking. Name the trade-off in the finding.
- Free: check once, in one job.
- Runs fewer or different checks: a native or faster checker, such as the Go-based TypeScript compiler (`tsgo`). Check its current release status and whether it supports the project's config before you suggest it.

**Saving.** An incremental run with a warm cache rechecks only what changed. Measure a cold and a warm run locally when you can (`time npx tsc --noEmit` twice, keeping the build info file) and use that ratio.

## C4. Tests that aren't sharded, or machines that are too small

**Measure.** The test step's work time, and the "Matrix jobs" table: existing shards and how uneven they are. Read the test runner's timing line in the sampled logs.

**Look at.** The test command and the runner's config: `jest.config.*`, `vitest.config.*`, `playwright.config.*`, `pytest.ini` or `pyproject.toml`, `.rspec`, the `go test` flags. Note `--runInBand`, `maxWorkers`, `workers`, `-n`, `-p` and `fullyParallel`. Compare them with the runner's core count.

**Usual causes:**

- One long test job on one machine.
- Shards split by file count, not by time, so one shard finishes much later than the rest.
- The runner uses one worker (`--runInBand`, `workers: 1`) on a multi-core machine.
- CPU-bound tests on a 2-core runner.

**Fixes:**

- Free: raise the worker count to match the cores. This keeps one job, so it adds no runner minutes.
- Free on public repos, costs money on private ones: a matrix of N shards. Jest, Vitest and Playwright take `--shard=i/N`. pytest uses pytest-split, or pytest-xdist inside one job.
- Free: balance uneven shards. Playwright's `fullyParallel` splits shards by test instead of by file, and pytest-split splits by stored durations.
- Costs money: a bigger runner.

**Saving.** Each shard takes about work / N plus the job's full setup. The new critical path is the slowest shard. Runner minutes grow by about (N − 1) × setup. Show the arithmetic.

## C5. Every test file reloads the whole app

**Measure.** The test runner's own breakdown. Vitest's `Duration` line splits time into transform, setup, collect, environment and tests. When setup, collect and environment far exceed tests, each file pays a large start-up cost. In Jest, compare the per-file times in a verbose run with the time of the tests inside them. pytest's `--durations` lists slow setup.

**Look at.** Global setup and per-file setup: `setupFiles`, `setupFilesAfterEach`, `globalSetup`, `conftest.py` fixtures and their scope, Rails and Django test settings, and .NET `WebApplicationFactory` use. Check whether test files import a barrel or entry point that loads the whole app.

**Usual causes:**

- The app, database or server boots in `beforeAll` or a function-scoped fixture in every file.
- Each file imports the full app through an index file.
- Each test file migrates or seeds a database.
- A heavy test environment (jsdom, happy-dom) for tests that don't need one.

**Fixes:**

- Free: move one-time work to global setup, or to a session-scoped fixture.
- Free: import the module under test, not the app's entry point.
- Free: set the lighter `node` environment for files that don't touch the DOM.
- Free: migrate once and reset the database between tests with transactions.
- Runs fewer or different checks: turn off isolation between files (Vitest `isolate: false`). It is often the biggest win, and it can let state leak between tests. Propose it only with a plan to run the suite several times.

**Saving.** Measure the setup share from the runner's own line. Then estimate what's left after the change from one file run alone (`npx vitest run path/to/one.test.ts`).

## C6. Slow setup

**Measure.** The Setup column, and the setup steps in the step tables: checkout, toolchain, cache restore, install, browser download. The sampled logs show cache hits and misses. A slow job whose log has no cache lines restores no cache at all.

**Look at.** `actions/checkout` inputs (`fetch-depth`, `filter`, `lfs`, `submodules`), the `setup-*` actions and their `cache` input, `actions/cache` keys and paths, the install command, `postinstall` scripts that download binaries (Playwright, Cypress, Puppeteer, Electron), container images, and any `-j`, `--concurrency` or worker settings.

**Usual causes:**

- No dependency cache. This is common in jobs added after the first one, which copied the steps without the `cache:` line.
- A cache key that changes on every run, such as one built from `github.sha` or a timestamp.
- A cache that never saves, because the job fails before the save step.
- A cache saved only on PR branches. A run can restore caches from its own branch and from the default branch, so when the default branch never saves one, every new PR starts cold.
- `fetch-depth: 0` when the job needs no history. A job that needs history can use `filter: blob:none` so the clone skips file contents it doesn't need.
- Browsers or other binaries downloaded fresh in every run.
- More parallel tasks than cores (`make -j16`, `turbo --concurrency=10`, `pytest -n 8` on 2 cores). Inside containers, tools can see the host's cores instead of the container's limit.
- Steps that build the same thing in several jobs, instead of building once and passing an artifact.

**Fixes:**

- Free: the setup action's `cache:` input, or `actions/cache` keyed on the OS and the lockfile hash, with `restore-keys` for partial hits.
- Free: `fetch-depth: 1` (the checkout default) or `filter: blob:none`. Check that the version of `actions/checkout` the workflow pins supports `filter`.
- Free: cache the browser folder keyed on the tool's version, or use the tool's official container image.
- Free: match parallel settings to the runner's cores.
- Free: build once, then share the output with `actions/upload-artifact` and `actions/download-artifact`.

**Saving.** Compare the same setup step in runs that hit the cache with runs that missed it. That's a measured saving. Multiply by the number of jobs that run the step for runner minutes.

## C7. Jobs that don't run in parallel

**Measure.** Compare the time to a CI result with the slowest single job. When the wait is much longer than any job, jobs run one after another. Check `needs:` chains and long single jobs that run several tasks in a row.

**Look at.** `needs:` in every workflow, jobs that run lint, typecheck, test and build in sequence, and workflows triggered by `workflow_run` after another workflow.

**Usual causes:**

- `needs:` used for ordering when there's no real dependency, such as tests waiting for lint.
- One job runs every task in sequence.
- A second workflow starts only after the first one finishes.

**Fixes:**

- Free: drop `needs:` that has no real dependency. Keep it where a job uses another job's output or artifact.
- Free on public repos, costs money on private ones: split a sequential job into parallel jobs. Each new job pays the full setup again, so split only when a task's work time is larger than about twice the job's setup.
- Free: run independent tasks in parallel inside one job, with the task runner's own parallel mode (`turbo run lint typecheck test`, `npm-run-all --parallel`, `nx run-many --parallel`).

**Saving.** The new critical path is the longest remaining chain: the queue, setup and work of each job on it. Compute it from the measured job times.

## C8. Every PR runs the full test suite

**Measure.** Compare the files a typical PR changes (`gh pr list --state merged --limit 20 --json files`) with what CI runs. Docs-only or single-package PRs that run every suite are the signal.

**Look at.** `paths` and `paths-ignore` in `on:`, job-level `if:` conditions, monorepo tools (Nx, Turborepo, Bazel, pnpm `--filter`) and their affected-only modes, and a merge queue (`merge_group` trigger).

**Usual causes:**

- No path filters, so a README change runs every suite.
- A monorepo runs every package's tests on every PR.
- Slow end-to-end suites run on every push instead of before merge.

**Fixes.** All of these run fewer checks on some PRs, so they go under "For You to Decide":

- Path filters. A required check whose workflow is skipped by `paths` stays pending and blocks the merge. Use a job-level `if:` with a step that detects changed paths, and one always-run job that reports the result to the branch rules.
- Affected-only runs: `nx affected`, `turbo run test --filter=...[origin/main]`, Jest `--changedSince`, Vitest `--changed`.
- Run the slowest suites in the merge queue, or on the default branch, instead of on every PR push.

**Saving.** Take the share of recent PRs that wouldn't trigger the suite, times the suite's runner minutes. Mark it as an estimate.

## C9. No local checks before push

**Measure.** Failed jobs in the summary's Failed column, especially lint, format and typecheck failures. Each one cost a full CI round trip that a check of a few seconds on the developer's machine would have caught. Count them, and read one or two failure logs to confirm the cause (`gh run view --job <id> --log-failed`).

**Look at.** Git hook setups: `.husky/`, `lefthook.yml`, `.pre-commit-config.yaml`, `simple-git-hooks` in `package.json`, `core.hooksPath` and `.githooks/`. Also scripts such as `npm run check`, and CONTRIBUTING notes on what to run before pushing.

**Usual causes:**

- No pre-push hook.
- A hook that runs the full suite, so people skip it with `--no-verify`.
- A hook that exists but isn't installed for new clones.

**Fixes:**

- Free: a pre-push hook that runs fast checks on the changed files: format, lint and typecheck. It must stay fast enough that nobody bypasses it. A hook changes every developer's push, so name that in the finding.
- Free: a single `check` script that runs the same commands as CI, documented in CONTRIBUTING. Agents and people can run it before they push. ai-git's `/git-preflight` command runs a project's checks this way.

**Saving.** Failed runs times the median time to a CI result, plus their runner minutes, over the sample. This saving is wait and minutes avoided, not a faster run.
