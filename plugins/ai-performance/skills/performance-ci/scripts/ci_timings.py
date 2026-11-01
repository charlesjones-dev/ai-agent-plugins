#!/usr/bin/env python3
"""Measure where a repository's GitHub Actions time goes.

Part of the ai-performance plugin's /performance-ci skill. Two subcommands:

    python3 -I ci_timings.py fetch --out DIR [--repo OWNER/NAME] [--runs 150]
        [--workflow NAME] [--branch NAME] [--events LIST] [--logs N]
    python3 -I ci_timings.py summarize DIR [--top 5] [--setup REGEX] [--work REGEX]

fetch calls the GitHub CLI (gh) with GET requests only, and saves:

    DIR/meta.json            the repository, its visibility and the fetch settings
    DIR/workflows.json       the repository's workflows and their files
    DIR/runs.json            the completed runs, newest first
    DIR/jobs/<run id>.json   the jobs of each run's latest attempt, with their steps
    DIR/logs/<job id>.log    logs of the slowest jobs, two per job

summarize reads those files, splits each job into three parts, prints Markdown tables
and writes the same data to DIR/summary.json:

    queue  from when GitHub created the job to when a runner picked it up. GitHub
           creates a job only when the jobs it needs have finished, so this is time
           spent waiting for a machine, or for an environment's approval.
    setup  everything in the job that isn't its own work: "Set up job", checkout,
           toolchain setup, cache restore and save, dependency installs, post-job
           cleanup, and the gaps between steps
    work   the remaining steps

--setup and --work take a regular expression that moves matching step names into that
part, for steps the built-in patterns get wrong. Timing tables use successful jobs only.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

DEFAULT_EVENTS = "pull_request,pull_request_target,push,merge_group"
EVENT_FAMILY = {
    "pull_request": "pull request",
    "pull_request_target": "pull request",
    "push": "push",
    "merge_group": "merge queue",
}
ALL_JOBS_ROWS = 30
MAX_RUN_PAGES = 10  # the runs API returns at most 1,000 results when filtered by status
WORKERS = 4
LOGS_PER_JOB = 2

# Step names that are setup rather than the job's own work. GitHub names a step that
# has no `name:` after its command or action, such as "Run npm ci" or
# "Run actions/checkout@v4", so both forms are covered.
SETUP_STEP = re.compile(r"""(?ix)
    ^(set\ up\ job|set\ up\ runner|initialize\ containers|stop\ containers|complete\ job|complete\ runner)$
  | \bcheck\ ?out\b
  | \bsetup\b | \bset\ up\b
  | toolchain | \brustup\b
  | \bcach(e|es|ing)\b | \brestore\b
  | \binstall | \bdeps\b | \bbootstrap\b
  | \bnpm\ ci\b | \bpnpm\ i\b | \byarn(\s+--\S+)*$ | \buv\ sync\b
  | \bgo\ mod\ download\b | \bcargo\ fetch\b
  | \blogin\b | \bbuildx\b | \bqemu\b
  | download-artifact | \bdownload\ artifacts?\b
