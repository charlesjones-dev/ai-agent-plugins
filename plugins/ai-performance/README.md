# AI-Performance Plugin

**Performance audits for Claude Code, Codex and Cursor.** `/performance-audit` reads your codebase and saves a timestamped report with an impact score for each bottleneck it finds. `/performance-ci` measures where your GitHub Actions time goes and says which line to change to cut it.

---

## What This Plugin Does

The plugin ships two skills:

- `/performance-audit` finds code-level performance problems during development, before they reach production.
- `/performance-ci` finds where each pull request's CI wait goes: waiting for a machine, setup, or the checks themselves.

## Limits

`/performance-audit` reads code. It doesn't run your app, so it can't measure execution time or Core Web Vitals in a browser. Pair it with profiling and load tests. Improvement figures in the report are estimates.

`/performance-ci` measures GitHub Actions only, through the GitHub CLI (`gh`). For another CI system, it offers a review of the config with no measured times. Its savings are estimates built from the measured times, and they show how each one was worked out. A change shows its effect only after the new workflow has run on GitHub.

## Available Skills

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

It needs the GitHub CLI, logged in with read access to the repository's Actions (`gh auth login`), and Python 3.

---

## Quick Start

### Installation

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

### Usage

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

---

## Features

### `/performance-audit`

#### Performance Pattern Detection

- **N+1 Query Problems**: Identifies loading related entities in loops
- **Synchronous/Blocking Operations**: Detects blocking database calls, I/O operations, and event loop blocking (Node.js)
- **Memory Issues**: Finds leaks from closures, uncleared listeners, large object allocations, and missing resource disposal
- **Concurrency Problems**: Detects race conditions, deadlocks, connection pool exhaustion, and thread/worker saturation
- **Inefficient Queries**: Detects suboptimal ORM usage and missing projections
- **Missing Caching**: Locates frequently computed operations without caching
- **Database Optimization**: Identifies missing indexes and expensive queries
- **Frontend Performance**: Evaluates Core Web Vitals impact (LCP, INP, CLS), bundle size, and rendering performance
- **GraphQL Issues**: Detects missing query depth limiting, DataLoader opportunities, and over-fetching

#### Detailed Reporting

Each finding includes:

- **Location**: Exact file path and line number
- **Performance Impact**: Numerical impact score (1.0-10.0) with defined severity thresholds
- **Pattern Detected**: What performance issue was identified
- **Code Context**: The problematic code snippet
- **Impact**: Performance cost and scalability concerns
- **Recommendation**: How to optimize it
- **Fix Priority**: When it should be addressed

#### Code Optimization Examples

Reports include 2-4 before/after examples built from code in the findings, each with an expected improvement estimate.

### `/performance-ci`

#### Measurement

A bundled Python script (`scripts/ci_timings.py`, standard library only) pulls the runs, their jobs and steps, and a sample of logs through `gh`, with GET requests only. It reports:

- **Time to a CI result per commit**, for pull requests, pushes and the merge queue, and the job that most often finishes last
- **Queue, setup and work** for every job, as medians and 90th percentiles, with a step-by-step table for the five slowest jobs
- **Machine wait by runner label**, the delay before a run's first job, and commits that ran a workflow for both the push and the pull request
- **Runner minutes**, rounded up per job the way GitHub bills hosted runners
- **Matrix jobs**, such as test shards, and how uneven they are
- **Cache hit and miss lines and test-runner timings** from the logs of the slowest jobs

#### The Nine Checks

1. Queueing on the default runners
2. Slow lint
3. Slow typechecking
4. Tests that aren't sharded, or machines that are too small
5. Every test file reloads the whole app
6. Slow setup: cache misses, full clones, more parallel tasks than cores
7. Jobs that don't run in parallel
8. Every PR runs the full test suite
9. No local checks before push

#### The Report

- **Findings**: free fixes, each with the seconds it costs now, the file and line, the change, the seconds it saves and how that was worked out. Each saving says whether it shortens the wait for a CI result or only saves runner minutes.
- **For You to Decide**: changes that cost money (bigger or paid runners, more shards on a private repository), and changes that run fewer or different checks (path filters, affected-only tests, a different linter).
- **Expected Result**: the time to a CI result now, after the free fixes, and after every decided item.
- **Changes Since the Last Run**: before and after times, when an earlier report is saved.

After the report, it asks which fixes to apply. It applies the free fixes one at a time, biggest first, so each one can be measured. It doesn't commit or push unless you ask.

---

## How It Works

`/performance-audit` scans source files for the patterns above, only under the given directory if you pass one, and tailors findings to the detected stack. Findings are grouped as Critical, High, Medium or Low, and the report ends with a phased optimization roadmap.

`/performance-ci` reads the project's docs and workflow files, measures the runs with its script, ties each slow step to the file and line that defines it, and runs the nine checks. Logs stay in a temporary folder outside the repository.

---

## Best Practices

### When to Run Performance Audits

- Before production deployments
- After implementing new features with database access
- When adding new API endpoints
- After integrating third-party services
- During performance reviews and optimization sprints

### When to Run the CI Audit

- When pull requests wait on CI longer than they take to write
- After adding jobs, workflows or test suites
- After each CI fix ships and has run about ten times, to measure it

### How to Use Audit Results

1. **Prioritize Critical & High findings** - Address these immediately
2. **Review code context** - Understand why each finding impacts performance
3. **Apply optimization examples** - Use provided code fixes as templates
4. **Measure improvements** - Benchmark before and after optimizations
5. **Re-audit after fixes** - Verify improvements and track progress

---

## Configuration

There's nothing to configure.

`/performance-audit` saves its reports to `docs/performance/` at the repository root as `YYYY-MM-DD-HHMMSS-performance-audit.md` (e.g., `2025-10-17-143022-performance-audit.md`). This timestamp-based naming ensures multiple audits on the same day don't overwrite each other.

`/performance-ci` saves its report there as `YYYY-MM-DD-HHMMSS-ci-audit.md` when you pass `save=yes`, or when an earlier CI report is already there.

---

## Plugin Details

- **Name:** AI-Performance
- **Version:** 2.1.0
- **Type:** Skill
- **Features:**
  - Skills: `/performance-audit`, `/performance-ci`
- **License:** MIT
- **Author:** Charles Jones

---

## Credits

`/performance-ci` is inspired by [a post by Vox](https://x.com/Voxyz_ai/status/2116636332344889391) (Voxyz_ai on X) with a prompt for a CI audit. It follows the post's approach: split each job's time into queue, setup and work, check nine causes, and report before changing anything. Its text and measurement script are original.

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License - See [LICENSE](LICENSE) file for details.
