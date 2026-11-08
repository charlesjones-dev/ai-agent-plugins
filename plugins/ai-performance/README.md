# AI-Performance plugin

Audits a codebase, or one directory, for performance bottlenecks and saves a timestamped report with an impact score for each finding. `/performance-audit` does the code audit. `/performance-ci` measures where your GitHub Actions time goes and says which line to change to cut it. Both run in Claude Code, Codex and Cursor.

## Limits

`/performance-audit` reads code. It doesn't run your app, so it can't measure execution time or Core Web Vitals in a browser. Pair it with profiling and load tests. Improvement figures in the report are estimates.

`/performance-ci` measures GitHub Actions only, through the GitHub CLI (`gh`). For another CI system, it offers a review of the config with no measured times. Its savings are estimates built from the measured times, and they show how each one was worked out. A change shows its effect only after the new workflow has run on GitHub.

## Available skills

### `/performance-audit`

Audits the whole repository by default. To limit the audit to one part of the code, pass a directory path relative to the repository root, for example `/performance-audit src/api`. The report still goes to `docs/performance/` at the repository root. Other text after the command is ignored.

The audit asks no questions while it runs, so you can use it for unattended or scheduled reviews.

### `/performance-ci`

Measures the last 150 completed GitHub Actions runs of the repository in the working directory. It splits every job's time into three parts: waiting for a machine, setup (checkout, installs, cache restore) and the job's own work. Then it lists the slowest jobs and runs nine checks. Each fix comes with the file and line to change and the seconds it saves. Changes that cost money or run fewer tests go in a separate list for you to decide. Nothing changes until you pick the fixes.

| Argument | Sets | Default |
|----------|------|---------|
| `runs=N` | How many completed runs to measure, up to 1000 | 150 |
| `workflow=NAME` | Only one workflow, by its name, file name or ID | Every workflow |
| `branch=NAME` | Only runs on one branch | Every branch |
| `events=all` | Count every trigger, including schedules and manual runs | Pull requests, pushes and the merge queue |
| `repo=OWNER/NAME` | Measure another repository you can read, without a checkout | The repository in the working directory |
| `save=yes` or `save=no` | Save the report under `docs/performance/` | `yes` when a CI report is already saved there |

It needs the GitHub CLI, logged in with read access to the repository's Actions (`gh auth login`), and Python 3. To measure a fix, run it again after the changed workflow has run about ten times.

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-performance@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-performance@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-performance`. See the [Cursor install steps](../../README.md#cursor).

Install the plugin at user scope to use its commands in every repository.

## Usage

```
# Audit the whole repository
/performance-audit

# Audit one directory
/performance-audit src/api

# Measure the CI time of the repository you're in
/performance-ci

# Measure one workflow over more runs, and save the report
/performance-ci workflow=ci.yml runs=300 save=yes

# Review the generated reports in docs/performance/
```

## Features

### `/performance-audit`

#### What it looks for

- N+1 queries: related entities loaded in loops
- Blocking work: blocking database calls and I/O, and a blocked event loop in Node.js
- Memory: leaks from closures, listeners that are never removed, large allocations, and resources that are never disposed of
- Concurrency: race conditions, deadlocks, an exhausted connection pool, and saturated threads or workers
- Queries: ORM calls that load more than they need, and missing projections
- Caching: work computed again and again with no cache
- Databases: missing indexes and expensive queries
- Frontend: the effect on Core Web Vitals (LCP, INP, CLS), bundle size and rendering
- GraphQL: no query depth limit, places for a DataLoader, and over-fetching

#### What each finding includes

- The file path and line number
- An impact score from 1.0 to 10.0, with defined severity thresholds
- The pattern it found
- The code snippet
- The cost to performance and scaling
- How to fix it
- When to fix it

Reports include 2-4 before/after examples built from code in the findings, each with an estimated improvement.

#### How it works

The audit scans source files for these patterns, only under the given directory if you pass one, and tailors findings to the detected stack. It groups findings as Critical, High, Medium or Low, and the report ends with a phased optimization roadmap.

### `/performance-ci`

#### Measurement

A bundled Python script (`scripts/ci_timings.py`, standard library only) pulls the runs, their jobs and steps, and a sample of logs through `gh`, with GET requests only. It reports:

- **Time to a CI result per commit**, for pull requests, pushes and the merge queue, and the job that most often finishes last
- **Queue, setup and work** for every job, as medians and 90th percentiles, with a step-by-step table for the five slowest jobs
- **Machine wait by runner label**, the delay before a run's first job, and commits that ran a workflow for both the push and the pull request
- **Runner minutes**, rounded up per job the way GitHub bills hosted runners
- **Matrix jobs**, such as test shards, and how uneven they are
- **Cache hit and miss lines and test-runner timings** from the logs of the slowest jobs

#### The nine checks

1. Queueing on the default runners
2. Slow lint
3. Slow typechecking
4. Tests that aren't sharded, or machines that are too small
5. Every test file reloads the whole app
6. Slow setup: cache misses, full clones, more parallel tasks than cores
7. Jobs that don't run in parallel
8. Every PR runs the full test suite
9. No local checks before push

#### The report

- **Findings**: free fixes, each with the seconds it costs now, the file and line, the change, the seconds it saves and how that was worked out. Each saving says whether it shortens the wait for a CI result or only saves runner minutes.
- **For You to Decide**: changes that cost money (bigger or paid runners, more shards on a private repository), and changes that run fewer or different checks (path filters, affected-only tests, a different linter).
- **Expected Result**: the time to a CI result now, after the free fixes, and after every decided item.
- **Changes Since the Last Run**: before and after times, when an earlier report is saved.

After the report, it asks which fixes to apply. It applies the free fixes one at a time, biggest first, so each one can be measured. It doesn't commit or push unless you ask.

#### How it works

The skill reads the project's docs and workflow files, measures the runs with its script, ties each slow step to the file and line that defines it, and runs the nine checks. Logs stay in a temporary folder outside the repository.

## Report files

`/performance-audit` saves its reports to `docs/performance/` at the repository root as `YYYY-MM-DD-HHMMSS-performance-audit.md` (e.g., `2025-10-17-143022-performance-audit.md`). The timestamp keeps two audits from the same day apart.

`/performance-ci` saves its report there as `YYYY-MM-DD-HHMMSS-ci-audit.md` when you pass `save=yes`, or when an earlier CI report is already there.

## Plugin details

- **Name:** AI-Performance
- **Version:** 2.1.1
- **License:** MIT
- **Author:** Charles Jones

## Credits

`/performance-ci` is inspired by [a post by Vox](https://x.com/Voxyz_ai/status/2116636332344889391) (Voxyz_ai on X) with a prompt for a CI audit. It follows the post's approach: split each job's time into queue, setup and work, check nine causes, and report before changing anything. Its text and measurement script are original.

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).
