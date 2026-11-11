#!/usr/bin/env python3
"""Check ai-rules' section library and its rules.py helper.

Run from the repository root:

    python3 scripts/test-rules-library.py

Checks:
- catalog.json is well formed: unique IDs, known groups, a template file for every
  released version, and a sha256 that still matches each released template. Released
  templates must never change, because /rules-setup renders the installed version to
  tell whether the user edited a section.
- Every template renders with every combination of modules, yes/no options and text
  options that may be empty, with no tags left over, no unknown names, no heading
  without text under it and the section heading first.
- `status` reports current, edited, upgrade, edited-upgrade, kept, newer, unknown,
  duplicate, unmanaged and legacy blocks correctly, using a copy of the library with a
  fake newer version that adds a module and an option.

Exits 1 and lists every problem when a check fails. Standard library only.
"""

import importlib.util
import itertools
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "ai-rules" / "skills" / "rules-setup"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

spec = importlib.util.spec_from_file_location("rules", SKILL / "scripts" / "rules.py")
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)

problems = []


def problem(msg):
    problems.append(msg)


def check_catalog(catalog):
    groups = {g["id"] for g in catalog["groups"]}
    ids = [s["id"] for s in catalog["sections"]]
    if len(ids) != len(set(ids)):
        problem("catalog.json: section IDs repeat")
    headings = [s["heading"] for s in catalog["sections"]]
    if len(headings) != len(set(headings)):
        problem("catalog.json: section headings repeat")
    for gid in groups:
        size = sum(1 for sec in catalog["sections"] if sec.get("group") == gid)
        if not 1 <= size <= 4:
            problem(f"catalog.json: group '{gid}' has {size} sections. A wizard question holds 1 to 4 options")
    for sec in catalog["sections"]:
        sid = sec["id"]
        if sec.get("group") not in groups:
            problem(f"{sid}: group '{sec.get('group')}' isn't in groups")
        for req in sec.get("requires", []):
            if req not in ids:
                problem(f"{sid}: requires unknown section '{req}'")
        versions = [v["version"] for v in sec["versions"]]
        if not all(SEMVER.match(v) for v in versions):
            problem(f"{sid}: versions must be x.y.z")
            continue
        if versions != sorted(versions, key=rules.vkey):
            problem(f"{sid}: list versions oldest first")
        if sec["current"] != versions[-1]:
            problem(f"{sid}: current must be the last version listed")
        for v in sec["versions"]:
            if not v.get("changes"):
                problem(f"{sid} {v['version']}: needs a changes note")
            path = SKILL / "library" / sid / f"{v['version']}.md"
            if not path.exists():
                problem(f"{sid} {v['version']}: no template at {path.relative_to(ROOT)}")
                continue
            actual = rules.template_hash(sid, v["version"])
            if v.get("sha256") != actual:
                problem(f"{sid} {v['version']}: sha256 in catalog.json doesn't match the template. "
                        f"Released templates must not change: add a new version instead. "
                        f"For a new version, set sha256 to {actual}")
        extra = {p.stem for p in (SKILL / "library" / sid).glob("*.md")} - set(versions)
        if extra:
            problem(f"{sid}: template files not listed in catalog.json: {sorted(extra)}")
        option_ids = {o["id"] for o in sec.get("options", [])}
        module_ids = [m["id"] for m in sec.get("modules", [])]
        if len(module_ids) != len(set(module_ids)) or set(module_ids) & option_ids:
            problem(f"{sid}: module and option IDs must be unique")
        for m in sec.get("modules", []):
            for req in m.get("requires", []):
                if req not in option_ids:
                    problem(f"{sid}: module '{m['id']}' requires unknown option '{req}'")
            if rules.vkey(m.get("since", "1.0.0")) > rules.vkey(sec["current"]):
                problem(f"{sid}: module '{m['id']}' has a since later than current")
        for o in sec.get("options", []):
            if o.get("kind") not in ("yes-no", "text"):
                problem(f"{sid}: option '{o['id']}' kind must be yes-no or text")
            if not isinstance(o.get("default"), str):
                problem(f"{sid}: option '{o['id']}' needs a default: a value, \"\" or \"detect\"")
            if rules.vkey(o.get("since", "1.0.0")) > rules.vkey(sec["current"]):
                problem(f"{sid}: option '{o['id']}' has a since later than current")
    legacy = catalog.get("legacy", {})
    if legacy and legacy.get("section") not in ids:
        problem("catalog.json: legacy.section isn't a section")


