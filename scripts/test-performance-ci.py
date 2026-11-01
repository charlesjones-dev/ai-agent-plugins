#!/usr/bin/env python3
"""Run ai-performance's ci_timings.py against a fake gh and sample CI data.

Run from the repository root:

    python3 scripts/test-performance-ci.py

The script is plugins/ai-performance/skills/performance-ci/scripts/ci_timings.py. The test
puts a fake `gh` first on PATH. It answers from a generated repository with two
workflows, 120 completed runs (20 of them scheduled), four jobs per CI run and one per
lint run, and a log for each job. The fake records every call.

The cases cover fetch (paging, the event filter, stopping at --runs, the workflow
filter, GET-only calls, the retry for gh versions without --allow-escape-sequences, the
log sample) and summarize (queue, setup and work per job, medians and p90s, failed and
skipped jobs, step classification and its overrides, cleanup steps and a step the
workflow names "Post comment", timestamps with offsets and fractions, time per commit,
machine wait by runner, rounded-up runner minutes, matrix jobs, cache and test-runner
log lines).

Exits 1 and lists every failure. Standard library only.
"""

import json
import os
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "ai-performance" / "skills" / "performance-ci" / "scripts" / "ci_timings.py"
BASE = datetime(2026, 10, 1, tzinfo=timezone.utc)
LONG_QUEUE = {1, 3, 5, 7, 9, 11}  # lint commits that wait 900 s for a runner

FAKE_GH = r'''
import json, os, sys
from urllib.parse import urlsplit, parse_qs

args = sys.argv[1:]
with open(os.environ["FAKE_GH_CALLS"], "a") as calls:
    calls.write(json.dumps(args) + "\n")
world = json.load(open(os.environ["FAKE_GH_WORLD"]))

if args[:2] == ["repo", "view"]:
    print(json.dumps({"nameWithOwner": "acme/widgets", "visibility": "PRIVATE", "defaultBranchRef": {"name": "main"}}))
    sys.exit(0)
if args[0] != "api":
    sys.exit("fake gh: unexpected command")
if "--allow-escape-sequences" in args and os.environ.get("FAKE_GH_OLD"):
    sys.stderr.write("unknown flag: --allow-escape-sequences\n")
    sys.exit(1)

url = urlsplit(args[-1])
query = {key: values[0] for key, values in parse_qs(url.query).items()}
parts = url.path.split("/")
page, per_page = int(query.get("page", 1)), int(query.get("per_page", 30))

def paged(items):
    return items[(page - 1) * per_page: page * per_page]

if url.path == "repos/acme/widgets/actions/workflows":
    print(json.dumps({"workflows": paged(world["workflows"])}))
elif url.path == "repos/acme/widgets/actions/runs" or (len(parts) == 7 and parts[4] == "workflows" and parts[6] == "runs"):
    runs = world["runs"]
    if parts[4] == "workflows":
        runs = [run for run in runs if str(run["workflow_id"]) == parts[5]]
    print(json.dumps({"workflow_runs": paged(runs)}))
elif len(parts) == 7 and parts[4] == "runs" and parts[6] == "jobs":
    print(json.dumps({"jobs": paged(world["jobs"][parts[5]])}))
elif len(parts) == 7 and parts[4] == "jobs" and parts[6] == "logs":
    sys.stdout.write(world["logs"][parts[5]])
else:
    sys.exit(f"fake gh: unknown path {url.path}")
'''


