#!/usr/bin/env python3
"""Render ai-rules library sections and report what a CLAUDE.md has installed.

Standard library only. Python 3.8 or later. The skill also works without this
script by following the same rules by hand, so keep the two in step: the
rendering rules here are the ones SKILL.md describes under "Rendering".

    python3 rules.py render <section-id> [--version X] [--modules a,b] [--set key=value ...] [--markers]
    python3 rules.py status <path-to-CLAUDE.md>
    python3 rules.py hash <section-id> <version>

`render` prints one section. Options left out take their catalog default. A
default of "detect" has no value until the skill picks one, so pass --set for it.
`status` prints JSON that describes each managed block, each library section
that sits in the file without markers, and each legacy /workflow-rules marker.
`hash` prints the sha256 that catalog.json records for a released version file.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

LIBRARY = Path(__file__).resolve().parent.parent / "library"
CATALOG = LIBRARY / "catalog.json"

TAG = re.compile(r"\{\{([#^/]?)([a-z0-9-]+)\}\}")
STANDALONE = re.compile(r"^[ \t]*(\{\{[#^/][a-z0-9-]+\}\})[ \t]*(?:\n|\Z)", re.M)
BEGIN = re.compile(r"<!--\s*ai-rules:begin\s+(.*?)\s*-->")
END = re.compile(r"<!--\s*ai-rules:end\s+id=([a-z0-9-]+)\s*-->")
ATTR = re.compile(r'([a-z][a-z0-9-]*)=(?:"([^"]*)"|(\S+))')
LEGACY = re.compile(r"<!--\s*workflow-rules:id=([a-z0-9-]+)\s*-->")

TRUE = {"yes", "true", "on", "1"}
FALSE = {"no", "false", "off", "0", ""}


class RulesError(Exception):
    pass


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def section(catalog, sid):
    for s in catalog["sections"]:
        if s["id"] == sid:
            return s
    raise RulesError(f"no section '{sid}' in the library")


def vkey(version):
    return tuple(int(p) for p in version.split("."))


def read_template(sid, version):
    path = LIBRARY / sid / f"{version}.md"
    if not path.exists():
        raise RulesError(f"library has no file for {sid} {version}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def template_hash(sid, version):
    return hashlib.sha256(read_template(sid, version).encode("utf-8")).hexdigest()


def truthy(name, modules, options):
    if name in modules:
        return True
    if name in options:
        value = options[name].strip().lower()
        if value in TRUE:
            return True
        if value in FALSE:
            return False
        return True
    return False


def render_template(text, modules, options, known):
    """Mustache-style sections: {{#x}}..{{/x}} when x is on, {{^x}}..{{/x}} when off, {{x}} for a value."""
    text = text.replace("\r\n", "\n")
    # A line that holds only a section tag disappears with its newline.
    text = STANDALONE.sub(r"\1", text)

    out, stack, pos = [], [], 0
    emitting = lambda: all(stack_item[2] for stack_item in stack)
    for m in TAG.finditer(text):
        if emitting():
            out.append(text[pos:m.start()])
        pos = m.end()
        kind, name = m.groups()
        if name not in known:
            raise RulesError(f"unknown name '{name}' in template")
        if kind in ("#", "^"):
            on = truthy(name, modules, options)
            stack.append((kind, name, on if kind == "#" else not on))
        elif kind == "/":
            if not stack or stack[-1][1] != name:
                raise RulesError(f"'{{{{/{name}}}}}' closes nothing")
            stack.pop()
        elif emitting():
            if name not in options:
                raise RulesError(f"'{{{{{name}}}}}' is not an option with a value")
            out.append(options[name])
    if stack:
        raise RulesError(f"'{{{{{stack[-1][0]}{stack[-1][1]}}}}}' is never closed")
    out.append(text[pos:])
    result = "".join(out)
    result = "\n".join(line.rstrip() for line in result.split("\n"))
    result = re.sub(r"\n{3,}", "\n\n", result).strip("\n")
    return result + "\n"


def resolve(sec, modules, options):
    """Check the modules and options against the catalog and fill in defaults."""
    known_modules = {m["id"]: m for m in sec.get("modules", [])}
    for mid in modules:
        if mid not in known_modules:
            raise RulesError(f"{sec['id']} has no module '{mid}'")
    opts = {}
    for o in sec.get("options", []):
        if o["id"] in options:
            opts[o["id"]] = options[o["id"]]
        elif o["default"] != "detect":
            opts[o["id"]] = o["default"]
        else:
            raise RulesError(f"option '{o['id']}' has no default, pass --set {o['id']}=<value>")
    for key in options:
        if key not in opts:
            raise RulesError(f"{sec['id']} has no option '{key}'")
    # A module that needs an option that is off can't be on.
    active = [m for m in modules
              if all(truthy(r, set(), opts) for r in known_modules[m].get("requires", []))]
    return active, opts


def known_names(sec):
    return {m["id"] for m in sec.get("modules", [])} | {o["id"] for o in sec.get("options", [])}


def render(catalog, sid, version=None, modules=(), options=None, markers=False):
    sec = section(catalog, sid)
    version = version or sec["current"]
    active, opts = resolve(sec, list(modules), dict(options or {}))
    body = render_template(read_template(sid, version), set(active), opts, known_names(sec))
    if not markers:
        return body
    return begin_marker(sec, version, active, opts) + "\n" + body + end_marker(sid) + "\n"


def begin_marker(sec, version, modules, options, skip=None):
    order = [m["id"] for m in sec.get("modules", [])]
    mods = ",".join(m for m in order if m in modules)
    parts = [f"id={sec['id']}", f"v={version}", f'modules="{mods}"']
    for o in sec.get("options", []):
        if o["id"] in options:
            parts.append(f'{o["id"]}="{options[o["id"]]}"')
    if skip:
        parts.append(f'skip="{skip}"')
    return "<!-- ai-rules:begin " + " ".join(parts) + " -->"


def end_marker(sid):
    return f"<!-- ai-rules:end id={sid} -->"


def normalize(text):
    """What counts as the same text: ignore line endings, trailing spaces and blank lines."""
    return [line.rstrip() for line in text.replace("\r\n", "\n").split("\n") if line.strip()]


def fenced_lines(lines):
    """Indexes of lines inside fenced code blocks (``` or ~~~), fence lines included."""
    inside, fence, result = False, "", set()
    for n, line in enumerate(lines):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if not inside and m:
            inside, fence = True, m.group(1)
            result.add(n)
        elif inside:
            result.add(n)
            if line.strip().startswith(fence[0] * len(fence)) and line.strip().strip(fence[0]) == "":
                inside = False
    return result


def status(catalog, path):
    text = Path(path).read_bytes().decode("utf-8-sig")
    lines = text.replace("\r\n", "\n").split("\n")
    by_id = {s["id"]: s for s in catalog["sections"]}
    blocks, seen, problems = [], {}, []
    managed_lines = set()
    fenced = fenced_lines(lines)

    i = 0
    while i < len(lines):
        m = BEGIN.search(lines[i]) if i not in fenced else None
        if not m:
            i += 1
            continue
        attrs = {a.group(1): a.group(2) if a.group(2) is not None else a.group(3)
                 for a in ATTR.finditer(m.group(1))}
        sid = attrs.get("id", "")
        j = i + 1
        while j < len(lines) and not END.search(lines[j]):
            if BEGIN.search(lines[j]):
                break
            j += 1
        if j >= len(lines) or not END.search(lines[j]) or END.search(lines[j]).group(1) != sid:
            problems.append(f"line {i + 1}: begin marker for '{sid}' has no matching end marker")
            i += 1
            continue
        managed_lines.update(range(i, j + 1))
        body = "\n".join(lines[i + 1:j]) + "\n"
        block = {
            "id": sid,
            "version": attrs.get("v"),
            "modules": [x for x in attrs.get("modules", "").split(",") if x],
            "options": {k: v for k, v in attrs.items() if k not in ("id", "v", "modules", "skip")},
            "skip": attrs.get("skip"),
            "begin_line": i + 1,
            "end_line": j + 1,
        }
        if sid in seen:
            block["state"] = "duplicate"
            problems.append(f"line {i + 1}: '{sid}' is installed twice (first at line {seen[sid]})")
        elif sid not in by_id:
            block["state"] = "unknown"
        elif not re.match(r"^\d+\.\d+\.\d+$", block["version"] or ""):
            seen[sid] = i + 1
            block["state"] = "broken"
            problems.append(f"line {i + 1}: '{sid}' has no valid v= version")
        elif vkey(block["version"]) > vkey(by_id[sid]["current"]):
            seen[sid] = i + 1
            block["current"] = by_id[sid]["current"]
            block["state"] = "newer"
        else:
            seen[sid] = i + 1
            sec = by_id[sid]
            block["current"] = sec["current"]
            try:
                expected = render(catalog, sid, block["version"], block["modules"], block["options"])
                edited = normalize(expected) != normalize(body)
            except RulesError as e:
                block["error"] = str(e)
                edited = True
            outdated = vkey(block["version"]) < vkey(sec["current"])
            block["edited"] = edited
            if outdated and block["skip"] and vkey(block["skip"]) >= vkey(sec["current"]):
                block["state"] = "kept"
            elif outdated:
                block["state"] = "edited-upgrade" if edited else "upgrade"
            else:
                block["state"] = "edited" if edited else "current"
            if outdated:
                installed = vkey(block["version"])
                block["changes"] = [v for v in sec["versions"] if vkey(v["version"]) > installed]
                block["new_modules"] = [m["id"] for m in sec.get("modules", [])
                                        if vkey(m.get("since", "1.0.0")) > installed]
        blocks.append(block)
        i = j + 1

    unmanaged = []
    for n, line in enumerate(lines):
        if n in managed_lines or n in fenced:
            continue
        for sec in catalog["sections"]:
            headings = [sec["heading"]] + sec.get("aliases", [])
            if line.strip() in headings and sec["id"] not in seen:
                end = n + 1
                while end < len(lines) and not (
                        end in managed_lines
                        or (end not in fenced and re.match(r"^#{1,2} ", lines[end]))
                        or (end not in fenced and LEGACY.search(lines[end]))):
                    end += 1
                while end > n + 1 and not lines[end - 1].strip():
                    end -= 1
                unmanaged.append({"id": sec["id"], "heading": line.strip(), "line": n + 1, "end_line": end})

    legacy = []
    retired = {r["id"]: r for r in catalog.get("legacy", {}).get("retired", [])}
    for n, line in enumerate(lines):
        m = LEGACY.search(line)
        if m and n not in managed_lines and n not in fenced:
            rid = m.group(1)
            entry = {"id": rid, "line": n + 1}
            if rid in retired:
                entry["retired"] = True
                entry["replacement"] = retired[rid]["replacement"]
            legacy.append(entry)

    installed = {b["id"] for b in blocks}
    available = [s["id"] for s in catalog["sections"]
                 if s["id"] not in installed and s["id"] not in {u["id"] for u in unmanaged}]
    return {
        "file": str(path),
        "line_endings": "crlf" if "\r\n" in text else "lf",
        "blocks": blocks,
        "unmanaged": unmanaged,
        "legacy": legacy,
        "available": available,
        "problems": problems,
    }


def parse_sets(pairs):
    options = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise RulesError(f"--set needs key=value, not '{pair}'")
        key, value = pair.split("=", 1)
        options[key.strip()] = value
    return options


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("section")
    r.add_argument("--version")
    r.add_argument("--modules", default="")
    r.add_argument("--set", action="append", dest="sets")
    r.add_argument("--markers", action="store_true")
    s = sub.add_parser("status")
    s.add_argument("path")
    h = sub.add_parser("hash")
    h.add_argument("section")
    h.add_argument("version")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    try:
        catalog = load_catalog()
        if args.cmd == "render":
            modules = [m for m in args.modules.split(",") if m]
            sys.stdout.write(render(catalog, args.section, args.version, modules,
                                    parse_sets(args.sets), args.markers))
        elif args.cmd == "status":
            print(json.dumps(status(catalog, args.path), indent=2, ensure_ascii=False))
        elif args.cmd == "hash":
            print(template_hash(args.section, args.version))
    except (RulesError, OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
