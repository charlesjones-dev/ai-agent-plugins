#!/usr/bin/env python3
"""Check that the catalogs, plugin manifests and skill files agree.

Run from the repository root:

    python3 scripts/check-manifests.py

Checks:
- Each Claude Code catalog entry matches its plugin's .claude-plugin/plugin.json.
- Each root plugin.json (Agent Plugins 1.0) follows the spec's closed schema and
  matches the plugin's .claude-plugin/plugin.json.
- The Codex and Cursor catalogs list the same plugins, each with a root plugin.json.
- Each skill with `disable-model-invocation: true` has agents/openai.yaml that
  turns off implicit invocation in Codex, and no other skill does.
- Reference files shared between skills (SHARED_COPIES) are identical.
- Every row in ai-knowledge's command map has a known Kind, and every plugin command in
  its New column exists as a skill (built-in Claude Code commands are listed in BUILTINS).

Exits 1 and lists every problem when a check fails. Standard library only.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_CATALOG = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_CATALOG = ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_CATALOG = ROOT / ".cursor-plugin" / "marketplace.json"

AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGINS_KEYS = {"$schema", "name", "version", "description", "author", "homepage",
                      "repository", "license", "keywords", "extensions"}
AGENT_PLUGINS_NAME = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

# Fields that must match between a catalog entry or root plugin.json and .claude-plugin/plugin.json
CATALOG_FIELDS = ("name", "version", "description", "author", "keywords", "repository")
ROOT_MANIFEST_FIELDS = ("name", "version", "description", "author", "repository", "license", "keywords")

OPENAI_YAML = "policy:\n  allow_implicit_invocation: false\n"

# Reference files that more than one skill uses. A skill shouldn't link outside its own
# folder, so each skill keeps a copy, and the copies must stay identical.
SHARED_COPIES = [
    ("plugins/ai-slop/skills/slop-audit/signals.md", "plugins/ai-slop/skills/slop-rewrite/signals.md"),
    ("plugins/ai-seo/skills/seo-schema/references/json-ld.md",
     "plugins/ai-seo/skills/seo-fix/references/json-ld.md",
     "plugins/ai-seo/skills/seo-faq/references/json-ld.md"),
    ("plugins/ai-seo/skills/seo-audit/references/index-template.md",
     "plugins/ai-seo/skills/seo-questions/references/index-template.md"),
    tuple(f"plugins/ai-knowledge/skills/{s}/kb-format.md"
          for s in ("kb-init", "kb-migrate", "kb-add", "kb-learn", "kb-discover", "kb-query", "kb-prune")),
]

# /kb-migrate's map of renamed, merged and removed commands (Old | New | Kind | Notes)
COMMAND_MAP = ROOT / "plugins" / "ai-knowledge" / "skills" / "kb-migrate" / "command-map.md"
COMMAND_MAP_KINDS = {"rename", "changed", "removed"}
# Claude Code commands that can appear as replacements without being a skill in this repo
BUILTINS = {"init", "install-github-app", "code-review", "autofix-pr", "loop", "memory", "statusline",
            "security-review", "output-style", "config", "context", "review", "ultrareview", "goal",
            "plugin", "verify", "simplify"}

problems = []


def problem(msg):
    problems.append(msg)


def load(path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        problem(f"{path.relative_to(ROOT)}: missing")
    except json.JSONDecodeError as e:
        problem(f"{path.relative_to(ROOT)}: invalid JSON ({e})")
    return None


def frontmatter(skill_md):
    text = skill_md.read_text()
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) == 3 else ""


def check_root_manifest(name, root_manifest, claude_manifest):
    rel = f"plugins/{name}/plugin.json"
    extra = set(root_manifest) - AGENT_PLUGINS_KEYS
    if extra:
        problem(f"{rel}: fields outside the Agent Plugins schema: {sorted(extra)}")
    if root_manifest.get("$schema") != AGENT_PLUGINS_SCHEMA:
        problem(f"{rel}: $schema must be {AGENT_PLUGINS_SCHEMA}")
    if not AGENT_PLUGINS_NAME.match(str(root_manifest.get("name", ""))) or len(root_manifest.get("name", "")) > 64:
        problem(f"{rel}: name breaks the Agent Plugins name rules")
    author = root_manifest.get("author", {})
    if not isinstance(author, dict) or set(author) - {"name", "email", "url"} or \
            not all(isinstance(v, str) for v in author.values()):
        problem(f"{rel}: author may hold only name, email and url strings")
    for field in ROOT_MANIFEST_FIELDS:
        if root_manifest.get(field) != claude_manifest.get(field):
            problem(f"{rel}: {field} differs from .claude-plugin/plugin.json")


def check_command_map():
    rel = COMMAND_MAP.relative_to(ROOT)
    if not COMMAND_MAP.exists():
        problem(f"{rel}: missing")
        return
    skills = {}
    for skill_md in ROOT.glob("plugins/*/skills/*/SKILL.md"):
        skills.setdefault(skill_md.parent.name, set()).add(skill_md.parent.parent.parent.name)
    rows = 0
    for n, line in enumerate(COMMAND_MAP.read_text().splitlines(), 1):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|") or len(cells) < 4 or cells[0] == "Old" or set(cells[0]) <= set("-: "):
            continue
        rows += 1
        old, new, kind = cells[0], cells[1], cells[2].strip("`").lower()
        if kind not in COMMAND_MAP_KINDS:
            problem(f"{rel}:{n}: Kind must be one of {sorted(COMMAND_MAP_KINDS)}, not '{cells[2]}'")
        for code in re.findall(r"`([^`]+)`", new):
            token = code.split()[0]
            m = re.match(r"^[/$](?:([a-z0-9-]+):)?([a-z0-9-]+)$", token)
            if not m:
                continue
            plugin, name = m.groups()
            if name in BUILTINS and not plugin:
                continue
            if name not in skills or (plugin and plugin not in skills[name]):
                problem(f"{rel}:{n}: {token} in the New column isn't a skill in this repo "
                        "(add it to BUILTINS if it's a built-in Claude Code command)")
    if rows == 0:
        problem(f"{rel}: no table rows found (expected Old | New | Kind | Notes)")


def main():
    claude = load(CLAUDE_CATALOG)
    codex = load(CODEX_CATALOG)
    cursor = load(CURSOR_CATALOG)
    if claude is None:
        return

    manifests = {}
    for entry in claude.get("plugins", []):
        name = entry["name"]
        manifest = load(ROOT / "plugins" / name / ".claude-plugin" / "plugin.json")
        if manifest is None:
            continue
        manifests[name] = manifest
        for field in CATALOG_FIELDS:
            if entry.get(field) != manifest.get(field):
                problem(f".claude-plugin/marketplace.json: {name} {field} differs from its plugin.json")
        root_path = ROOT / "plugins" / name / "plugin.json"
        if root_path.exists():
            root_manifest = load(root_path)
            if root_manifest is not None:
                check_root_manifest(name, root_manifest, manifest)

    portable = {n for n in manifests if (ROOT / "plugins" / n / "plugin.json").exists()}
    version = claude.get("metadata", {}).get("version")

    if codex is not None:
        if codex.get("name") != claude.get("name"):
            problem(".agents/plugins/marketplace.json: name differs from the Claude Code catalog")
        listed = set()
        for entry in codex.get("plugins", []):
            name = entry.get("name")
            listed.add(name)
            if entry.get("source") != {"source": "local", "path": f"./plugins/{name}"}:
                problem(f".agents/plugins/marketplace.json: {name} source must be ./plugins/{name}")
            policy = entry.get("policy", {})
            if "installation" not in policy or "authentication" not in policy or "category" not in entry:
                problem(f".agents/plugins/marketplace.json: {name} needs policy.installation, "
                        "policy.authentication and category")
        if listed != portable:
            problem(f".agents/plugins/marketplace.json: lists {sorted(listed)}, but the plugins with "
                    f"a root plugin.json are {sorted(portable)}")

    if cursor is not None:
        if cursor.get("name") != claude.get("name"):
            problem(".cursor-plugin/marketplace.json: name differs from the Claude Code catalog")
        if cursor.get("metadata", {}).get("version") != version:
            problem(".cursor-plugin/marketplace.json: metadata.version differs from the Claude Code catalog")
        listed = set()
        for entry in cursor.get("plugins", []):
            name = entry.get("name")
            listed.add(name)
            if entry.get("source") != f"plugins/{name}":
                problem(f".cursor-plugin/marketplace.json: {name} source must be plugins/{name}")
            for field in ("version", "description"):
                if name in manifests and entry.get(field) != manifests[name].get(field):
                    problem(f".cursor-plugin/marketplace.json: {name} {field} differs from its plugin.json")
        if listed != portable:
            problem(f".cursor-plugin/marketplace.json: lists {sorted(listed)}, but the plugins with "
                    f"a root plugin.json are {sorted(portable)}")

    for skill_md in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        rel = skill_md.relative_to(ROOT)
        fm = frontmatter(skill_md)
        name = re.search(r"^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.M)
        if not name or name.group(1) != skill_md.parent.name or not SKILL_NAME.match(name.group(1)):
            problem(f"{rel}: name must match the folder name and use lowercase letters, digits and hyphens")
        manual_only = re.search(r"^disable-model-invocation:\s*true\s*$", fm, re.M) is not None
        openai_yaml = skill_md.parent / "agents" / "openai.yaml"
        has_policy = openai_yaml.exists() and openai_yaml.read_text() == OPENAI_YAML
        if manual_only and not has_policy:
            problem(f"{rel}: disable-model-invocation is true, so agents/openai.yaml must contain:\n"
                    + "    " + OPENAI_YAML.replace("\n", "\n    ").rstrip())
        if not manual_only and openai_yaml.exists():
            problem(f"{rel}: Claude can invoke this skill, so remove agents/openai.yaml or set "
                    "disable-model-invocation: true")

    for copies in SHARED_COPIES:
        texts = []
        for rel in copies:
            path = ROOT / rel
            if not path.exists():
                problem(f"{rel}: missing shared copy")
            else:
                texts.append(path.read_text())
        if len(texts) == len(copies) and len(set(texts)) > 1:
            problem(f"{' and '.join(copies)} must be identical; edit both copies")

    check_command_map()

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"- {p}")
        sys.exit(1)
    skills = len(list(ROOT.glob("plugins/*/skills/*/SKILL.md")))
    print(f"OK: {len(manifests)} plugins ({len(portable)} with Agent Plugins manifests), {skills} skills")


if __name__ == "__main__":
    main()