""")
# An action's display name when its step has no `name:`, such as "Run actions/cache@v4".
ACTION_STEP = re.compile(r"^Run [\w.-]+/[\w./-]+@\S+$")

CACHE_HIT = re.compile(r"(?i)cache hit for|cache restored (successfully|from key)|restored from cache key")
CACHE_MISS = re.compile(r"(?i)cache not found|cache is not found|no cache found|cache miss|failed to restore")
CACHE_SAVE = re.compile(r"(?i)cache saved (successfully|with key)")
TEST_TIMING = re.compile(r"""(?x)
    ^\s*Duration\s+[\d.]+\s*m?s\s*\(          # Vitest
  | ^Time:\s+[\d.]+\s*m?s                      # Jest
  | ^=+\ .*\b(passed|failed)\b.*\ in\ [\d.]+s  # pytest
  | ^\s*\d+\ passed\ \([\d.]+m?s\)             # Playwright
  | ^Finished\ in\ [\d.]+\ (seconds|minutes)   # RSpec
  | ^(Passed|Failed)!\s+-                      # dotnet test
  | ^\s*Summary\ \[\s*[\d.]+s\]                # cargo nextest
  | ^test\ result:\ .*finished\ in\ [\d.]+s    # cargo test
  | ^(ok|FAIL)\s+\S+\s+[\d.]+s                 # go test
""")
LOG_PREFIX = re.compile(r"^\ufeff?\d{4}-\d{2}-\d{2}T[\d:.]+Z ?")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
TIMESTAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$")


class GhError(Exception):
    pass


def fail(message, code=2):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------- fetch

def gh(args):
    env = dict(os.environ, GH_PROMPT_DISABLED="1", GH_PAGER="cat", NO_COLOR="1", CLICOLOR="0")
    try:
        result = subprocess.run(["gh", *args], capture_output=True, env=env)
    except FileNotFoundError:
        fail("gh isn't installed. Install the GitHub CLI from https://cli.github.com and run `gh auth login`.")
    if result.returncode != 0:
        raise GhError(result.stderr.decode("utf-8", "replace").strip() or f"gh exited {result.returncode}")
    return result.stdout


def gh_api(path):
    return json.loads(gh(["api", "-X", "GET", "-H", "Accept: application/vnd.github+json", path]))


_escape_flag = [True]


def gh_log(path):
    # gh 2.8x and later refuse to print terminal escape sequences without this flag,
    # and older versions don't know the flag.
    if _escape_flag[0]:
        try:
            return gh(["api", "-X", "GET", "--allow-escape-sequences", path])
        except GhError as error:
            if "unknown flag" not in str(error):
                raise
            _escape_flag[0] = False
    return gh(["api", "-X", "GET", path])


def slim_run(run):
    keys = ("id", "name", "workflow_id", "path", "event", "status", "conclusion", "head_branch",
            "head_sha", "run_attempt", "run_number", "created_at", "run_started_at", "updated_at")
    return {key: run.get(key) for key in keys}


def slim_job(job):
    keys = ("id", "run_id", "run_attempt", "name", "status", "conclusion", "created_at", "started_at",
            "completed_at", "labels", "runner_name", "runner_group_name")
    slim = {key: job.get(key) for key in keys}
    slim["steps"] = [{key: step.get(key) for key in ("number", "name", "conclusion", "started_at", "completed_at")}
                     for step in job.get("steps") or []]
    return slim


def match_workflow(workflows, wanted):
    wanted_lower = wanted.lower()
    for workflow in workflows:
        path = workflow.get("path") or ""
        if (str(workflow.get("id")) == wanted or (workflow.get("name") or "").lower() == wanted_lower
                or path.lower() == wanted_lower or path.rsplit("/", 1)[-1].lower() == wanted_lower.rsplit("/", 1)[-1]):
            return workflow
    return None


def cmd_fetch(args):
    out = Path(args.out)
    (out / "jobs").mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(exist_ok=True)

    try:
        repo_args = [args.repo] if args.repo else []
        info = json.loads(gh(["repo", "view", *repo_args, "--json", "nameWithOwner,visibility,defaultBranchRef"]))
    except GhError as error:
        fail(f"couldn't read the repository with gh: {error}")
    repo = info["nameWithOwner"]

    workflows, page = [], 1
    while True:
        try:
            batch = gh_api(f"repos/{repo}/actions/workflows?per_page=100&page={page}").get("workflows", [])
        except GhError as error:
            fail(f"couldn't list workflows for {repo}: {error}")
        workflows += [{key: w.get(key) for key in ("id", "name", "path", "state")} for w in batch]
        if len(batch) < 100:
            break
        page += 1

    base = f"repos/{repo}/actions/runs"
    if args.workflow:
        workflow = match_workflow(workflows, args.workflow)
        if not workflow:
            names = ", ".join(f"{w['name']} ({w['path']})" for w in workflows) or "none"
            fail(f"no workflow matches {args.workflow!r}. Workflows: {names}")
        base = f"repos/{repo}/actions/workflows/{workflow['id']}/runs"
    events = None if args.events == "all" else {e.strip() for e in args.events.split(",") if e.strip()}

    runs, skipped_events, page = [], Counter(), 1
    while len(runs) < args.runs and page <= MAX_RUN_PAGES:
        query = f"{base}?per_page=100&page={page}&status=completed&exclude_pull_requests=true"
        if args.branch:
            query += f"&branch={quote(args.branch, safe='')}"
        try:
            batch = gh_api(query).get("workflow_runs", [])
        except GhError as error:
            fail(f"couldn't list workflow runs for {repo}: {error}")
        for run in batch:
            if events is not None and run.get("event") not in events:
                skipped_events[run.get("event")] += 1
                continue
            runs.append(slim_run(run))
            if len(runs) >= args.runs:
                break
        if len(batch) < 100:
            break
        page += 1
    print(f"Listed {len(runs)} completed runs of {repo}.", file=sys.stderr)

    errors = []

    def fetch_jobs(run):
        jobs, page = [], 1
        while True:
            batch = gh_api(f"repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100&page={page}").get("jobs", [])
            jobs += [slim_job(job) for job in batch]
            if len(batch) < 100:
                break
            page += 1
        (out / "jobs" / f"{run['id']}.json").write_text(json.dumps(jobs), encoding="utf-8")
        return len(jobs)

    def safely(function, label):
        def wrapped(item):
            try:
                return function(item)
            except GhError as error:
                errors.append(f"{label} {item['id']}: {str(error)[:200]}")
                return 0
        return wrapped

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        job_count = sum(pool.map(safely(fetch_jobs, "jobs for run"), runs))
    print(f"Saved {job_count} jobs.", file=sys.stderr)

    # Logs of the slowest jobs, for cache hits and misses and test-runner timings.
    durations, recent = defaultdict(list), defaultdict(list)
    run_by_id = {run["id"]: run for run in runs}
    for run in runs:
        path = out / "jobs" / f"{run['id']}.json"
        if not path.exists():
            continue
        for job in json.loads(path.read_text(encoding="utf-8")):
            started, completed = parse_time(job.get("started_at")), parse_time(job.get("completed_at"))
            if job.get("conclusion") != "success" or started is None or completed is None:
                continue
            key = (run_by_id[run["id"]].get("name"), job.get("name"))
            durations[key].append(completed - started)
            recent[key].append((completed, job["id"]))
    slowest = sorted(durations, key=lambda key: statistics.median(durations[key]), reverse=True)[:args.logs]
    wanted = [{"id": job_id} for key in slowest for _, job_id in sorted(recent[key], reverse=True)[:LOGS_PER_JOB]]

    def fetch_log(job):
        data = gh_log(f"repos/{repo}/actions/jobs/{job['id']}/logs")
        (out / "logs" / f"{job['id']}.log").write_bytes(data)
        return 1

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        log_count = sum(pool.map(safely(fetch_log, "log for job"), wanted))

    meta = {
        "repo": repo,
        "visibility": info.get("visibility"),
        "default_branch": (info.get("defaultBranchRef") or {}).get("name"),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "settings": {"runs": args.runs, "workflow": args.workflow, "branch": args.branch,
                     "events": args.events, "logs": args.logs},
        "runs": len(runs),
        "jobs": job_count,
        "logs": log_count,
        "runs_skipped_by_event": dict(skipped_events),
        "errors": errors,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (out / "workflows.json").write_text(json.dumps(workflows, indent=2), encoding="utf-8")
    (out / "runs.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
    print(f"Saved {len(runs)} runs, {job_count} jobs and {log_count} logs from {repo} to {out}.")
    if errors:
        print(f"{len(errors)} request(s) failed. See errors in {out / 'meta.json'}.")


# ------------------------------------------------------------------------ summarize

def parse_time(value):
    if not value:
        return None
    match = TIMESTAMP.match(value)
    if not match:
        return None
    date, clock, fraction, zone = match.groups()
    fraction = (fraction or ".0")[1:7].ljust(6, "0")
    if zone in (None, "Z"):
        zone = "+00:00"
    elif ":" not in zone:
        zone = f"{zone[:3]}:{zone[3:]}"
    return datetime.fromisoformat(f"{date}T{clock}.{fraction}{zone}").timestamp()


def is_setup(name, setup_re, work_re, earlier=()):
    if work_re and work_re.search(name):
        return False
    if setup_re and setup_re.search(name):
        return True
    if name.startswith("Post "):
        # GitHub names an action's cleanup step "Post " plus the action step's name.
        # A step the workflow itself calls "Post comment" has no such earlier step.
        rest = name[5:]
        return rest in earlier or bool(SETUP_STEP.search(rest) or ACTION_STEP.match(rest))
    return bool(SETUP_STEP.search(name))


def spread(values):
    if not values:
        return None
    ordered = sorted(values)
    return {"median": round(statistics.median(ordered)), "p90": round(ordered[math.ceil(0.9 * len(ordered)) - 1]),
            "max": round(ordered[-1])}


def measure(job, run, setup_re, work_re):
    created, started, completed = (parse_time(job.get(key)) for key in ("created_at", "started_at", "completed_at"))
    record = {
        "key": f"{run.get('name')} / {job.get('name')}",
        "workflow": run.get("name"),
        "workflow_path": run.get("path"),
        "job": job.get("name"),
        "job_id": job.get("id"),
        "run_id": run.get("id"),
        "conclusion": job.get("conclusion"),
        "labels": ",".join(job.get("labels") or []) or "(none)",
        "runner_group": job.get("runner_group_name"),
        "created": created,
        "completed": completed,
        "timed": False,
    }
    if job.get("conclusion") == "skipped" or None in (created, started, completed):
        return record
    duration = max(0.0, completed - started)
    steps, work, earlier = [], 0.0, set()
    for step in job.get("steps") or []:
        step_start, step_end = parse_time(step.get("started_at")), parse_time(step.get("completed_at"))
        seconds = max(0.0, step_end - step_start) if step_start is not None and step_end is not None else 0.0
        setup = is_setup(step.get("name") or "", setup_re, work_re, earlier)
        earlier.add(step.get("name") or "")
        steps.append({"number": step.get("number"), "name": step.get("name"), "seconds": seconds,
                      "part": "setup" if setup else "work"})
        if not setup:
            work += seconds
    work = min(work, duration)
    record.update(timed=True, queue=max(0.0, started - created), duration=duration, work=work,
                  setup=duration - work, total=max(0.0, started - created) + duration, steps=steps)
    return record


def table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def clean_log_line(raw):
    return ANSI.sub("", LOG_PREFIX.sub("", raw)).strip()


def read_log(path):
    hits = misses = saves = 0
    cache_lines, test_lines = [], []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = clean_log_line(raw)
            found = False
            if CACHE_MISS.search(line):
                misses += 1
                found = True
            elif CACHE_HIT.search(line):
                hits += 1
                found = True
            elif CACHE_SAVE.search(line):
                saves += 1
                found = True
            if found and line[:200] not in cache_lines and len(cache_lines) < 4:
                cache_lines.append(line[:200])
            if TEST_TIMING.search(line) and len(test_lines) < 5:
                test_lines.append(line[:200])
    return {"hits": hits, "misses": misses, "saves": saves, "cache_lines": cache_lines, "test_lines": test_lines}


def cmd_summarize(args):
    folder = Path(args.dir)
    try:
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        runs = json.loads((folder / "runs.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(f"{folder} doesn't hold fetch output: {error}")
    setup_re = re.compile(args.setup, re.I) if args.setup else None
    work_re = re.compile(args.work, re.I) if args.work else None

    records, by_run = [], defaultdict(list)
    for run in runs:
        path = folder / "jobs" / f"{run['id']}.json"
        if not path.exists():
            continue
        for job in json.loads(path.read_text(encoding="utf-8")):
            record = measure(job, run, setup_re, work_re)
            records.append(record)
            by_run[run["id"]].append(record)
    if not records:
        print(f"No jobs to summarize in {folder}. The fetch found {len(runs)} completed runs.")
        sys.exit(1)

    conclusions = Counter(record["conclusion"] for record in records)
    timed = [record for record in records if record["timed"]]
    ok = [record for record in timed if record["conclusion"] == "success"]

    # Jobs, by workflow and job name.
    groups = defaultdict(list)
    for record in ok:
        groups[record["key"]].append(record)
    failures = Counter(record["key"] for record in records if record["conclusion"] == "failure")
    cancelled = Counter(record["key"] for record in records if record["conclusion"] == "cancelled")
    jobs = []
    for key, items in groups.items():
        jobs.append({
            "key": key,
            "workflow": items[0]["workflow"],
            "workflow_path": items[0]["workflow_path"],
            "job": items[0]["job"],
            "runs": len(items),
            "failures": failures[key],
            "cancelled": cancelled[key],
            "runner": Counter(item["labels"] for item in items).most_common(1)[0][0],
            "runner_group": Counter(item["runner_group"] for item in items).most_common(1)[0][0],
            "queue": spread([item["queue"] for item in items]),
            "setup": spread([item["setup"] for item in items]),
            "work": spread([item["work"] for item in items]),
            "total": spread([item["total"] for item in items]),
            "minutes": round(sum(item["duration"] for item in items) / 60, 1),
        })
    jobs.sort(key=lambda job: (job["total"]["median"], job["runs"]), reverse=True)

    # Steps of the slowest jobs.
    for job in jobs[:args.top]:
        by_step, position = defaultdict(list), defaultdict(list)
        part = {}
        for item in groups[job["key"]]:
            for step in item["steps"]:
                by_step[step["name"]].append(step["seconds"])
                position[step["name"]].append(step["number"] or 0)
                part[step["name"]] = step["part"]
        steps = [{"name": name, "part": part[name], "runs": len(values), **spread(values)}
                 for name, values in by_step.items()]
        steps.sort(key=lambda step: statistics.median(position[step["name"]]))
        job["steps"] = steps

    # Time from the first run's creation to the last job's end, per commit and trigger.
    commits = defaultdict(list)
    for run in runs:
        family = EVENT_FAMILY.get(run.get("event"))
        if family:
            commits[(family, run.get("head_sha"))].append(run)
    walls = defaultdict(list)
    last = defaultdict(Counter)
    for (family, _), commit_runs in commits.items():
        # A failed run ends early and a re-run starts late, so either one skews the time.
        if any(run.get("conclusion") != "success" or (run.get("run_attempt") or 1) != 1 for run in commit_runs):
            continue
        finished = [record for run in commit_runs for record in by_run[run["id"]] if record["timed"]]
        if not finished:
            continue
        start = min(parse_time(run.get("created_at")) for run in commit_runs)
        final = max(finished, key=lambda record: record["completed"])
        walls[family].append(final["completed"] - start)
        last[family][final["key"]] += 1
    per_commit = []
    for family in ("pull request", "push", "merge queue"):
        if walls[family]:
            key, count = last[family].most_common(1)[0]
            per_commit.append({"trigger": family, "commits": len(walls[family]), **spread(walls[family]),
                               "finishes_last": key, "finishes_last_share": round(100 * count / len(walls[family]))})

    # Delay between a run's creation and its first job, such as a run held in a concurrency group.
    delays = defaultdict(list)
    for run in runs:
        firsts = [record["created"] for record in by_run[run["id"]] if record["created"] is not None]
        run_created = parse_time(run.get("created_at"))
        if firsts and run_created is not None:
            delays[f"{run.get('name')} ({run.get('path')})"].append(max(0.0, min(firsts) - run_created))
    start_delay = sorted(({"workflow": name, "runs": len(values), **spread(values)} for name, values in delays.items()),
                         key=lambda row: row["p90"], reverse=True)

    # Commits that ran one workflow twice, once for the push and once for the pull request.
    triggers = defaultdict(set)
    for run in runs:
        triggers[(run.get("name"), run.get("head_sha"))].add(EVENT_FAMILY.get(run.get("event")))
    doubled = Counter(name for (name, _), families in triggers.items() if {"push", "pull request"} <= families)
    duplicate_triggers = [{"workflow": name, "commits": count} for name, count in doubled.most_common()]

    # Machine wait by runner labels, over every job that started.
    queues = defaultdict(list)
    for record in timed:
        queues[record["labels"]].append(record["queue"])
    queue_by_runner = sorted(({"runner": labels, "jobs": len(values), **spread(values)}
                              for labels, values in queues.items()), key=lambda row: row["p90"], reverse=True)

    # Runner time, the way GitHub bills hosted runners: each job rounded up to a whole minute.
    minutes = defaultdict(lambda: [0, 0.0, 0])
    for record in timed:
        row = minutes[record["labels"]]
        row[0] += 1
        row[1] += record["duration"] / 60
        row[2] += math.ceil(record["duration"] / 60) if record["duration"] else 0
    runner_minutes = sorted(({"runner": labels, "jobs": row[0], "minutes": round(row[1], 1), "rounded_up": row[2]}
                             for labels, row in minutes.items()), key=lambda row: row["minutes"], reverse=True)

    # Matrix jobs, such as test shards, grouped by the name before the parentheses.
    families = defaultdict(list)
    for job in jobs:
        base = re.sub(r"\s*\([^()]*\)\s*$", "", job["job"] or "")
        if base != job["job"]:
            families[(job["workflow"], base)].append(job)
    matrix = []
    for (workflow, base), members in families.items():
        if len(members) < 2:
            continue
        works = [member["work"]["median"] for member in members]
        matrix.append({"family": f"{workflow} / {base}", "jobs": len(members), "fastest_work": min(works),
                       "slowest_work": max(works), "slowest_job": max(members, key=lambda m: m["work"]["median"])["job"]})
    matrix.sort(key=lambda row: row["slowest_work"], reverse=True)

    # Cache and test-runner lines in the sampled logs.
    record_by_job = {record["job_id"]: record for record in records}
    logs = []
    for path in sorted((folder / "logs").glob("*.log")):
        try:
            job_id = int(path.stem)
        except ValueError:
            continue
        record = record_by_job.get(job_id)
        logs.append({"job": record["key"] if record else "(unknown)", "job_id": job_id, **read_log(path)})
    logs.sort(key=lambda row: (row["job"], row["job_id"]))

    created = sorted(run.get("created_at") for run in runs if run.get("created_at"))
    summary = {
        "repo": meta.get("repo"),
        "visibility": meta.get("visibility"),
        "default_branch": meta.get("default_branch"),
        "fetched_at": meta.get("fetched_at"),
        "sample": {
            "runs": len(runs),
            "first_run": created[0] if created else None,
            "last_run": created[-1] if created else None,
            "events": dict(Counter(run.get("event") for run in runs)),
            "workflows": dict(Counter(f"{run.get('name')} ({run.get('path')})" for run in runs)),
            "jobs": dict(conclusions),
            "fetch_errors": len(meta.get("errors") or []),
        },
        "setup_pattern_extra": args.setup,
        "work_pattern_extra": args.work,
        "per_commit": per_commit,
        "start_delay": start_delay,
        "duplicate_triggers": duplicate_triggers,
        "jobs": jobs,
        "queue_by_runner": queue_by_runner,
        "runner_minutes": runner_minutes,
        "matrix": matrix,
        "logs": logs,
    }
    (folder / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(render(summary, args.top))


def render(s, top):
    sample = s["sample"]
    jobs = s["jobs"]
    out = [f"# CI timings: {s['repo']}", ""]
    events = ", ".join(f"{name} {count}" for name, count in sorted(sample["events"].items(), key=lambda kv: -kv[1]))
    conclusions = ", ".join(f"{count} {name}" for name, count in sorted(sample["jobs"].items(), key=lambda kv: -kv[1]))
    out.append(f"{sample['runs']} completed runs ({events}) created {sample['first_run']} to {sample['last_run']}, "
               f"in {len(sample['workflows'])} workflow(s). {sum(sample['jobs'].values())} jobs: {conclusions}. "
               f"Repository visibility: {s['visibility']}. Timing tables use successful jobs only. All times in seconds.")
    if sample["fetch_errors"]:
        out.append(f"\n{sample['fetch_errors']} fetch request(s) failed. meta.json lists them.")

    out += ["", "## Time to a CI result per commit", ""]
    if s["per_commit"]:
        out.append("From the first run's creation to the last job's end, for commits whose runs all succeeded on the first attempt.")
        out.append("")
        out.append(table(["Trigger", "Commits", "Median", "p90", "Max", "Finishes last most often"],
                         [[row["trigger"], row["commits"], f"{row['median']} ({row['median'] / 60:.1f} min)",
                           f"{row['p90']} ({row['p90'] / 60:.1f} min)", row["max"],
                           f"{row['finishes_last']} ({row['finishes_last_share']}%)"] for row in s["per_commit"]]))
    else:
        out.append("No commit had all its runs succeed on the first attempt.")

    out += ["", f"## Slowest jobs (top {min(top, len(jobs))} by median total)", ""]
    out.append(table(["#", "Workflow / job", "Runs", "Runner", "Queue", "Setup", "Work", "Total", "p90 total", "Failed"],
                     [[i + 1, job["key"], job["runs"], job["runner"], job["queue"]["median"], job["setup"]["median"],
                       job["work"]["median"], job["total"]["median"], job["total"]["p90"], job["failures"]]
                      for i, job in enumerate(jobs[:top])]))

    for i, job in enumerate(jobs[:top]):
        out += ["", f"### {i + 1}. {job['key']}", "", f"Workflow file: `{job['workflow_path']}`", ""]
        shown = [step for step in job["steps"] if step["median"] >= 1 or step["p90"] >= 1]
        out.append(table(["Step", "Part", "Median", "p90"],
                         [[step["name"], step["part"], step["median"], step["p90"]] for step in shown]))
        hidden = len(job["steps"]) - len(shown)
        if hidden:
            out.append(f"\n{hidden} step(s) under 1 second not shown.")

    out += ["", "## All jobs", ""]
    out.append(table(["Workflow / job", "Runs", "Failed", "Cancelled", "Queue p50/p90", "Setup p50/p90",
                      "Work p50/p90", "Total p50/p90", "Runner minutes"],
                     [[job["key"], job["runs"], job["failures"], job["cancelled"],
                       f"{job['queue']['median']}/{job['queue']['p90']}", f"{job['setup']['median']}/{job['setup']['p90']}",
                       f"{job['work']['median']}/{job['work']['p90']}", f"{job['total']['median']}/{job['total']['p90']}",
                       job["minutes"]] for job in jobs[:ALL_JOBS_ROWS]]))
    if len(jobs) > ALL_JOBS_ROWS:
        out.append(f"\n{len(jobs) - ALL_JOBS_ROWS} faster job(s) not shown. summary.json lists every job.")

    out += ["", "## Machine wait by runner", ""]
    out.append(table(["Runner labels", "Jobs", "Median", "p90", "Max"],
                     [[row["runner"], row["jobs"], row["median"], row["p90"], row["max"]] for row in s["queue_by_runner"]]))

    out += ["", "## Delay before a run's first job", ""]
    out.append("Usually a second or two. A long delay means runs waited, for example in a `concurrency:` group.")
    out.append("")
    out.append(table(["Workflow", "Runs", "Median", "p90", "Max"],
                     [[row["workflow"], row["runs"], row["median"], row["p90"], row["max"]] for row in s["start_delay"]]))

    out += ["", "## Commits that ran a workflow for both push and pull request", ""]
    if s["duplicate_triggers"]:
        out.append(table(["Workflow", "Commits"], [[row["workflow"], row["commits"]] for row in s["duplicate_triggers"]]))
    else:
        out.append("None.")

    out += ["", "## Runner minutes in the sample", ""]
    out.append("Every job that started, any result. GitHub bills hosted runners per job, rounded up to a whole minute.")
    out.append("")
    out.append(table(["Runner labels", "Jobs", "Minutes", "Rounded up"],
                     [[row["runner"], row["jobs"], row["minutes"], row["rounded_up"]] for row in s["runner_minutes"]]))

    out += ["", "## Matrix jobs", ""]
    if s["matrix"]:
        out.append(table(["Matrix", "Jobs", "Fastest work (median)", "Slowest work (median)", "Slowest job"],
                         [[row["family"], row["jobs"], row["fastest_work"], row["slowest_work"], row["slowest_job"]]
                          for row in s["matrix"]]))
    else:
        out.append("None.")

    out += ["", "## Cache and test-runner lines in sampled logs", ""]
    if s["logs"]:
        out.append("Line counts, not restores: one restore can print two or three hit lines. "
                   "A log with no cache lines restored no cache.")
        out.append("")
        out.append(table(["Job", "Job ID", "Hit lines", "Miss lines", "Save lines", "Test-runner timing"],
                         [[row["job"], row["job_id"], row["hits"], row["misses"], row["saves"],
                           " / ".join(row["test_lines"][:2]) or "-"] for row in s["logs"]]))
        quoted = defaultdict(list)
        for row in s["logs"]:
            for line in row["cache_lines"]:
                if line not in quoted[row["job"]] and len(quoted[row["job"]]) < 4:
                    quoted[row["job"]].append(line)
        if quoted:
            out.append("\nCache lines, up to four different ones per job:")
            for job, lines in quoted.items():
                out += [f"- {job}: `{line}`" for line in lines]
    else:
        out.append("No logs were fetched.")

    extra = []
    if s["setup_pattern_extra"]:
        extra.append(f"--setup {s['setup_pattern_extra']!r}")
    if s["work_pattern_extra"]:
        extra.append(f"--work {s['work_pattern_extra']!r}")
    out += ["", "## Step classification", "",
            "Setup is the job's time minus its work steps, so it includes \"Set up job\", checkout, toolchain setup, "
            "cache restore and save, dependency installs, post-job cleanup and the gaps between steps. "
            + (f"Overrides: {', '.join(extra)}." if extra else "No overrides.")]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Measure where a repository's GitHub Actions time goes.")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="download runs, jobs and sample logs with gh")
    fetch.add_argument("--out", required=True, help="folder for the downloaded data")
    fetch.add_argument("--repo", help="OWNER/NAME. Defaults to the repository in the current folder")
    fetch.add_argument("--runs", type=int, default=150, help="completed runs to fetch (default 150, at most 1000)")
    fetch.add_argument("--workflow", help="only this workflow: its name, file name or ID")
    fetch.add_argument("--branch", help="only runs on this branch")
    fetch.add_argument("--events", default=DEFAULT_EVENTS, help=f"comma-separated events, or 'all' (default {DEFAULT_EVENTS})")
    fetch.add_argument("--logs", type=int, default=10, help="slowest jobs to fetch two logs each for (default 10)")

    summarize = commands.add_parser("summarize", help="split job time and print the tables")
    summarize.add_argument("dir", help="the folder fetch wrote")
    summarize.add_argument("--top", type=int, default=5, help="slowest jobs to break down by step (default 5)")
    summarize.add_argument("--setup", help="regular expression for extra step names that count as setup")
    summarize.add_argument("--work", help="regular expression for step names that count as work, checked first")

    args = parser.parse_args()
    if args.command == "fetch":
        args.runs = max(1, min(args.runs, 1000))
        args.logs = max(0, args.logs)
        cmd_fetch(args)
    else:
        cmd_summarize(args)


if __name__ == "__main__":
    main()