def empty_headings(body):
    """Subheadings with nothing under them: the next line is the end of the section, or a
    heading of the same level or higher. The section's own heading is left out, because a
    section whose text is all modules is only a heading when every module is off."""
    lines = [line for line in body.split("\n") if line.strip()]
    fenced = rules.fenced_lines(lines)
    level = lambda n: len(re.match(r"^(#{1,6}) ", lines[n]).group(1)) if (
        n < len(lines) and n not in fenced and re.match(r"^#{1,6} ", lines[n])) else 0
    found = []
    for n in range(1, len(lines)):
        if not level(n):
            continue
        ended = n + 1 >= len(lines) or lines[n + 1].startswith("<!-- ai-rules:end ")
        if ended or 0 < level(n + 1) <= level(n):
            found.append(lines[n])
    return found


def check_renders(catalog):
    for sec in catalog["sections"]:
        sid = sec["id"]
        for v in sec["versions"]:
            # Only the modules and options that this version has.
            has = lambda item: not rules.added_after(item, v["version"])
            modules = [m["id"] for m in sec.get("modules", []) if has(m)]
            options = [o for o in sec.get("options", []) if has(o)]
            # A yes/no option is on or off. A text option whose default is "" may be empty.
            choices = [["yes", "no"] if o["kind"] == "yes-no"
                       else ["Sample Value", ""] if o["default"] == "" else ["Sample Value"]
                       for o in options]
            for mods in itertools.chain.from_iterable(
                    itertools.combinations(modules, n) for n in range(len(modules) + 1)):
                for values in itertools.product(*choices):
                    opts = dict(zip([o["id"] for o in options], values))
                    label = f"{sid} {v['version']} modules={','.join(mods)} {opts}"
                    try:
                        out = rules.render(catalog, sid, v["version"], mods, opts, markers=True)
                    except rules.RulesError as e:
                        problem(f"{label}: {e}")
                        continue
                    body = out.split("\n", 1)[1]
                    if "{{" in out or "}}" in out:
                        problem(f"{label}: tags left in the output")
                    if "\n\n\n" in out:
                        problem(f"{label}: more than one blank line in a row")
                    if not body.startswith(sec["heading"] + "\n"):
                        problem(f"{label}: output doesn't start with {sec['heading']}")
                    for heading in empty_headings(body):
                        problem(f"{label}: nothing under the heading '{heading}'")
                    for line in body.split("\n"):
                        if re.search(r"\S {2,}\S", line) or re.search(r" [.,]", line):
                            problem(f"{label}: stray spaces in '{line[:60]}'")


def full_block(catalog, sid, version=None, **opts):
    """A block with every module and option that the version has."""
    sec = rules.section(catalog, sid)
    version = version or sec["current"]
    defaults = {o["id"]: ("yes" if o["kind"] == "yes-no" else "Sample Value")
                for o in sec.get("options", []) if not rules.added_after(o, version)}
    defaults.update(opts)
    mods = [m["id"] for m in sec.get("modules", []) if not rules.added_after(m, version)]
    return rules.render(catalog, sid, version, mods, defaults, markers=True)


