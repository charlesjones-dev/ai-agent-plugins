#!/usr/bin/env python3
"""Run the ai-statusline script templates against sample status line payloads.

Run from the repository root:

    python3 scripts/test-statusline.py

The templates are fenced code blocks in
plugins/ai-statusline/skills/statusline-wizard/SKILL.md. This script extracts the Bash
and PowerShell templates, sends each case's JSON on stdin, strips the ANSI colors and
compares the line with the expected text. A case also fails when the script exits
non-zero, writes to stderr, or prints an empty color code (an unset color variable).

The cases cover the rate-limit segment: both windows, no 5-hour window (accounts
without a 5-hour limit), a null window, the weekly window only, no windows, and
malformed windows.

The Bash template runs under /bin/bash and needs jq. The PowerShell template runs only
when pwsh or powershell is on the PATH; otherwise its cases are skipped.

Exits 1 and lists every failure. Standard library only.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIZARD = ROOT / "plugins" / "ai-statusline" / "skills" / "statusline-wizard" / "SKILL.md"

ANSI = re.compile(r"\x1b\[[0-9;]*m")
EMPTY_COLOR = "\x1b[m"
SEP = " · "

RESETS_5H = 1900000000
RESETS_7D = 1900400000
FIVE_HOUR = {"used_percentage": 23.5, "resets_at": RESETS_5H}
SEVEN_DAY = {"used_percentage": 41.2, "resets_at": RESETS_7D}
MISSING = object()

# Segments that don't depend on the clock or on a git checkout, so every run prints the same line
STABLE = {"SHOW_TIME": False, "SHOW_GIT_BRANCH": False}
ONLY_RATE_LIMITS = {name: False for name in (
    "SHOW_MODEL", "SHOW_EFFORT", "SHOW_TOKEN_COUNT", "SHOW_PROGRESS_BAR", "SHOW_DIRECTORY",
    "SHOW_GIT_BRANCH", "SHOW_COST", "SHOW_DURATION", "SHOW_TIME", "SHOW_VERSION")}


def full_line(rate_segment):
    segments = ["Opus 5", "high", "42k/100k ▓▓▓▓░░░░░░ 42%",
                rate_segment, "proj", "5m 23s", "v2.1.300"]
    return SEP.join(s for s in segments if s)


def five_hour(**fields):
    return {"five_hour": fields, "seven_day": SEVEN_DAY}


# (name, rate_limits value or MISSING, expected rate-limit segment or None)
CASES = [
    ("5h present", {"five_hour": FIVE_HOUR, "seven_day": SEVEN_DAY}, "5h:23.5% 7d:41.2%"),
    ("5h present at 0%", {"five_hour": {"used_percentage": 0, "resets_at": RESETS_5H},
                          "seven_day": SEVEN_DAY}, "5h:0% 7d:41.2%"),
    ("5h above 100% is capped", {"five_hour": {"used_percentage": 250, "resets_at": RESETS_5H},
                                 "seven_day": SEVEN_DAY}, "5h:100% 7d:41.2%"),
    ("5h absent", {"seven_day": SEVEN_DAY}, "7d:41.2%"),
    ("5h null", {"five_hour": None, "seven_day": SEVEN_DAY}, "7d:41.2%"),
    ("5h empty object", {"five_hour": {}, "seven_day": SEVEN_DAY}, "7d:41.2%"),
    ("5h empty string", {"five_hour": "", "seven_day": SEVEN_DAY}, "7d:41.2%"),
    ("5h empty array", {"five_hour": [], "seven_day": SEVEN_DAY}, "7d:41.2%"),
    ("5h used_percentage null", five_hour(used_percentage=None, resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage missing", five_hour(resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage numeric string", five_hour(used_percentage="23.5", resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage text", five_hour(used_percentage="n/a", resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage empty string", five_hour(used_percentage="", resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage boolean", five_hour(used_percentage=True, resets_at=RESETS_5H), "7d:41.2%"),
    ("5h used_percentage negative", five_hour(used_percentage=-5, resets_at=RESETS_5H), "7d:41.2%"),
    ("5h resets_at missing", five_hour(used_percentage=0), "7d:41.2%"),
    ("5h resets_at null", five_hour(used_percentage=0, resets_at=None), "7d:41.2%"),
    ("5h resets_at zero", five_hour(used_percentage=0, resets_at=0), "7d:41.2%"),
    ("5h resets_at negative", five_hour(used_percentage=12, resets_at=-1), "7d:41.2%"),
    ("5h resets_at string", five_hour(used_percentage=12, resets_at="2026-11-01T00:00:00Z"), "7d:41.2%"),
    ("weekly only with a gateway spend limit",
     {"seven_day": SEVEN_DAY, "spend_limit": {"used_percentage": 63, "resets_at": RESETS_7D}}, "7d:41.2%"),
    ("5h only, 7d malformed", {"five_hour": FIVE_HOUR, "seven_day": {"used_percentage": "x"}}, "5h:23.5%"),
    ("none: rate_limits absent", MISSING, None),
    ("none: rate_limits null", None, None),
    ("none: rate_limits empty object", {}, None),
    ("none: both windows null", {"five_hour": None, "seven_day": None}, None),
    ("none: both windows malformed", {"five_hour": {"used_percentage": None},
                                      "seven_day": {"used_percentage": 3, "resets_at": None}}, None),
    ("none: gateway spend limit only", {"spend_limit": {"used_percentage": 63, "resets_at": RESETS_7D}}, None),
    ("none: rate_limits is a string", "unlimited", None),
    ("none: rate_limits is an array", [{"five_hour": FIVE_HOUR}], None),
]

# (name, config overrides, rate_limits, expected full line, ANSI-colored substrings to find)
LINE_CASES = [
    ("colors follow the thresholds", STABLE,
     {"five_hour": {"used_percentage": 85, "resets_at": RESETS_5H},
      "seven_day": {"used_percentage": 55, "resets_at": RESETS_7D}},
     full_line("5h:85% 7d:55%"), ["\x1b[31m5h:85%", "\x1b[33m7d:55%"]),
    ("SHOW_RATE_LIMITS=false hides both windows", {**STABLE, "SHOW_RATE_LIMITS": False},
     {"five_hour": FIVE_HOUR, "seven_day": SEVEN_DAY}, full_line(None), []),
    ("rate limits alone: weekly only", ONLY_RATE_LIMITS, {"seven_day": SEVEN_DAY}, "7d:41.2%", []),
    ("rate limits alone: none", ONLY_RATE_LIMITS, {"five_hour": None}, "", []),
]


def extract(lang, heading):
    text = WIZARD.read_text(encoding="utf-8")
    start = text.index(heading)
    match = re.compile(rf"^```{lang}\n(.*?)^```$", re.S | re.M).search(text, start)
    if not match:
        sys.exit(f"{WIZARD}: no ```{lang} block after {heading!r}")
    return match.group(1)


def configure(script, lang, overrides):
    for name, value in overrides.items():
        if lang == "bash":
            pattern, line = rf"^{name}=\S+", f"{name}={'true' if value else 'false'}"
        else:
            pattern, line = rf"^\${name} = \S+", f"${name} = ${'true' if value else 'false'}"
        script, count = re.subn(pattern, lambda _: line, script, count=1, flags=re.M)
        if count != 1:
            sys.exit(f"{WIZARD}: the {lang} template has no {name} setting")
    return script


def payload(workdir, rate_limits):
    data = {
        "session_id": "test-session",
        "model": {"display_name": "Opus 5"},
        "effort": {"level": "high"},
        "workspace": {"current_dir": str(workdir), "project_dir": str(workdir)},
        "version": "2.1.300",
        "cost": {"total_cost_usd": 1.5, "total_duration_ms": 323000},
        "context_window": {
            "context_window_size": 100000,
            "used_percentage": 42,
            "current_usage": {"input_tokens": 42000, "cache_creation_input_tokens": 0,
                              "cache_read_input_tokens": 0},
        },
    }
    if rate_limits is not MISSING:
        data["rate_limits"] = rate_limits
    return json.dumps(data)


def runners():
    bash = "/bin/bash" if Path("/bin/bash").exists() else shutil.which("bash")
    found = [("bash", "### Bash Script Template", [bash])]
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if pwsh:
        # Execution policy applies only on Windows
        policy = ["-ExecutionPolicy", "Bypass"] if os.name == "nt" else []
        found.append(("powershell", "### PowerShell Script Template",
                      [pwsh, "-NoProfile", "-NonInteractive", *policy, "-File"]))
    return found


def main():
    if not shutil.which("jq"):
        sys.exit("jq is required to run the Bash template")

    failures = []
    total = 0
    langs = runners()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        workdir = tmp / "proj"
        workdir.mkdir()
        env = {**os.environ, "HOME": str(tmp), "USERPROFILE": str(tmp)}
        env.pop("CLAUDE_CONFIG_DIR", None)

        for lang, heading, command in langs:
            template = extract(lang, heading)
            suffix = ".sh" if lang == "bash" else ".ps1"
            jobs = [(name, STABLE, rate_limits, full_line(segment), [])
                    for name, rate_limits, segment in CASES] + LINE_CASES

            scripts = {}
            for name, overrides, rate_limits, expected, colors in jobs:
                total += 1
                key = tuple(sorted(overrides.items()))
                if key not in scripts:
                    path = tmp / f"statusline-{len(scripts)}{suffix}"
                    path.write_text(configure(template, lang, overrides), encoding="utf-8")
                    scripts[key] = path
                result = subprocess.run(command + [str(scripts[key])], input=payload(workdir, rate_limits),
                                        capture_output=True, text=True, encoding="utf-8", env=env,
                                        cwd=workdir, timeout=60)
                actual = ANSI.sub("", result.stdout)
                problems = []
                if result.returncode != 0:
                    problems.append(f"exit code {result.returncode}")
                if result.stderr.strip():
                    problems.append(f"stderr: {result.stderr.strip()}")
                if actual != expected:
                    problems.append(f"expected {expected!r}\n      got      {actual!r}")
                if EMPTY_COLOR in result.stdout:
                    problems.append("printed an empty color code")
                for colored in colors:
                    if colored not in result.stdout:
                        problems.append(f"missing colored text {colored!r}")
                if problems:
                    failures.append(f"[{lang}] {name}: " + "\n    ".join(problems))

    for lang, *_ in langs:
        print(f"{lang}: ran {len(CASES) + len(LINE_CASES)} cases")
    if len(langs) == 1:
        print("powershell: skipped, because neither pwsh nor powershell is on the PATH")
    if failures:
        print(f"\n{len(failures)} of {total} cases failed:\n")
        for failure in failures:
            print(f"  {failure}")
        sys.exit(1)
    print(f"All {total} cases passed.")


if __name__ == "__main__":
    main()