def utc(seconds):
    return (BASE + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def local(seconds):
    # Step times in the style some older runs use: a UTC offset and milliseconds.
    zone = timezone(timedelta(hours=-7))
    return (BASE + timedelta(seconds=seconds)).astimezone(zone).strftime("%Y-%m-%dT%H:%M:%S.000-07:00")


def steps(start, spans, stamp):
    out, t = [], start
    for number, (name, seconds) in enumerate(spans, 1):
        out.append({"number": number, "name": name, "status": "completed", "conclusion": "success",
                    "started_at": stamp(t), "completed_at": stamp(t + seconds)})
        t += seconds
    return out


def job(job_id, run_id, name, created, started, completed, labels, step_list, conclusion="success", group="GitHub Actions"):
    return {"id": job_id, "run_id": run_id, "run_attempt": 1, "name": name, "status": "completed",
            "conclusion": conclusion, "created_at": utc(created), "started_at": utc(started),
            "completed_at": utc(completed), "labels": labels, "runner_name": "runner", "runner_group_name": group,
            "steps": step_list, "html_url": "https://example.invalid/ignored"}


def world():
    workflows = [{"id": 11, "name": "CI", "path": ".github/workflows/ci.yml", "state": "active"},
                 {"id": 12, "name": "Lint", "path": ".github/workflows/lint.yml", "state": "active"}]
    runs, jobs, logs = [], {}, {}
    for i in range(1, 121):
        k = (i + 1) // 2
        ci = i % 2 == 1
        run_id = 1000 + i
        created = k * 3600 + (0 if ci else 2)
        event = "schedule" if k % 6 == 0 else ("pull_request" if k % 2 == 1 else "push")
        runs.append({"id": run_id, "name": "CI" if ci else "Lint", "workflow_id": 11 if ci else 12,
                     "path": ".github/workflows/ci.yml" if ci else ".github/workflows/lint.yml", "event": event,
                     "status": "completed", "conclusion": "failure" if i == 3 else "success",
                     "head_branch": "main", "head_sha": f"{k:040x}", "run_attempt": 2 if i == 5 else 1,
                     "run_number": i, "created_at": utc(created), "run_started_at": utc(created),
                     "updated_at": utc(created + 999), "display_title": "ignored"})
        c = created
        if ci:
            build = job(run_id * 10 + 1, run_id, "build", c + 1, c + 5, c + 67, ["ubuntu-latest"], steps(c + 5, [
                ("Set up job", 2), ("Run actions/checkout@v4", 3), ("Setup Node", 5), ("Run npm ci", 20),
                ("Run npm run build", 30), ("Post Run actions/checkout@v4", 1), ("Complete job", 0)], local))
            shards = []
            for shard, test_seconds in ((1, 60), (2, 30)):
                end = c + 77 + 2 + 3 + 20 + test_seconds + 2 + 1
                shards.append(job(run_id * 10 + 1 + shard, run_id, f"test ({shard}, 2)", c + 67, c + 77, end,
                                  ["ubuntu-latest"], steps(c + 77, [
                                      ("Set up job", 2), ("Run actions/checkout@v4", 3), ("Run npm ci", 20),
                                      (f"Run npm test -- --shard={shard}/2", test_seconds), ("Post comment", 2),
                                      ("Post Run actions/checkout@v4", 1), ("Complete job", 0)], utc),
                                  conclusion="failure" if (i == 3 and shard == 1) else "success"))
            skipped = job(run_id * 10 + 4, run_id, "deploy-preview", c + 67, c + 67, c + 67, ["ubuntu-latest"], [],
                          conclusion="skipped")
            jobs[str(run_id)] = [build, *shards, skipped]
            logs[str(build["id"])] = ("2026-10-01T00:00:01.0000000Z Cache restored from key: npm-linux-abc\n"
                                      "2026-10-01T00:00:02.0000000Z Cache saved successfully\n")
            for shard in shards:
                logs[str(shard["id"])] = ("﻿2026-10-01T00:00:01.0000000Z \x1b[2m Duration \x1b[22m 12.34s "
                                          "(transform 1.2s, setup 4.1s, collect 5.0s, tests 2.0s)\n")
        else:
            queue = 900 if k in LONG_QUEUE else 120
            start = c + 1 + queue
            lint = job(run_id * 10 + 1, run_id, "lint", c + 1, start, start + 47, ["self-hosted", "linux"], steps(start, [
                ("Set up job", 1), ("Checkout", 2), ("Restore cache", 4), ("Run npx eslint .", 40)], utc), group="Default")
            jobs[str(run_id)] = [lint]
            logs[str(lint["id"])] = "2026-10-01T00:00:01.0000000Z Cache not found for input keys: eslint-linux-abc\n"
    runs.sort(key=lambda run: run["id"], reverse=True)  # newest first, as the API returns them
    return {"workflows": workflows, "runs": runs, "jobs": jobs, "logs": logs}


def main():
    failures, total = [], 0

    def check(name, condition, detail=""):
        nonlocal total
        total += 1
        if not condition:
            failures.append(f"{name}: {detail}"[:600] if detail else name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "gh"
        fake.write_text(f"#!{sys.executable}\n{FAKE_GH}", encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        (tmp / "world.json").write_text(json.dumps(world()), encoding="utf-8")
        calls = tmp / "calls.jsonl"

        def run(*args, old_gh=False):
            calls.write_text("", encoding="utf-8")
            env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                       FAKE_GH_WORLD=str(tmp / "world.json"), FAKE_GH_CALLS=str(calls))
            env.pop("FAKE_GH_OLD", None)
            if old_gh:
                env["FAKE_GH_OLD"] = "1"
            return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, env=env)

        def logged():
            return [json.loads(line) for line in calls.read_text(encoding="utf-8").splitlines()]

        # fetch: stops at --runs on the second page and skips scheduled runs
        out = tmp / "ninety"
        r = run("fetch", "--out", str(out), "--runs", "90", "--logs", "0")
        check("fetch 90: exit code", r.returncode == 0, r.stderr)
        meta = json.loads((out / "meta.json").read_text()) if r.returncode == 0 else {}
        runs = json.loads((out / "runs.json").read_text()) if r.returncode == 0 else []
        check("fetch 90: 90 runs", len(runs) == 90, str(len(runs)))
        check("fetch 90: no scheduled runs", all(run["event"] != "schedule" for run in runs))
        check("fetch 90: 18 scheduled runs skipped", meta.get("runs_skipped_by_event") == {"schedule": 18},
              str(meta.get("runs_skipped_by_event")))
        run_pages = [c[-1] for c in logged() if c[0] == "api" and "/actions/runs?" in c[-1]]
        check("fetch 90: read two pages of runs", len(run_pages) == 2 and "page=2" in run_pages[1], str(run_pages))
        check("fetch 90: completed runs only", all("status=completed" in p for p in run_pages), str(run_pages))
        check("fetch 90: slim run fields", runs and "display_title" not in runs[0] and "head_sha" in runs[0])
        check("fetch 90: meta", meta.get("repo") == "acme/widgets" and meta.get("visibility") == "PRIVATE"
              and meta.get("default_branch") == "main", str(meta)[:300])

        # fetch: the default sample, logs, and a gh without --allow-escape-sequences
        out = tmp / "all"
        r = run("fetch", "--out", str(out), old_gh=True)
        check("fetch: exit code", r.returncode == 0, r.stderr)
        runs = json.loads((out / "runs.json").read_text()) if r.returncode == 0 else []
        meta = json.loads((out / "meta.json").read_text()) if r.returncode == 0 else {}
        check("fetch: 100 runs", len(runs) == 100, str(len(runs)))
        check("fetch: jobs saved", len(list((out / "jobs").glob("*.json"))) == 100)
        saved_job = json.loads((out / "jobs" / "1001.json").read_text())[0] if (out / "jobs" / "1001.json").exists() else {}
        check("fetch: slim job fields", "html_url" not in saved_job and saved_job.get("steps"), str(saved_job)[:200])
        check("fetch: 8 logs, two for each of four jobs", meta.get("logs") == 8 and len(list((out / "logs").glob("*.log"))) == 8,
              str(meta.get("logs")))
        # Runs 1119 and 1120 are scheduled, so the newest kept runs are 1117 (CI) and 1118 (Lint).
        check("fetch: newest logs", (out / "logs" / "11171.log").exists() and (out / "logs" / "11181.log").exists(),
              str(sorted(p.name for p in (out / "logs").glob("*.log"))))
        api_calls = [c for c in logged() if c[0] == "api"]
        check("fetch: every API call is a GET", api_calls and all(c[1:3] == ["-X", "GET"] for c in api_calls))
        log_calls = [c for c in api_calls if c[-1].endswith("/logs")]
        check("fetch: retries logs without --allow-escape-sequences",
              any("--allow-escape-sequences" in c for c in log_calls) and sum("--allow-escape-sequences" not in c for c in log_calls) == 8,
              str(log_calls[:3]))
        check("fetch: no errors", meta.get("errors") == [], str(meta.get("errors")))

        # fetch: one workflow by file name, and a workflow that doesn't exist
        r = run("fetch", "--out", str(tmp / "lint"), "--workflow", "lint.yml", "--runs", "5", "--logs", "0")
        lint_runs = json.loads((tmp / "lint" / "runs.json").read_text()) if r.returncode == 0 else []
        check("fetch --workflow: lint runs only", len(lint_runs) == 5 and all(run["name"] == "Lint" for run in lint_runs),
              r.stderr + str(lint_runs[:1]))
        check("fetch --workflow: uses the workflow's runs", any("actions/workflows/12/runs?" in c[-1] for c in logged()))
        r = run("fetch", "--out", str(tmp / "none"), "--workflow", "deploy.yml")
        check("fetch --workflow: unknown workflow", r.returncode == 2 and "no workflow matches" in r.stderr
              and "lint.yml" in r.stderr, r.stderr)

        # summarize
        r = run("summarize", str(out))
        check("summarize: exit code", r.returncode == 0, r.stderr)
        s = json.loads((out / "summary.json").read_text()) if r.returncode == 0 else {"jobs": []}
        jobs = {job["key"]: job for job in s["jobs"]}
        check("summarize: four jobs", sorted(jobs) == ["CI / build", "CI / test (1, 2)", "CI / test (2, 2)", "Lint / lint"],
              str(sorted(jobs)))
        check("summarize: slowest first", [job["key"] for job in s["jobs"]] ==
              ["Lint / lint", "CI / test (1, 2)", "CI / test (2, 2)", "CI / build"], str([job["key"] for job in s["jobs"]]))
        build = jobs.get("CI / build", {})
        check("summarize: build split", (build.get("queue", {}).get("median"), build.get("setup", {}).get("median"),
                                         build.get("work", {}).get("median"), build.get("total", {}).get("median")) == (4, 32, 30, 66),
              str({k: build.get(k) for k in ("queue", "setup", "work", "total")}))
        test1 = jobs.get("CI / test (1, 2)", {})
        check("summarize: test shard split counts Post comment as work",
              (test1.get("queue", {}).get("median"), test1.get("setup", {}).get("median"), test1.get("work", {}).get("median"))
              == (10, 26, 62), str({k: test1.get(k) for k in ("queue", "setup", "work")}))
        check("summarize: failed job counted, not timed", test1.get("runs") == 49 and test1.get("failures") == 1,
              f"{test1.get('runs')} {test1.get('failures')}")
        lint = jobs.get("Lint / lint", {})
        check("summarize: lint queue median and p90", (lint.get("queue", {}).get("median"), lint.get("queue", {}).get("p90"),
                                                       lint.get("total", {}).get("median"), lint.get("total", {}).get("p90"))
              == (120, 900, 167, 947), str({k: lint.get(k) for k in ("queue", "total")}))
        check("summarize: lint setup", (lint.get("setup", {}).get("median"), lint.get("work", {}).get("median")) == (7, 40))
        check("summarize: runner and group", lint.get("runner") == "self-hosted,linux" and lint.get("runner_group") == "Default")
        check("summarize: conclusions", s.get("sample", {}).get("jobs") == {"success": 199, "failure": 1, "skipped": 50},
              str(s.get("sample", {}).get("jobs")))
        parts = {step["name"]: step["part"] for job in s["jobs"] for step in job.get("steps", [])}
        expected = {"Set up job": "setup", "Run actions/checkout@v4": "setup", "Setup Node": "setup", "Run npm ci": "setup",
                    "Run npm run build": "work", "Post Run actions/checkout@v4": "setup", "Post comment": "work",
                    "Checkout": "setup", "Restore cache": "setup", "Run npx eslint .": "work",
                    "Run npm test -- --shard=1/2": "work"}
        check("summarize: step classification", all(parts.get(name) == part for name, part in expected.items()),
              str({name: parts.get(name) for name in expected}))
        build_steps = [step["name"] for step in build.get("steps", [])]
        check("summarize: steps in run order", build_steps[:3] == ["Set up job", "Run actions/checkout@v4", "Setup Node"],
              str(build_steps))
        npm_build = next((step for step in build.get("steps", []) if step["name"] == "Run npm run build"), {})
        check("summarize: step times across offsets", npm_build.get("median") == 30, str(npm_build))

        commits = {row["trigger"]: row for row in s.get("per_commit", [])}
        pr = commits.get("pull request", {})
        check("summarize: pull request commits", (pr.get("commits"), pr.get("median"), pr.get("p90"), pr.get("max"))
              == (29, 170, 950, 950), str(pr))
        check("summarize: finishes last", pr.get("finishes_last") == "Lint / lint" and pr.get("finishes_last_share") == 100,
              str(pr))
        push = commits.get("push", {})
        check("summarize: push commits skip the failed run", (push.get("commits"), push.get("median")) == (19, 170), str(push))
        check("summarize: no merge queue row", "merge queue" not in commits)
        delays = {row["workflow"]: row for row in s.get("start_delay", [])}
        check("summarize: start delay", delays.get("CI (.github/workflows/ci.yml)", {}).get("median") == 1
              and delays.get("Lint (.github/workflows/lint.yml)", {}).get("runs") == 50, str(delays))
        check("summarize: no doubled triggers", s.get("duplicate_triggers") == [], str(s.get("duplicate_triggers")))

        queues = {row["runner"]: row for row in s.get("queue_by_runner", [])}
        check("summarize: queue by runner", (queues.get("self-hosted,linux", {}).get("jobs"), queues.get("self-hosted,linux", {}).get("p90"),
                                             queues.get("ubuntu-latest", {}).get("jobs"), queues.get("ubuntu-latest", {}).get("median"))
              == (50, 900, 150, 10), str(queues))
        check("summarize: longest wait first", s.get("queue_by_runner", [{}])[0].get("runner") == "self-hosted,linux")
        minutes = {row["runner"]: row for row in s.get("runner_minutes", [])}
        check("summarize: runner minutes", (minutes.get("ubuntu-latest", {}).get("minutes"), minutes.get("ubuntu-latest", {}).get("rounded_up"),
                                            minutes.get("self-hosted,linux", {}).get("rounded_up")) == (173.3, 250, 50), str(minutes))
        matrix = s.get("matrix", [])
        check("summarize: matrix family", len(matrix) == 1 and (matrix[0]["family"], matrix[0]["jobs"], matrix[0]["fastest_work"],
                                                                 matrix[0]["slowest_work"], matrix[0]["slowest_job"])
              == ("CI / test", 2, 32, 62, "test (1, 2)"), str(matrix))

        logs = {}
        for row in s.get("logs", []):
            logs.setdefault(row["job"], row)
        check("summarize: cache hit and save lines", (logs.get("CI / build", {}).get("hits"), logs.get("CI / build", {}).get("saves"))
              == (1, 1), str(logs.get("CI / build")))
        check("summarize: cache miss line", logs.get("Lint / lint", {}).get("misses") == 1
              and logs.get("Lint / lint", {}).get("cache_lines") == ["Cache not found for input keys: eslint-linux-abc"],
              str(logs.get("Lint / lint")))
        check("summarize: test-runner line without escape codes or BOM",
              logs.get("CI / test (1, 2)", {}).get("test_lines") == ["Duration  12.34s (transform 1.2s, setup 4.1s, collect 5.0s, tests 2.0s)"],
              str(logs.get("CI / test (1, 2)")))

        text = r.stdout
        for heading in ("# CI timings: acme/widgets", "## Time to a CI result per commit", "## Slowest jobs (top 4 by median total)",
                        "### 1. Lint / lint", "Workflow file: `.github/workflows/lint.yml`", "## Machine wait by runner",
                        "## Runner minutes in the sample", "## Matrix jobs", "## Cache and test-runner lines in sampled logs",
                        "## Step classification"):
            check(f"summarize: Markdown has {heading!r}", heading in text)

        # summarize: overrides
        r = run("summarize", str(out), "--work", "npm ci", "--setup", "^Post comment$", "--top", "2")
        s = json.loads((out / "summary.json").read_text()) if r.returncode == 0 else {"jobs": []}
        jobs = {job["key"]: job for job in s["jobs"]}
        check("summarize --work: install counted as work", (jobs.get("CI / build", {}).get("work", {}).get("median"),
                                                            jobs.get("CI / build", {}).get("setup", {}).get("median")) == (50, 12),
              str(jobs.get("CI / build", {}).get("work")))
        check("summarize --setup: Post comment counted as setup", jobs.get("CI / test (1, 2)", {}).get("work", {}).get("median") == 80,
              str(jobs.get("CI / test (1, 2)", {}).get("work")))
        check("summarize --top: steps for two jobs only", sum("steps" in job for job in s["jobs"]) == 2)
        check("summarize: overrides listed", "--work 'npm ci'" in r.stdout and "--setup '^Post comment$'" in r.stdout, r.stdout[-300:])

        # summarize: a workflow that runs for both the push and the pull request, after a long delay
        doubled = tmp / "doubled"
        (doubled / "jobs").mkdir(parents=True)
        (doubled / "meta.json").write_text(json.dumps({"repo": "acme/widgets", "visibility": "PUBLIC"}))
        pair = []
        for run_id, event in ((1, "push"), (2, "pull_request")):
            pair.append({"id": run_id, "name": "CI", "path": ".github/workflows/ci.yml", "event": event,
                         "conclusion": "success", "head_sha": "abc", "run_attempt": 1, "created_at": utc(0)})
            (doubled / "jobs" / f"{run_id}.json").write_text(json.dumps([job(run_id * 10, run_id, "test", 300, 302, 362,
                                                                              ["ubuntu-latest"], [])]))
        (doubled / "runs.json").write_text(json.dumps(pair))
        r = run("summarize", str(doubled))
        s = json.loads((doubled / "summary.json").read_text()) if r.returncode == 0 else {}
        check("summarize: doubled triggers", s.get("duplicate_triggers") == [{"workflow": "CI", "commits": 1}],
              r.stderr + str(s.get("duplicate_triggers")))
        check("summarize: long start delay", (s.get("start_delay") or [{}])[0].get("median") == 300, str(s.get("start_delay")))
        check("summarize: no logs folder", r.returncode == 0 and "No logs were fetched." in r.stdout, r.stderr)

        # summarize: a folder without fetch output
        empty = tmp / "empty"
        empty.mkdir()
        r = run("summarize", str(empty))
        check("summarize: missing data", r.returncode == 2 and "doesn't hold fetch output" in r.stderr, r.stderr)

    if failures:
        print(f"{len(failures)} of {total} checks failed:\n")
        for failure in failures:
            print(f"  {failure}")
        sys.exit(1)
    print(f"All {total} checks passed.")


if __name__ == "__main__":
    main()