def check_status():
    with tempfile.TemporaryDirectory() as tmp:
        lib = Path(tmp) / "library"
        shutil.copytree(SKILL / "library", lib)
        rules.LIBRARY, rules.CATALOG = lib, lib / "catalog.json"
        try:
            catalog = rules.load_catalog()
            sec = rules.section(catalog, "estimates")
            # A fake 1.1.0 with one changed line, a new module and a new option with no default.
            old = rules.read_template("estimates", "1.0.0")
            new = old.replace("Quote implementation work in minutes", "Quote implementation work only in minutes")
            new += "{{#extra}}\n\n### Extra\n\n- A new rule.\n{{/extra}}\n{{#flag}}\n- A rule for the flag.\n{{/flag}}\n"
            (lib / "estimates" / "1.1.0.md").write_text(new, encoding="utf-8")
            sec["versions"].append({"version": "1.1.0", "date": "2026-12-01", "changes": "Test.", "sha256": ""})
            sec["current"] = "1.1.0"
            sec["modules"].append({"id": "extra", "title": "Extra", "summary": "x", "default": True,
                                   "requires": [], "since": "1.1.0"})
            sec["options"].append({"id": "flag", "title": "Flag", "kind": "yes-no", "default": "detect",
                                   "prompt": "x", "since": "1.1.0"})
            rules.CATALOG.write_text(json.dumps(catalog), encoding="utf-8")
            catalog = rules.load_catalog()

            v100 = full_block(catalog, "estimates", "1.0.0")
            edited = v100.replace("Never quote a human-developer estimate", "Never ever quote a human-developer estimate")
            kept = edited.replace(" -->\n", ' skip="1.1.0" -->\n', 1)
            newer = full_block(catalog, "plain-wording").replace("v=1.0.0", "v=9.0.0")
            unknown = "<!-- ai-rules:begin id=gone v=1.0.0 modules=\"\" -->\n## Gone\n<!-- ai-rules:end id=gone -->\n"
            legacy = ("## PR and Commit Hygiene\n\n<!-- workflow-rules:id=short-pr-bodies -->\n### Keep PR bodies short\n\n"
                      "- Keep PR bodies short.\n<!-- /workflow-rules:id=short-pr-bodies -->\n\n"
                      "<!-- workflow-rules:id=no-internal-narration -->\n### Don't narrate\n\n- x\n"
                      "<!-- /workflow-rules:id=no-internal-narration -->\n")
            cases = [
                ("current", full_block(catalog, "reply-format", timezone="US Eastern"), "reply-format", "current"),
                ("current with CRLF and extra blank lines",
                 full_block(catalog, "claude-in-chrome").replace("\n- ", "\n\n- ").replace("\n", "\r\n"),
                 "claude-in-chrome", "current"),
                ("upgrade", v100, "estimates", "upgrade"),
                ("edited-upgrade", edited, "estimates", "edited-upgrade"),
                ("kept", kept, "estimates", "kept"),
                ("newer", newer, "plain-wording", "newer"),
                ("unknown", unknown, "gone", "unknown"),
            ]
            for label, text, sid, state in cases:
                path = Path(tmp) / "CLAUDE.md"
                path.write_text("# Notes\n\nMy own rule.\n\n" + text + "\n## Mine\n\nMore text.\n", encoding="utf-8",
                                newline="")
                result = rules.status(catalog, path)
                block = next((b for b in result["blocks"] if b["id"] == sid), None)
                if not block or block["state"] != state:
                    problem(f"status {label}: expected {state}, got {block and block['state']}")
                if state in ("upgrade", "edited-upgrade"):
                    if (block.get("new_modules") != ["extra"] or block.get("new_options") != ["flag"]
                            or [c["version"] for c in block.get("changes", [])] != ["1.1.0"]):
                        problem(f"status {label}: wrong changes, new_modules or new_options: {block}")

            edited_current = full_block(catalog, "ios-simulators").replace("Don't delete a simulator", "Never delete a simulator")
            path = Path(tmp) / "CLAUDE.md"
            path.write_text(edited_current + "\n" + full_block(catalog, "ios-simulators") + "\n## Plain wording\n\nx\n\n"
                            + legacy, encoding="utf-8")
            result = rules.status(catalog, path)
            states = [b["state"] for b in result["blocks"]]
            if states != ["edited", "duplicate"]:
                problem(f"status edited/duplicate: got {states}")
            if not result["problems"]:
                problem("status duplicate: expected a problem")
            if {u["id"] for u in result["unmanaged"]} != {"plain-wording", "pr-hygiene"}:
                problem(f"status unmanaged: got {result['unmanaged']}")
            legacy_ids = {(entry["id"], entry.get("retired", False)) for entry in result["legacy"]}
            if legacy_ids != {("short-pr-bodies", False), ("no-internal-narration", True)}:
                problem(f"status legacy: got {result['legacy']}")

            fenced = ("## Estimates\n\nText.\n\n~~~markdown\n## Not a heading\n"
                      "<!-- ai-rules:begin id=plain-wording v=1.0.0 modules=\"\" -->\n~~~\n\nMore.\n\n## Mine\n")
            path.write_text(fenced, encoding="utf-8")
            result = rules.status(catalog, path)
            if result["blocks"] or result["problems"] or [(u["id"], u["line"], u["end_line"]) for u in result["unmanaged"]] != [("estimates", 1, 10)]:
                problem(f"status fenced code: headings and markers inside fences must be ignored, got {result}")

            path.write_text("<!-- ai-rules:begin id=estimates v=1.0.0 modules=\"\" -->\n## Estimates\n", encoding="utf-8")
            if not rules.status(catalog, path)["problems"]:
                problem("status: a begin marker without an end marker must be a problem")
        finally:
            rules.LIBRARY = SKILL / "library"
            rules.CATALOG = rules.LIBRARY / "catalog.json"


def main():
    catalog = rules.load_catalog()
    check_catalog(catalog)
    check_renders(catalog)
    check_status()
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"- {p}")
        sys.exit(1)
    print(f"OK: {len(catalog['sections'])} sections, every render and status case passed")


if __name__ == "__main__":
    main()
